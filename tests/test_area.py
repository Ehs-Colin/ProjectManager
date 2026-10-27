# tests/test_areas.py
import pathlib
import unittest

import sqlalchemy

import internal.areas as areas

SCHEMA = (
    pathlib.Path(__file__).resolve().parents[1] / "sql" / "schema" / "0001_projects.sql"
)


def _apply_schema(conn: sqlalchemy.engine.Connection) -> None:
    up = SCHEMA.read_text().split("-- +goose Down")[0]
    for stmt in up.split(";"):
        if stmt.strip():
            conn.exec_driver_sql(stmt)


class AreasTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = sqlalchemy.create_engine("sqlite://")
        self.conn = self.engine.connect()
        _apply_schema(self.conn)

    def tearDown(self):
        self.conn.close()
        self.engine.dispose()

    def _create(self, name="Kitchen", description="Main floor"):
        return areas.create_area(self.conn, [name, description])


class TestHomeArea(unittest.TestCase):
    def test_defaults(self):
        a = areas.HomeArea()
        self.assertEqual(a.name, a.id)
        self.assertEqual(a.description, "")
        self.assertIsNotNone(a.create_at)
        self.assertIsNotNone(a.update_at)

    def test_custom_values(self):
        a = areas.HomeArea(name="Garage", description="Detached")
        self.assertEqual(a.name, "Garage")
        self.assertEqual(a.description, "Detached")

    def test_unique_ids(self):
        self.assertNotEqual(areas.HomeArea().id, areas.HomeArea().id)

    def test_str_includes_name_and_id(self):
        a = areas.HomeArea(name="Garage")
        r = str(a)
        self.assertIn("AREA: Garage", r)
        self.assertIn(a.id, r)


class TestCreateArea(AreasTestCase):
    def test_creates_row(self):
        self._create("Kitchen", "Main floor")
        a = areas.get_area(self.conn, "Kitchen")
        self.assertIsNotNone(a)
        self.assertEqual(a.description, "Main floor")

    def test_returns_stored_area(self):
        created = self._create("Kitchen", "Main floor")
        a = areas.get_area(self.conn, "Kitchen")
        self.assertIsInstance(created, areas.HomeArea)
        self.assertEqual(created.id, a.id)
        self.assertEqual(created.name, "Kitchen")
        self.assertEqual(created.description, "Main floor")
        self.assertIsNotNone(created.create_at)
        self.assertIsNotNone(created.update_at)

    def test_wrong_arg_count(self):
        for args in ([], ["only-name"], ["a", "b", "c"]):
            with self.assertRaises(TypeError):
                areas.create_area(self.conn, args)

    def test_duplicate_name_rejected(self):
        self._create("Kitchen")
        with self.assertRaises(sqlalchemy.exc.IntegrityError):
            self._create("Kitchen")


class TestGetArea(AreasTestCase):
    def test_by_name_and_id(self):
        self._create("Kitchen")
        by_name = areas.get_area(self.conn, "Kitchen")
        by_id = areas.get_area(self.conn, by_name.id)
        self.assertIsInstance(by_name, areas.HomeArea)
        self.assertEqual(by_id.name, "Kitchen")
        self.assertIsNotNone(by_id.create_at)
        self.assertIsNotNone(by_id.update_at)

    def test_missing_returns_none(self):
        self.assertIsNone(areas.get_area(self.conn, "nope"))


class TestListAreas(AreasTestCase):
    def test_empty(self):
        self.assertEqual(areas.list_areas(self.conn), [])

    def test_lists_all(self):
        self._create("Kitchen")
        self._create("Garage")
        names = {a.name for a in areas.list_areas(self.conn)}
        self.assertEqual(names, {"Kitchen", "Garage"})


class TestDeleteArea(AreasTestCase):
    def test_deletes(self):
        self._create("Kitchen")
        a = areas.get_area(self.conn, "Kitchen")
        self.assertTrue(areas.delete_area(self.conn, a.id))
        self.assertIsNone(areas.get_area(self.conn, "Kitchen"))

    def test_delete_missing_is_noop(self):
        self.assertTrue(areas.delete_area(self.conn, "does-not-exist"))


class TestUpdateArea(AreasTestCase):
    def test_updates_description(self):
        self._create("Kitchen", "Main floor")
        msg = areas.update_area(self.conn, "Kitchen", ["description=Upstairs"])
        self.assertEqual(msg, "Updated area with name Kitchen (description)")
        a = areas.get_area(self.conn, "Kitchen")
        self.assertEqual(a.description, "Upstairs")
        self.assertEqual(a.name, "Kitchen")  # untouched field preserved

    def test_updates_multiple_fields(self):
        self._create("Kitchen", "Main floor")
        msg = areas.update_area(
            self.conn, "Kitchen", ["name=Galley", "description=Narrow"]
        )
        self.assertEqual(msg, "Updated area with name Kitchen (name, description)")
        a = areas.get_area(self.conn, "Galley")
        self.assertEqual(a.description, "Narrow")

    def test_rename(self):
        self._create("Kitchen")
        areas.update_area(self.conn, "Kitchen", ["name=Galley"])
        self.assertIsNone(areas.get_area(self.conn, "Kitchen"))
        self.assertIsNotNone(areas.get_area(self.conn, "Galley"))

    def test_value_may_contain_equals(self):
        self._create("Kitchen")
        areas.update_area(self.conn, "Kitchen", ["description=a=b"])
        self.assertEqual(areas.get_area(self.conn, "Kitchen").description, "a=b")

    def test_by_id(self):
        self._create("Kitchen")
        area_id = areas.get_area(self.conn, "Kitchen").id
        msg = areas.update_area(self.conn, area_id, ["description=a=b"])
        self.assertEqual(msg, "Updated area with name Kitchen (description)")
        self.assertEqual(areas.get_area(self.conn, "Kitchen").description, "a=b")

    def test_no_args(self):
        with self.assertRaises(TypeError):
            areas.update_area(self.conn, "Kitchen", [])

    def test_bad_args(self):
        self._create("Kitchen")
        for arg in ("description", "color=red", "budget=1"):
            with self.assertRaises(ValueError, msg=arg):
                areas.update_area(self.conn, "Kitchen", [arg])

    def test_missing_area(self):
        with self.assertRaises(ValueError):
            areas.update_area(self.conn, "nope", ["description=x"])


if __name__ == "__main__":
    unittest.main()
