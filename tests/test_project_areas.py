# tests/test_project_areas.py
import pathlib
import unittest

import sqlalchemy

import internal.areas as areas
import internal.project_areas as project_areas
import internal.projects as projects

SCHEMA = (
    pathlib.Path(__file__).resolve().parents[1] / "sql" / "schema" / "0001_projects.sql"
)


def _apply_schema(conn: sqlalchemy.engine.Connection) -> None:
    up = SCHEMA.read_text().split("-- +goose Down")[0]
    for stmt in up.split(";"):
        if stmt.strip():
            conn.exec_driver_sql(stmt)


class ProjectAreasTestCase(unittest.TestCase):
    def setUp(self):
        self.engine = sqlalchemy.create_engine("sqlite://")
        self.conn = self.engine.connect()
        _apply_schema(self.conn)
        projects.create_project(self.conn, ["Remodel", "Kitchen remodel"])
        projects.create_project(self.conn, ["Paint", "Repaint walls"])
        areas.create_area(self.conn, ["Kitchen", "Main floor"])
        areas.create_area(self.conn, ["Garage", "Detached"])
        self.project_id = projects.get_project(self.conn, "Remodel").id
        self.area_id = areas.get_area(self.conn, "Kitchen").id

    def tearDown(self):
        self.conn.close()
        self.engine.dispose()

    def _create(self, project="Remodel", area="Kitchen", notes="Cabinets"):
        return project_areas.create_project_area(self.conn, [project, area, notes])


class TestHomeProjectArea(unittest.TestCase):
    def test_defaults(self):
        pa = project_areas.HomeProjectArea()
        self.assertEqual(pa.project_id, "")
        self.assertEqual(pa.area_id, "")
        self.assertEqual(pa.notes, "")

    def test_str_includes_ids_and_notes(self):
        pa = project_areas.HomeProjectArea(project_id="p1", area_id="a1", notes="n")
        r = str(pa)
        self.assertIn("project p1 / area a1", r)
        self.assertIn("n", r)


class TestCreateProjectArea(ProjectAreasTestCase):
    def test_creates_by_name(self):
        pa = self._create()
        self.assertIsInstance(pa, project_areas.HomeProjectArea)
        self.assertEqual(pa.project_id, self.project_id)
        self.assertEqual(pa.area_id, self.area_id)
        self.assertEqual(pa.notes, "Cabinets")

    def test_creates_by_id(self):
        pa = self._create(self.project_id, self.area_id)
        self.assertIsInstance(pa, project_areas.HomeProjectArea)

    def test_notes_optional(self):
        pa = project_areas.create_project_area(self.conn, ["Remodel", "Kitchen"])
        self.assertEqual(pa.notes, "")

    def test_duplicate_returns_message(self):
        self._create()
        result = self._create()
        self.assertIsInstance(result, str)
        self.assertIn("already linked", result)

    def test_wrong_arg_count(self):
        with self.assertRaises(TypeError):
            project_areas.create_project_area(self.conn, ["Remodel"])
        with self.assertRaises(TypeError):
            project_areas.create_project_area(self.conn, ["a", "b", "c", "d"])

    def test_unknown_project(self):
        with self.assertRaises(ValueError):
            self._create(project="Nope")

    def test_unknown_area(self):
        with self.assertRaises(ValueError):
            self._create(area="Nope")


class TestGetProjectArea(ProjectAreasTestCase):
    def test_get_existing(self):
        self._create()
        pa = project_areas.get_project_area(self.conn, "Remodel", "Kitchen")
        self.assertIsNotNone(pa)
        self.assertEqual(pa.notes, "Cabinets")

    def test_get_missing_link(self):
        self.assertIsNone(
            project_areas.get_project_area(self.conn, "Remodel", "Garage")
        )

    def test_get_unknown_project(self):
        with self.assertRaises(ValueError):
            project_areas.get_project_area(self.conn, "Nope", "Kitchen")


class TestListProjectAreas(ProjectAreasTestCase):
    def test_list_by_project(self):
        self._create("Remodel", "Kitchen")
        self._create("Remodel", "Garage")
        result = project_areas.list_project_areas(self.conn, "Remodel")
        self.assertEqual(len(result), 2)

    def test_list_by_area(self):
        self._create("Remodel", "Kitchen")
        self._create("Paint", "Kitchen")
        result = project_areas.list_project_areas(self.conn, "Kitchen")
        self.assertEqual(len(result), 2)
        self.assertTrue(all(pa.area_id == self.area_id for pa in result))

    def test_list_empty(self):
        self.assertEqual(project_areas.list_project_areas(self.conn, "Remodel"), [])

    def test_list_unknown(self):
        with self.assertRaises(ValueError):
            project_areas.list_project_areas(self.conn, "Nope")

    def test_list_ambiguous(self):
        areas.create_area(self.conn, ["Remodel", "Same name as project"])
        with self.assertRaises(ValueError):
            project_areas.list_project_areas(self.conn, "Remodel")


class TestUpdateProjectArea(ProjectAreasTestCase):
    def test_update_notes(self):
        self._create()
        msg = project_areas.update_project_area(
            self.conn, "Remodel", "Kitchen", ["notes=New notes"]
        )
        self.assertIn("Updated", msg)
        pa = project_areas.get_project_area(self.conn, "Remodel", "Kitchen")
        self.assertEqual(pa.notes, "New notes")

    def test_no_args(self):
        with self.assertRaises(TypeError):
            project_areas.update_project_area(self.conn, "Remodel", "Kitchen", [])

    def test_missing_equals(self):
        self._create()
        with self.assertRaises(ValueError):
            project_areas.update_project_area(
                self.conn, "Remodel", "Kitchen", ["notes"]
            )

    def test_unknown_field(self):
        self._create()
        with self.assertRaises(ValueError):
            project_areas.update_project_area(
                self.conn, "Remodel", "Kitchen", ["bogus=1"]
            )

    def test_not_linked(self):
        with self.assertRaises(ValueError):
            project_areas.update_project_area(
                self.conn, "Remodel", "Garage", ["notes=x"]
            )


class TestDeleteProjectArea(ProjectAreasTestCase):
    def test_delete(self):
        self._create()
        self.assertTrue(
            project_areas.delete_project_area(self.conn, "Remodel", "Kitchen")
        )
        self.assertIsNone(
            project_areas.get_project_area(self.conn, "Remodel", "Kitchen")
        )

    def test_delete_unknown_area(self):
        with self.assertRaises(ValueError):
            project_areas.delete_project_area(self.conn, "Remodel", "Nope")


if __name__ == "__main__":
    unittest.main()
