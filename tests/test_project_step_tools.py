# tests/test_project_step_tools.py
import pathlib
import unittest

import sqlalchemy

import internal.project_step_tools as project_step_tools
import internal.projects as projects
import internal.projectsteps as projectsteps
import internal.tools as tools

SCHEMA = (
    pathlib.Path(__file__).resolve().parents[1] / "sql" / "schema" / "0001_projects.sql"
)


def _apply_schema(conn: sqlalchemy.engine.Connection) -> None:
    up = SCHEMA.read_text().split("-- +goose Down")[0]
    for stmt in up.split(";"):
        if stmt.strip():
            conn.exec_driver_sql(stmt)


class ProjectStepToolsTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = sqlalchemy.create_engine("sqlite://")
        self.conn = self.engine.connect()
        _apply_schema(self.conn)
        self.project_id = projects.create_project(self.conn, ["Kitchen", "Remodel"]).id
        self.other_id = projects.create_project(self.conn, ["Garden", "Beds"]).id
        self.step_id = projectsteps.create_projectstep(
            self.conn, [self.project_id, "Demo", "Tear out"]
        ).id
        projectsteps.create_projectstep(self.conn, [self.project_id, "Paint", "Walls"])
        projectsteps.create_projectstep(self.conn, [self.other_id, "Dig", "Holes"])
        self.tool_id = tools.create_tool(self.conn, ["Hammer", "Claw"]).id
        tools.create_tool(self.conn, ["Saw", "Circular"])

    def tearDown(self):
        self.conn.close()
        self.engine.dispose()


class TestHomeProjectStepTool(unittest.TestCase):
    def test_str(self):
        pst = project_step_tools.HomeProjectStepTool("p", "s", "t")
        self.assertIn("project p / step s / tool t", str(pst))


class TestCreateProjectStepTool(ProjectStepToolsTestCase):
    def test_by_names(self):
        pst = project_step_tools.create_project_step_tool(
            self.conn, ["Kitchen", "Demo", "Hammer"]
        )
        self.assertIsInstance(pst, project_step_tools.HomeProjectStepTool)
        self.assertEqual(pst.project_id, self.project_id)
        self.assertEqual(pst.step_id, self.step_id)
        self.assertEqual(pst.tool_id, self.tool_id)

    def test_by_ids(self):
        pst = project_step_tools.create_project_step_tool(
            self.conn, [self.project_id, self.step_id, self.tool_id]
        )
        self.assertEqual(pst.step_id, self.step_id)

    def test_duplicate(self):
        args = ["Kitchen", "Demo", "Hammer"]
        project_step_tools.create_project_step_tool(self.conn, args)
        msg = project_step_tools.create_project_step_tool(self.conn, args)
        self.assertIsInstance(msg, str)
        self.assertIn("already linked", msg)

    def test_wrong_arg_count(self):
        for args in ([], ["Kitchen", "Demo"], ["a", "b", "c", "d"]):
            with self.assertRaises(TypeError, msg=args):
                project_step_tools.create_project_step_tool(self.conn, args)

    def test_step_not_in_project(self):
        with self.assertRaises(ValueError):
            project_step_tools.create_project_step_tool(
                self.conn, ["Kitchen", "Dig", "Hammer"]
            )
        with self.assertRaises(ValueError):
            project_step_tools.create_project_step_tool(
                self.conn, ["Garden", self.step_id, "Hammer"]
            )

    def test_missing_entities(self):
        for args in (
            ["nope", "Demo", "Hammer"],
            ["Kitchen", "nope", "Hammer"],
            ["Kitchen", "Demo", "nope"],
        ):
            with self.assertRaises(ValueError, msg=args):
                project_step_tools.create_project_step_tool(self.conn, args)


class TestGetProjectStepTool(ProjectStepToolsTestCase):
    def test_found(self):
        project_step_tools.create_project_step_tool(
            self.conn, ["Kitchen", "Demo", "Hammer"]
        )
        pst = project_step_tools.get_project_step_tool(
            self.conn, self.project_id, "Demo", self.tool_id
        )
        self.assertEqual(pst.tool_id, self.tool_id)

    def test_not_linked_returns_none(self):
        self.assertIsNone(
            project_step_tools.get_project_step_tool(
                self.conn, "Kitchen", "Demo", "Hammer"
            )
        )


class TestListProjectStepTools(ProjectStepToolsTestCase):
    def setUp(self):
        super().setUp()
        for step, tool in (("Demo", "Hammer"), ("Demo", "Saw"), ("Paint", "Saw")):
            project_step_tools.create_project_step_tool(
                self.conn, ["Kitchen", step, tool]
            )

    def test_by_project(self):
        self.assertEqual(
            len(project_step_tools.list_project_step_tools(self.conn, "Kitchen")), 3
        )
        self.assertEqual(
            project_step_tools.list_project_step_tools(self.conn, "Garden"), []
        )

    def test_by_project_and_step(self):
        rows = project_step_tools.list_project_step_tools(self.conn, "Kitchen", "Demo")
        self.assertEqual(len(rows), 2)
        self.assertTrue(all(r.step_id == self.step_id for r in rows))

    def test_missing_project(self):
        with self.assertRaises(ValueError):
            project_step_tools.list_project_step_tools(self.conn, "nope")


class TestDeleteProjectStepTool(ProjectStepToolsTestCase):
    def test_deletes_link(self):
        project_step_tools.create_project_step_tool(
            self.conn, ["Kitchen", "Demo", "Hammer"]
        )
        self.assertTrue(
            project_step_tools.delete_project_step_tool(
                self.conn, "Kitchen", "Demo", "Hammer"
            )
        )
        self.assertIsNone(
            project_step_tools.get_project_step_tool(
                self.conn, "Kitchen", "Demo", "Hammer"
            )
        )


if __name__ == "__main__":
    unittest.main()
