# Project areas module for project manager
import sqlalchemy

import internal.db.areas
import internal.db.models
import internal.db.project_areas
import internal.db.projects


class HomeProjectArea(internal.db.models.Projectarea):
    def __init__(self, project_id="", area_id="", notes=""):
        super().__init__(project_id=project_id, area_id=area_id, notes=notes)

    def ConvertFromSql(self, sqlProjectArea: internal.db.models.Projectarea) -> None:
        self.project_id = sqlProjectArea.project_id
        self.area_id = sqlProjectArea.area_id
        self.notes = sqlProjectArea.notes

    def __str__(self) -> str:
        return f"""
=== PROJECT AREA: project {self.project_id} / area {self.area_id} ===
 * notes:              {self.notes}
"""


def _find_project(
    conn: sqlalchemy.engine.Connection, project: str
) -> internal.db.models.Project | None:
    query = internal.db.projects.Querier(conn)
    found = query.get_project_by_id(id=project)
    if found is None:
        found = query.get_project_by_name(name=project)
    return found


def _find_area(
    conn: sqlalchemy.engine.Connection, area: str
) -> internal.db.models.Area | None:
    query = internal.db.areas.Querier(conn)
    found = query.get_area_by_id(id=area)
    if found is None:
        found = query.get_area_by_name(name=area)
    return found


def _resolve_project_id(conn: sqlalchemy.engine.Connection, project: str) -> str:
    found = _find_project(conn, project)
    if found is None:
        raise ValueError(f"no project found with id or name {project!r}")
    return found.id


def _resolve_area_id(conn: sqlalchemy.engine.Connection, area: str) -> str:
    found = _find_area(conn, area)
    if found is None:
        raise ValueError(f"no area found with id or name {area!r}")
    return found.id


def _get_existing(
    query: internal.db.project_areas.Querier, project_id: str, area_id: str
) -> internal.db.models.Projectarea | None:
    for pa in query.get_project_areas(project_id=project_id):
        if pa.area_id == area_id:
            return pa
    return None


def create_project_area(
    conn: sqlalchemy.engine.Connection, args: list[str]
) -> HomeProjectArea | str:
    if len(args) not in (2, 3):
        raise TypeError(
            f"create project area expects 2 or 3 arguments "
            f"(project, area, [notes]), got {len(args)}"
        )
    project, area = args[0], args[1]
    notes = args[2] if len(args) == 3 else ""
    project_id = _resolve_project_id(conn, project)
    area_id = _resolve_area_id(conn, area)

    query = internal.db.project_areas.Querier(conn)
    if _get_existing(query, project_id, area_id) is not None:
        return f"project {project!r} is already linked to area {area!r}"
    sqlProjectArea = query.create_project_area(
        project_id=project_id, area_id=area_id, notes=notes
    )
    if sqlProjectArea is None:
        return f"failed to link project {project!r} to area {area!r}"
    projectArea = HomeProjectArea()
    projectArea.ConvertFromSql(sqlProjectArea)
    return projectArea


def delete_project_area(
    conn: sqlalchemy.engine.Connection, project: str, area: str
) -> bool:
    project_id = _resolve_project_id(conn, project)
    area_id = _resolve_area_id(conn, area)
    query = internal.db.project_areas.Querier(conn)
    query.delete_project_area(project_id=project_id, area_id=area_id)
    return True


def get_project_area(
    conn: sqlalchemy.engine.Connection, project: str, area: str
) -> HomeProjectArea | None:
    project_id = _resolve_project_id(conn, project)
    area_id = _resolve_area_id(conn, area)
    query = internal.db.project_areas.Querier(conn)
    sqlProjectArea = _get_existing(query, project_id, area_id)
    if sqlProjectArea is None:
        return None
    projectArea = HomeProjectArea()
    projectArea.ConvertFromSql(sqlProjectArea)
    return projectArea


def list_project_areas(
    conn: sqlalchemy.engine.Connection, lookup: str
) -> list[HomeProjectArea]:
    """List links for a project or an area, identified by id or name."""
    query = internal.db.project_areas.Querier(conn)
    project = _find_project(conn, lookup)
    area = _find_area(conn, lookup)
    if project is not None and area is not None:
        raise ValueError(f"{lookup!r} matches both a project and an area")
    if project is not None:
        rows = query.get_project_areas(project_id=project.id)
    elif area is not None:
        rows = query.get_area_projects(area_id=area.id)
    else:
        raise ValueError(f"no project or area found with id or name {lookup!r}")

    projectAreas: list[HomeProjectArea] = []
    for sqlProjectArea in rows:
        projectArea = HomeProjectArea()
        projectArea.ConvertFromSql(sqlProjectArea)
        projectAreas.append(projectArea)
    return projectAreas


_UPDATABLE_FIELDS = {
    "notes": str,
}


def update_project_area(
    conn: sqlalchemy.engine.Connection, project: str, area: str, args: list[str]
) -> str:
    if not args:
        raise TypeError(
            f"update project area expects at least 1 field=value argument "
            f"({', '.join(_UPDATABLE_FIELDS)})"
        )

    updates: dict[str, object] = {}
    for arg in args:
        field, sep, value = arg.partition("=")
        field = field.strip()
        if not sep:
            raise ValueError(f"expected field=value, got {arg!r}")
        if field not in _UPDATABLE_FIELDS:
            raise ValueError(
                f"unknown field {field!r}; valid fields: {', '.join(_UPDATABLE_FIELDS)}"
            )
        updates[field] = _UPDATABLE_FIELDS[field](value)

    project_id = _resolve_project_id(conn, project)
    area_id = _resolve_area_id(conn, area)
    query = internal.db.project_areas.Querier(conn)
    if _get_existing(query, project_id, area_id) is None:
        raise ValueError(f"project {project!r} is not linked to area {area!r}")

    query.update_project_area(
        project_id=project_id, area_id=area_id, notes=updates["notes"]
    )
    return f"Updated project area {project} / {area} ({', '.join(updates)})"
