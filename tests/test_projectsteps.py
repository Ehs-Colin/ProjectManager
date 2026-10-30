# tests/test_projectsteps.py
import pathlib
import unittest

import sqlalchemy

import internal.projects as projects
import internal.projectsteps as projectsteps

SCHEMA = (
    pathlib.Path(__file__).resolve().parents[1] / "sql" / "schema" / "0001_projects.sql"
)


def _apply_schema(conn: sqlalchemy.engine.Connection) -> None:
    up = SCHEMA.read_text().split("-- +goose Down")[0]
    for stmt in up.split(";"):
        if stmt.strip():
            conn.exec_driver_sql(stmt)


class ProjectStepsTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = sqlalchemy.create_engine("sqlite://")
        self.conn = self.engine.connect()
        _apply_schema(self.conn)
        projects.create_project(self.conn, ["Kitchen", "Remodel"])
        self.project_id = projects.get_project(self.conn, "Kitchen").id

    def tearDown(self):
        self.conn.close()
        self.engine.dispose()

    def _create(self, name="Demo", description="Tear out cabinets"):
        return projectsteps.create_projectstep(
            self.conn, [self.project_id, name, description]
        )

    def _get(self, name="Demo"):
        return projectsteps.get_projectstep(self.conn, self.project_id, name)


class TestHomeProjectStep(unittest.TestCase):
    def test_defaults(self):
        s = projectsteps.HomeProjectStep()
        self.assertEqual(s.name, s.id)
        self.assertEqual(s.project_id, "")
        self.assertEqual(s.description, "")
        self.assertEqual(s.completion_percent, 0.0)
        self.assertEqual(s.order_id, 0)
        self.assertEqual(s.performstepvalue, 0)
        self.assertEqual(s.projectvalue, 0)
        self.assertIsNotNone(s.create_at)
        self.assertIsNotNone(s.update_at)

    def test_custom_values(self):
        s = projectsteps.HomeProjectStep(
            project_id="p1", name="Paint", description="Walls", order_id=2
        )
        self.assertEqual(s.project_id, "p1")
        self.assertEqual(s.name, "Paint")
        self.assertEqual(s.description, "Walls")
        self.assertEqual(s.order_id, 2)

    def test_unique_ids(self):
        self.assertNotEqual(
            projectsteps.HomeProjectStep().id, projectsteps.HomeProjectStep().id
        )

    def test_convert_from_sql(self):
        src = projectsteps.HomeProjectStep(project_id="p1", name="Paint")
        dst = projectsteps.HomeProjectStep()
        dst.ConvertFromSql(src)
        self.assertEqual(dst.id, src.id)
        self.assertEqual(dst.project_id, "p1")
        self.assertEqual(dst.name, "Paint")
        self.assertEqual(dst.create_at, src.create_at)

    def test_str_includes_name_and_id(self):
        s = projectsteps.HomeProjectStep(name="Paint")
        r = str(s)
        self.assertIn("PROJECT STEP: Paint", r)
        self.assertIn(s.id, r)


class TestCreateProjectStep(ProjectStepsTestCase):
    def test_creates_row(self):
        created = self._create("Demo", "Tear out cabinets")
        self.assertIsInstance(created, projectsteps.HomeProjectStep)
        self.assertEqual(created.name, "Demo")
        self.assertEqual(created.project_id, self.project_id)
        step = self._get("Demo")
        self.assertIsNotNone(step)
        self.assertEqual(created.id, step.id)
        self.assertEqual(step.project_id, self.project_id)
        self.assertEqual(step.description, "Tear out cabinets")

    def test_wrong_arg_count(self):
        with self.assertRaises(TypeError):
            projectsteps.create_projectstep(self.conn, [self.project_id, "Demo"])

    def test_unknown_project(self):
        with self.assertRaises(ValueError):
            projectsteps.create_projectstep(self.conn, ["missing", "Demo", ""])


class TestListProjectSteps(ProjectStepsTestCase):
    def test_empty(self):
        self.assertEqual(projectsteps.list_projectsteps(self.conn, self.project_id), [])

    def test_lists_only_project_steps(self):
        self._create("A", "")
        self._create("B", "")
        projects.create_project(self.conn, ["Other", ""])
        other_id = projects.get_project(self.conn, "Other").id
        projectsteps.create_projectstep(self.conn, [other_id, "C", ""])

        steps = projectsteps.list_projectsteps(self.conn, self.project_id)
        self.assertEqual(
            [s.id for s in projectsteps.list_projectsteps(self.conn, "Kitchen")],
            [s.id for s in steps],
        )
        self.assertEqual(sorted(s.name for s in steps), ["A", "B"])
        for s in steps:
            self.assertIsInstance(s, projectsteps.HomeProjectStep)


class TestGetProjectStep(ProjectStepsTestCase):
    def test_by_name(self):
        self._create()
        self.assertEqual(self._get("Demo").name, "Demo")

    def test_by_id(self):
        self._create()
        step_id = self._get().id
        step = projectsteps.get_projectstep(self.conn, self.project_id, step_id)
        self.assertEqual(step.name, "Demo")

    def test_missing_returns_none(self):
        self.assertIsNone(self._get("nope"))

    def test_by_project_name(self):
        self._create()
        step = projectsteps.get_projectstep(self.conn, "Kitchen", "Demo")
        self.assertEqual(step.project_id, self.project_id)

    def test_by_project_name_and_step_id(self):
        self._create()
        step_id = self._get().id
        step = projectsteps.get_projectstep(self.conn, "Kitchen", step_id)
        self.assertEqual(step.name, "Demo")

    def test_missing_project_returns_none(self):
        self._create()
        self.assertIsNone(projectsteps.get_projectstep(self.conn, "nope", "Demo"))

    def test_step_from_other_project_returns_none(self):
        self._create()
        step_id = self._get().id
        projects.create_project(self.conn, ["Other", "x"])
        self.assertIsNone(projectsteps.get_projectstep(self.conn, "Other", step_id))
        self.assertIsNone(projectsteps.get_projectstep(self.conn, "Other", "Demo"))


