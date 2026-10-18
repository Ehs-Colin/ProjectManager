# Projects module for project manager
import uuid

import sqlalchemy

import internal.db.models
import internal.db.projects


class Project:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.id = uuid.uuid4()
        self.budget = 0
        self.completion_percent = 0.0
        self.active = True
        self.complete = False

    def ConvertFromSql(self, sqlProject: internal.db.models.Project) -> None:
        self.id = sqlProject.id
        self.name = sqlProject.name
        self.description = sqlProject.description
        self.budget = sqlProject.budget
        self.completion_percent = sqlProject.completion_percent
        self.active = sqlProject.active
        self.complete = sqlProject.complete

    def __str__(self) -> str:
        return f"Project(name={self.name}\n * description={self.description}\n * id={self.id}\n * budget={self.budget}\n * completion_percent={self.completion_percent}\n * active={self.active}\n * complete={self.complete}\n)"

    def __repr__(self) -> str:
        return f"Project(name={self.name}\n * description={self.description}\n * id={self.id}\n * budget={self.budget}\n * completion_percent={self.completion_percent}\n * active={self.active}\n * complete={self.complete}\n)"


def create_project(conn: sqlalchemy.engine.Connection, args: list[str]) -> str:
    if len(args) != 2:
        raise TypeError(
            f"create project expects 2 arguments (name, description), got {len(args)}"
        )
    name, description = args
    project = Project(name, description)
    query = internal.db.projects.Querier(conn)
    query.create_project(
        internal.db.projects.CreateProjectParams(
            id=str(project.id),
            name=project.name,
            description=project.description,
            budget=project.budget,
            completion_percent=project.completion_percent,
            active=project.active,
            complete=project.complete,
        ),
    )
    return f"Created project '{project.name}' with id {project.id}"


def delete_project(conn: sqlalchemy.engine.Connection, project_id: str) -> str:
    query = internal.db.projects.Querier(conn)
    query.delete_project(id=project_id)
    return f"Deleted project with id {project_id}"


def get_project(conn: sqlalchemy.engine.Connection, project_name: str) -> Project:
    query = internal.db.projects.Querier(conn)
    sqlProject = query.get_project_by_name(name=project_name)
    project = Project(str(sqlProject.name), str(sqlProject.description))
    project.ConvertFromSql(sqlProject)
    return project


# CREATE TABLE Projects (
#     id uuid PRIMARY KEY,
#     name TEXT,
#     description TEXT,
#     budget INTEGER,
#     completion_percent REAL,
#     active BOOLEAN,
#     complete BOOLEAN
# );
