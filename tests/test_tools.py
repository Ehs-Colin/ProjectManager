# tests/test_tools.py
import pathlib
import unittest

import sqlalchemy

import internal.tools as tools

SCHEMA = (
    pathlib.Path(__file__).resolve().parents[1] / "sql" / "schema" / "0001_projects.sql"
)


def _apply_schema(conn: sqlalchemy.engine.Connection) -> None:
    up = SCHEMA.read_text().split("-- +goose Down")[0]
    for stmt in up.split(";"):
        if stmt.strip():
            conn.exec_driver_sql(stmt)


class ToolsTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = sqlalchemy.create_engine("sqlite://")
        self.conn = self.engine.connect()
        _apply_schema(self.conn)

    def tearDown(self):
        self.conn.close()
        self.engine.dispose()

    def _create(self, name="Hammer", description="Claw"):
        return tools.create_tool(self.conn, [name, description])


class TestHomeTool(unittest.TestCase):
    def test_defaults(self):
        t = tools.HomeTool()
        self.assertEqual(t.name, t.id)
        self.assertEqual(t.description, "")
        self.assertIsNotNone(t.create_at)
        self.assertIsNotNone(t.update_at)

    def test_custom_values(self):
        t = tools.HomeTool(name="Drill", description="Cordless")
        self.assertEqual(t.name, "Drill")
        self.assertEqual(t.description, "Cordless")

    def test_unique_ids(self):
        self.assertNotEqual(tools.HomeTool().id, tools.HomeTool().id)

    def test_repr_includes_name_and_id(self):
        t = tools.HomeTool(name="Drill")
        r = repr(t)
        self.assertIn("TOOL: Drill", r)
        self.assertIn(t.id, r)


class TestCreateTool(ToolsTestCase):
    def test_creates_row(self):
        self._create("Hammer", "Claw")
        t = tools.get_tool(self.conn, "Hammer")
        self.assertIsNotNone(t)
        self.assertEqual(t.description, "Claw")

    def test_message_reports_stored_name_and_id(self):
        msg = self._create("Hammer")
        t = tools.get_tool(self.conn, "Hammer")
        self.assertEqual(msg, f"Created tool 'Hammer' with id {t.id}")

    def test_wrong_arg_count(self):
        for args in ([], ["only-name"], ["a", "b", "c"]):
            with self.assertRaises(TypeError):
                tools.create_tool(self.conn, args)

    def test_duplicate_name_rejected(self):
        self._create("Hammer")
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            self._create("Hammer")


class TestGetTool(ToolsTestCase):
    def test_by_name_and_id(self):
        self._create("Hammer")
        by_name = tools.get_tool(self.conn, "Hammer")
        by_id = tools.get_tool(self.conn, by_name.id, by="id")
        self.assertIsInstance(by_name, tools.HomeTool)
        self.assertEqual(by_id.name, "Hammer")
        self.assertIsNotNone(by_id.create_at)
        self.assertIsNotNone(by_id.update_at)

    def test_missing_returns_none(self):
        self.assertIsNone(tools.get_tool(self.conn, "nope"))
        self.assertIsNone(tools.get_tool(self.conn, "nope", by="id"))

    def test_invalid_lookup_type(self):
        with self.assertRaises(ValueError):
            tools.get_tool(self.conn, "Hammer", by="description")


class TestListTools(ToolsTestCase):
    def test_empty(self):
        self.assertEqual(tools.list_tools(self.conn), [])

    def test_lists_all(self):
        self._create("Hammer")
        self._create("Drill")
        names = {t.name for t in tools.list_tools(self.conn)}
        self.assertEqual(names, {"Hammer", "Drill"})


class TestDeleteTool(ToolsTestCase):
    def test_deletes(self):
        self._create("Hammer")
        t = tools.get_tool(self.conn, "Hammer")
        self.assertTrue(tools.delete_tool(self.conn, t.id))
        self.assertIsNone(tools.get_tool(self.conn, "Hammer"))

    def test_delete_missing_is_noop(self):
        self.assertTrue(tools.delete_tool(self.conn, "does-not-exist"))


class TestUpdateTool(ToolsTestCase):
    def test_updates_description(self):
        self._create("Hammer", "Claw")
        msg = tools.update_tool(self.conn, "Hammer", ["description=Sledge"])
        self.assertEqual(msg, "Updated tool with name Hammer (description)")
        t = tools.get_tool(self.conn, "Hammer")
        self.assertEqual(t.description, "Sledge")
        self.assertEqual(t.name, "Hammer")  # untouched field preserved

    def test_updates_multiple_fields(self):
        self._create("Hammer", "Claw")
        msg = tools.update_tool(
            self.conn, "Hammer", ["name=Mallet", "description=Rubber"]
        )
        self.assertEqual(msg, "Updated tool with name Hammer (name, description)")
        t = tools.get_tool(self.conn, "Mallet")
        self.assertEqual(t.description, "Rubber")

    def test_rename(self):
        self._create("Hammer")
        tools.update_tool(self.conn, "Hammer", ["name=Mallet"])
        self.assertIsNone(tools.get_tool(self.conn, "Hammer"))
        self.assertIsNotNone(tools.get_tool(self.conn, "Mallet"))

    def test_value_may_contain_equals(self):
        self._create("Hammer")
        tools.update_tool(self.conn, "Hammer", ["description=a=b"])
        self.assertEqual(tools.get_tool(self.conn, "Hammer").description, "a=b")

    def test_no_args(self):
        with self.assertRaises(TypeError):
            tools.update_tool(self.conn, "Hammer", [])

    def test_bad_args(self):
        self._create("Hammer")
        for arg in ("description", "color=red", "budget=1"):
            with self.assertRaises(ValueError, msg=arg):
                tools.update_tool(self.conn, "Hammer", [arg])

    def test_missing_tool(self):
        with self.assertRaises(ValueError):
            tools.update_tool(self.conn, "nope", ["description=x"])


if __name__ == "__main__":
    unittest.main()
