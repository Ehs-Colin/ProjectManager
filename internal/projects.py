# Projects module for project manager
import uuid
from datetime import datetime

import sqlalchemy

import internal.db.models
import internal.db.project_areas
import internal.db.project_step_tools
import internal.db.projects
from internal import projectsteps


class HomeProject(internal.db.models.Project):
    def __init__(
        self,
        name="",
        description="",
        budget=0,
        completion_percent=0.0,
        active=True,
        complete=False,
    ):
        new_id = str(uuid.uuid4())
        if name == "":
            name = new_id
        super().__init__(
            id=new_id,
            name=name,
            description=description,
            budget=budget,
            completion_percent=completion_percent,
            active=active,
            complete=complete,
            create_at=datetime.now(),
            update_at=datetime.now(),
        )

    def ConvertFromSql(self, sqlProject: internal.db.models.Project) -> None:
        self.id = sqlProject.id
        self.name = sqlProject.name
        self.description = sqlProject.description
        self.budget = sqlProject.budget
        self.completion_percent = sqlProject.completion_percent
        self.active = sqlProject.active
        self.complete = sqlProject.complete
        self.create_at = sqlProject.create_at
        self.update_at = sqlProject.update_at

    def __str__(self) -> str:
        return f"""
=== PROJECT: {self.name} - ({self.id}) ===
 * description:        {self.description}
 * budget:             {self.budget}
 * completion_percent: {self.completion_percent}
 * active:             {self.active}
 * complete:           {self.complete}
 * Created:            {self.create_at}
 * Updated:            {self.update_at}
"""


def display_project(conn: sqlalchemy.engine.Connection, lookup: str) -> str:
    current_project = get_project(conn, lookup)
    if current_project is None:
        return ""

    result: str = f"=== PROJECT: {current_project.name}        {current_project.completion_percent}% ===\n"
    result += f"* description:        {current_project.description}\n"
    result += f"* budget:             {current_project.budget}\n"
    result += "----------------------------------------\n"

    current_areas = internal.db.project_areas.Querier(conn).get_project_areas_info(
        project_id=current_project.id
    )
    first = True
    for area in current_areas:
        if not first:
            result += "\n"
        result += f"--= Project Area: {area.name} =--\n"
        result += f" * {area.description}\n"
        result += f" * {area.project_area_notes}\n"
        first = False
    result += "----------------------------------------\n"

    current_project_steps = projectsteps.list_projectsteps(conn, current_project.id)
    if current_project_steps is not None:
        first = True
        for step in current_project_steps:
            if not first:
                result += "\n"
            result += (
                f" --= Step {step.name}:          {step.completion_percent}% =--\n"
            )
            result += f" * {step.description}\n"
            step_tools = internal.db.project_step_tools.Querier(
                conn
            ).get_project_step_tools_info(
                project_id=current_project.id, step_id=step.id
            )
            for tool in step_tools:
                result += f"      * Tool: {tool.name} - {tool.description}\n"
            first = False

    return result


def create_project(
    conn: sqlalchemy.engine.Connection, args: list[str]
) -> HomeProject | str:
    if len(args) != 2:
        raise TypeError(
            f"create project expects 2 arguments (name, description), got {len(args)}"
        )
    name, description = args
    project = HomeProject(name=name, description=description)
    query = internal.db.projects.Querier(conn)
    sqlProject = query.create_project(
        internal.db.projects.CreateProjectParams(
            name=project.name,
            description=project.description,
            id=project.id,
            budget=project.budget,
            completion_percent=project.completion_percent,
            active=project.active,
            complete=project.complete,
        )
    )
    if sqlProject is None:
        return f"failed to create project {name}"
    project.ConvertFromSql(sqlProject)
    return project


def delete_project(conn: sqlalchemy.engine.Connection, project_id: str) -> bool:
    query = internal.db.projects.Querier(conn)
    query.delete_project(id=project_id)
    return True


def get_project(conn: sqlalchemy.engine.Connection, lookup: str) -> HomeProject | None:
    try:
        return find_project(conn, lookup)
    except ValueError:
        return None


def list_projects(conn: sqlalchemy.engine.Connection) -> list[HomeProject] | None:
    query = internal.db.projects.Querier(conn)
    projects: list[HomeProject] = []
    for sqlProject in query.get_projects():
        project = HomeProject()
        project.ConvertFromSql(sqlProject)
        projects.append(project)
    return projects


_UPDATABLE_FIELDS = {
    "name": str,
    "description": str,
    "budget": int,
    "completion_percent": float,
    "active": lambda v: _parse_bool(v),
    "complete": lambda v: _parse_bool(v),
}


def _parse_bool(value: str) -> bool:
    lowered = value.strip().lower()
    if lowered in ("true", "1", "yes", "y"):
        return True
    if lowered in ("false", "0", "no", "n"):
        return False
    raise ValueError(f"invalid boolean value: {value!r}")


def update_project(
    conn: sqlalchemy.engine.Connection, project: str, args: list[str]
) -> str:
    if not args:
        raise TypeError(
            f"update project expects at least 1 field=value argument "
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

    existing = find_project(conn, project)

    params = {field: getattr(existing, field) for field in _UPDATABLE_FIELDS}
    params.update(updates)

    query = internal.db.projects.Querier(conn)
    query.update_project(
        internal.db.projects.UpdateProjectParams(id=existing.id, **params),
    )
    return f"Updated project with name {existing.name} ({', '.join(updates)})"


def find_project(conn: sqlalchemy.engine.Connection, project: str) -> HomeProject:
    query = internal.db.projects.Querier(conn)
    found = query.get_project_by_id(id=project)
    if found is None:
        found = query.get_project_by_name(name=project)
    if found is None:
        raise ValueError(f"no project found with id or name {project!r}")
    home_project = HomeProject()
    home_project.ConvertFromSql(found)
    return home_project


def get_project_id(conn: sqlalchemy.engine.Connection, project: str) -> str:
    found = find_project(conn, project)
    return found.id
