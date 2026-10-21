# Projects module for project manager
import uuid
from datetime import datetime
from venv import create

import sqlalchemy

import internal.db.models
import internal.db.projects


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
        # self.name = name
        # self.description = description
        # self.id = new_id
        # self.budget = budget
        # self.completion_percent = completion_percent
        # self.active = active
        # self.complete = complete
        # self.create_at = datetime.now()
        # self.update_at = datetime.now()

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

    def __repr__(self) -> str:
        return f"""
=== {self.name} - ({self.id}) ===
 * description:        {self.description}
 * budget:             {self.budget}
 * completion_percent: {self.completion_percent}
 * active:             {self.active}
 * complete:           {self.complete}
 * Created:            {self.create_at}
 * Updated:            {self.update_at}
"""


def create_project(conn: sqlalchemy.engine.Connection, args: list[str]) -> str:
    if len(args) != 2:
        raise TypeError(
            f"create project expects 2 arguments (name, description), got {len(args)}"
        )
    name, description = args
    project = HomeProject(name=name, description=description)
    query = internal.db.projects.Querier(conn)
    query.create_project(
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
    return f"Created project '{project.name}' with id {project.id}"


def delete_project(conn: sqlalchemy.engine.Connection, project_id: str) -> bool:
    query = internal.db.projects.Querier(conn)
    query.delete_project(id=project_id)
    return True


def get_project(
    conn: sqlalchemy.engine.Connection, lookup: str, by: str = "name"
) -> HomeProject | None:
    query = internal.db.projects.Querier(conn)
    if by == "name":
        sqlProject = query.get_project_by_name(name=lookup)
    elif by == "id":
        sqlProject = query.get_project_by_id(id=lookup)
    else:
        raise ValueError(f"invalid lookup type {by}; expected 'name' or 'id'")
    if sqlProject is None:
        return None
    project = HomeProject()
    project.ConvertFromSql(sqlProject)
    return project


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
    conn: sqlalchemy.engine.Connection, project_name: str, args: list[str]
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

    query = internal.db.projects.Querier(conn)
    existing = query.get_project_by_name(name=project_name)
    if existing is None:
        raise ValueError(f"no project found with name {project_name}")

    params = {field: getattr(existing, field) for field in _UPDATABLE_FIELDS}
    params.update(updates)

    query.update_project(
        internal.db.projects.UpdateProjectParams(id=existing.id, **params),
    )
    return f"Updated project with name {project_name} ({', '.join(updates)})"