class TestDeleteProjectStep(ProjectStepsTestCase):
    def test_deletes_row(self):
        self._create()
        self.assertTrue(projectsteps.delete_projectstep(self.conn, self._get().id))
        self.assertIsNone(self._get())


class TestUpdateProjectStep(ProjectStepsTestCase):
    def _update(self, *args, name="Demo"):
        return projectsteps.update_projectstep(
            self.conn, self.project_id, name, list(args)
        )

    def test_updates_fields(self):
        self._create()
        msg = self._update(
            "description=New",
            "completion_percent=50.5",
            "order_id=3",
            "performstepvalue=7",
            "projectvalue=9",
        )
        self.assertIn("Updated project step with name Demo", msg)
        step = self._get()
        self.assertEqual(step.description, "New")
        self.assertEqual(step.completion_percent, 50.5)
        self.assertEqual(step.order_id, 3)
        self.assertEqual(step.performstepvalue, 7)
        self.assertEqual(step.projectvalue, 9)

    def test_rename(self):
        self._create()
        self._update("name=Renamed")
        self.assertIsNone(self._get("Demo"))
        self.assertIsNotNone(self._get("Renamed"))

    def test_preserves_untouched_fields(self):
        self._create("Demo", "Keep me")
        self._update("order_id=1")
        self.assertEqual(self._get().description, "Keep me")

    def test_no_args(self):
        with self.assertRaises(TypeError):
            self._update()

    def test_missing_separator(self):
        self._create()
        with self.assertRaises(ValueError):
            self._update("description")

    def test_unknown_field(self):
        self._create()
        with self.assertRaises(ValueError):
            self._update("project_id=other")

    def test_bad_value_type(self):
        self._create()
        with self.assertRaises(ValueError):
            self._update("order_id=abc")

    def test_by_project_name(self):
        self._create()
        projectsteps.update_projectstep(self.conn, "Kitchen", "Demo", ["order_id=4"])
        self.assertEqual(self._get().order_id, 4)

    def test_by_step_id(self):
        self._create()
        step_id = self._get().id
        msg = projectsteps.update_projectstep(
            self.conn, self.project_id, step_id, ["order_id=5"]
        )
        self.assertEqual(msg, "Updated project step with name Demo (order_id)")
        self.assertEqual(self._get().order_id, 5)

    def test_missing_project(self):
        self._create()
        with self.assertRaises(ValueError):
            projectsteps.update_projectstep(self.conn, "nope", "Demo", ["order_id=4"])

    def test_missing_step(self):
        with self.assertRaises(ValueError):
            self._update("description=x", name="nope")


class TestAdvanceStep(ProjectStepsTestCase):
    def _set(self, name, *fields):
        projectsteps.update_projectstep(self.conn, self.project_id, name, list(fields))

    def _project_percent(self):
        return projects.get_project(self.conn, "Kitchen").completion_percent

    def test_advances_by_one(self):
        self._create()
        msg = projectsteps.advancestep(self.conn, self.project_id, "Demo")
        self.assertEqual(self._get().completion_percent, 1.0)
        self.assertIn("Advanced project step Demo to 1.0%", msg)

    def test_repeated_advances_accumulate(self):
        self._create()
        for _ in range(3):
            projectsteps.advancestep(self.conn, self.project_id, "Demo")
        self.assertEqual(self._get().completion_percent, 3.0)

    def test_caps_at_100(self):
        self._create()
        self._set("Demo", "completion_percent=99.5")
        projectsteps.advancestep(self.conn, self.project_id, "Demo")
        self.assertEqual(self._get().completion_percent, 100.0)

    def test_already_complete_is_noop(self):
        self._create()
        self._set("Demo", "completion_percent=100", "projectvalue=50")
        msg = projectsteps.advancestep(self.conn, self.project_id, "Demo")
        self.assertIn("already 100% complete", msg)
        self.assertEqual(self._get().completion_percent, 100.0)
        self.assertEqual(self._project_percent(), 0.0)

    def test_updates_project_percent_by_step_value(self):
        self._create()
        self._set("Demo", "projectvalue=50")
        msg = projectsteps.advancestep(self.conn, self.project_id, "Demo")
        self.assertEqual(self._project_percent(), 0.5)
        self.assertIn("project now 0.5%", msg)

    def test_project_percent_sums_all_steps(self):
        self._create("A", "")
        self._create("B", "")
        self._set("A", "projectvalue=40", "completion_percent=100")
        self._set("B", "projectvalue=60", "completion_percent=49")
        projectsteps.advancestep(self.conn, self.project_id, "B")
        self.assertEqual(self._project_percent(), 70.0)

    def test_zero_projectvalue_leaves_project_unchanged(self):
        self._create()
        projectsteps.advancestep(self.conn, self.project_id, "Demo")
        self.assertEqual(self._project_percent(), 0.0)

    def test_by_project_name_and_step_id(self):
        self._create()
        step_id = self._get().id
        projectsteps.advancestep(self.conn, "Kitchen", step_id)
        self.assertEqual(self._get().completion_percent, 1.0)

    def test_missing_step(self):
        with self.assertRaises(ValueError):
            projectsteps.advancestep(self.conn, self.project_id, "nope")

    def test_missing_project(self):
        self._create()
        with self.assertRaises(ValueError):
            projectsteps.advancestep(self.conn, "nope", "Demo")


if __name__ == "__main__":
    unittest.main()
