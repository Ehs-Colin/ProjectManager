# tests/test_projects.py
import pathlib
import unittest

import sqlalchemy

import internal.projects as projects

SCHEMA = (
    pathlib.Path(__file__).resolve().parents[1] / "sql" / "schema" / "0001_projects.sql"
)


def _apply_schema(conn: sqlalchemy.engine.Connection) -> None:
    up = SCHEMA.read_text().split("-- +goose Down")[0]
    for stmt in up.split(";"):
        if stmt.strip():
            conn.exec_driver_sql(stmt)


class ProjectsTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = sqlalchemy.create_engine("sqlite://")
        self.conn = self.engine.connect()
        _apply_schema(self.conn)

    def tearDown(self):
        self.conn.close()
        self.engine.dispose()

    def _create(self, name="Kitchen", description="Remodel"):
        return projects.create_project(self.conn, [name, description])


class TestHomeProject(unittest.TestCase):
    def test_defaults(self):
        p = projects.HomeProject()
        self.assertEqual(p.name, p.id)
        self.assertEqual(p.description, "")
        self.assertEqual(p.budget, 0)
        self.assertEqual(p.completion_percent, 0.0)
        self.assertTrue(p.active)
        self.assertFalse(p.complete)

    def test_custom_values(self):
        p = projects.HomeProject(name="Deck", description="Build", budget=500)
        self.assertEqual(p.name, "Deck")
        self.assertEqual(p.description, "Build")
        self.assertEqual(p.budget, 500)

    def test_unique_ids(self):
        self.assertNotEqual(projects.HomeProject().id, projects.HomeProject().id)


class TestParseBool(unittest.TestCase):
    def test_truthy(self):
        for v in ("true", "TRUE", " 1 ", "yes", "y"):
            self.assertTrue(projects._parse_bool(v), v)

    def test_falsy(self):
        for v in ("false", "0", "No", "n"):
            self.assertFalse(projects._parse_bool(v), v)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            projects._parse_bool("maybe")


class TestCreateProject(ProjectsTestCase):
    def test_creates_row(self):
        self._create("Kitchen", "Remodel")
        p = projects.get_project(self.conn, "Kitchen")
        self.assertIsNotNone(p)
        self.assertEqual(p.description, "Remodel")
        self.assertEqual(p.budget, 0)
        self.assertTrue(p.active)
        self.assertFalse(p.complete)

    def test_returns_stored_project(self):
        created = self._create("Kitchen", "Remodel")
        p = projects.get_project(self.conn, "Kitchen")
        self.assertIsInstance(created, projects.HomeProject)
        self.assertEqual(created.id, p.id)
        self.assertEqual(created.name, "Kitchen")
        self.assertEqual(created.description, "Remodel")
        self.assertIsNotNone(created.create_at)
        self.assertIsNotNone(created.update_at)

    def test_wrong_arg_count(self):
        for args in ([], ["only-name"], ["a", "b", "c"]):
            with self.assertRaises(TypeError):
                projects.create_project(self.conn, args)

    def test_duplicate_name_rejected(self):
        self._create("Kitchen")
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            self._create("Kitchen")


class TestGetProject(ProjectsTestCase):
    def test_by_name_and_id(self):
        self._create("Kitchen")
        by_name = projects.get_project(self.conn, "Kitchen")
        by_id = projects.get_project(self.conn, by_name.id, by="id")
        self.assertIsInstance(by_name, projects.HomeProject)
        self.assertEqual(by_id.name, "Kitchen")
        self.assertIsNotNone(by_id.create_at)
        self.assertIsNotNone(by_id.update_at)

    def test_missing_returns_none(self):
        self.assertIsNone(projects.get_project(self.conn, "nope"))
        self.assertIsNone(projects.get_project(self.conn, "nope", by="id"))

    def test_invalid_lookup_type(self):
        with self.assertRaises(ValueError):
            projects.get_project(self.conn, "Kitchen", by="budget")


class TestListProjects(ProjectsTestCase):
    def test_empty(self):
        self.assertEqual(projects.list_projects(self.conn), [])

    def test_lists_all(self):
        self._create("Kitchen")
        self._create("Deck")
        names = {p.name for p in projects.list_projects(self.conn)}
        self.assertEqual(names, {"Kitchen", "Deck"})


class TestDeleteProject(ProjectsTestCase):
    def test_deletes(self):
        self._create("Kitchen")
        p = projects.get_project(self.conn, "Kitchen")
        self.assertTrue(projects.delete_project(self.conn, p.id))
        self.assertIsNone(projects.get_project(self.conn, "Kitchen"))

    def test_delete_missing_is_noop(self):
        self.assertTrue(projects.delete_project(self.conn, "does-not-exist"))


class TestUpdateProject(ProjectsTestCase):
    def test_updates_fields(self):
        self._create("Kitchen", "Remodel")
        msg = projects.update_project(
            self.conn,
            "Kitchen",
            ["budget=1500", "completion_percent=42.5", "active=no", "complete=yes"],
        )
        self.assertEqual(
            msg,
            "Updated project with name Kitchen (budget, completion_percent, active, complete)",
        )
        p = projects.get_project(self.conn, "Kitchen")
        self.assertEqual(p.budget, 1500)
        self.assertEqual(p.completion_percent, 42.5)
        self.assertFalse(p.active)
        self.assertTrue(p.complete)
        self.assertEqual(p.description, "Remodel")  # untouched fields preserved

    def test_rename(self):
        self._create("Kitchen")
        projects.update_project(self.conn, "Kitchen", ["name=Galley"])
        self.assertIsNone(projects.get_project(self.conn, "Kitchen"))
        self.assertIsNotNone(projects.get_project(self.conn, "Galley"))

    def test_value_may_contain_equals(self):
        self._create("Kitchen")
        projects.update_project(self.conn, "Kitchen", ["description=a=b"])
        self.assertEqual(projects.get_project(self.conn, "Kitchen").description, "a=b")

    def test_no_args(self):
        with self.assertRaises(TypeError):
            projects.update_project(self.conn, "Kitchen", [])

    def test_bad_args(self):
        self._create("Kitchen")
        for arg in ("budget", "color=red", "budget=lots", "active=maybe"):
            with self.assertRaises(ValueError, msg=arg):
                projects.update_project(self.conn, "Kitchen", [arg])

    def test_missing_project(self):
        with self.assertRaises(ValueError):
            projects.update_project(self.conn, "nope", ["budget=1"])


if __name__ == "__main__":
    unittest.main()
