# Project steps module for project manager
import uuid
from datetime import datetime

import sqlalchemy

import internal.db.models
import internal.db.project_steps
import internal.db.projects
import internal.projects


class HomeProjectStep(internal.db.models.Projectstep):
    def __init__(
        self,
        project_id="",
        name="",
        description="",
        completion_percent=0.0,
        order_id=0,
        performstepvalue=0,
        projectvalue=0,
    ):
        new_id = str(uuid.uuid4())
        if name == "":
            name = new_id
        super().__init__(
            id=new_id,
            project_id=project_id,
            name=name,
            description=description,
            completion_percent=completion_percent,
            order_id=order_id,
            performstepvalue=performstepvalue,
            projectvalue=projectvalue,
            create_at=datetime.now(),
            update_at=datetime.now(),
        )

    def ConvertFromSql(self, sqlStep: internal.db.models.Projectstep) -> None:
        self.id = sqlStep.id
        self.project_id = sqlStep.project_id
        self.name = sqlStep.name
        self.description = sqlStep.description
        self.completion_percent = sqlStep.completion_percent
        self.order_id = sqlStep.order_id
        self.performstepvalue = sqlStep.performstepvalue
        self.projectvalue = sqlStep.projectvalue
        self.create_at = sqlStep.create_at
        self.update_at = sqlStep.update_at

    def __str__(self) -> str:
        return f"""
=== PROJECT STEP: {self.name} - ({self.id}) ===
 * project_id:         {self.project_id}
 * description:        {self.description}
 * completion_percent: {self.completion_percent}
 * order_id:           {self.order_id}
 * performstepvalue:   {self.performstepvalue}
 * projectvalue:       {self.projectvalue}
 * Created:            {self.create_at}
 * Updated:            {self.update_at}
"""


def _verify_project(conn: sqlalchemy.engine.Connection, project_id: str) -> None:
    query = internal.db.projects.Querier(conn)
    if query.get_project_by_id(id=project_id) is None:
        raise ValueError(f"no project found with id {project_id}")


def create_projectstep(
    conn: sqlalchemy.engine.Connection, args: list[str]
) -> HomeProjectStep | str:
    if len(args) != 3:
        raise TypeError(
            "create projectstep expects 3 arguments "
            f"(project_id, name, description), got {len(args)}"
        )
    project_id, name, description = args
    _verify_project(conn, project_id)
    step = HomeProjectStep(project_id=project_id, name=name, description=description)
    query = internal.db.project_steps.Querier(conn)
    sqlStep = query.create_project_step(
        internal.db.project_steps.CreateProjectStepParams(
            id=step.id,
            project_id=step.project_id,
            name=step.name,
            description=step.description,
            completion_percent=step.completion_percent,
            order_id=step.order_id,
            performstepvalue=step.performstepvalue,
            projectvalue=step.projectvalue,
        )
    )
    if sqlStep is None:
        return f"Failed to create project step '{step.name}'"
    step.ConvertFromSql(sqlStep)
    return step


def delete_projectstep(conn: sqlalchemy.engine.Connection, step_id: str) -> bool:
    query = internal.db.project_steps.Querier(conn)
    query.delete_project_step(id=step_id)
    return True


def list_projectsteps(
    conn: sqlalchemy.engine.Connection,
    project: str,
) -> list[HomeProjectStep] | None:
    try:
        sqlProject = internal.projects.find_project(conn, project)
    except ValueError:
        return None
    query = internal.db.project_steps.Querier(conn)
    steps: list[HomeProjectStep] = []
    for sqlStep in query.get_project_steps_by_project_id(project_id=sqlProject.id):
        step = HomeProjectStep()
        step.ConvertFromSql(sqlStep)
        steps.append(step)
    return steps


def get_projectstep(
    conn: sqlalchemy.engine.Connection,
    project: str,
    lookup: str,
) -> HomeProjectStep | None:
    try:
        found = internal.projects.find_project(conn, project)
    except ValueError:
        return None
    query = internal.db.project_steps.Querier(conn)
    sqlStep = query.get_project_step_by_id(id=lookup)
    if sqlStep is None or sqlStep.project_id != found.id:
        sqlStep = query.get_project_step_by_name(project_id=found.id, name=lookup)
    if sqlStep is None:
        return None
    step = HomeProjectStep()
    step.ConvertFromSql(sqlStep)
    return step


# project_id is intentionally excluded: steps cannot be moved between projects.
_UPDATABLE_FIELDS = {
    "name": str,
    "description": str,
    "completion_percent": float,
    "order_id": int,
    "performstepvalue": int,
    "projectvalue": int,
}


def update_projectstep(
    conn: sqlalchemy.engine.Connection,
    project: str,
    step: str,
    args: list[str],
) -> str:
    if not args:
        raise TypeError(
            f"update projectstep expects at least 1 field=value argument "
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

    existing = get_projectstep(conn, project, step)
    if existing is None:
        raise ValueError(
            f"no project step found with id or name {step!r} in project {project!r}"
        )

    params = {field: getattr(existing, field) for field in _UPDATABLE_FIELDS}
    params.update(updates)

    query = internal.db.project_steps.Querier(conn)
    query.update_project_step(
        internal.db.project_steps.UpdateProjectStepParams(id=existing.id, **params),
    )
    return f"Updated project step with name {existing.name} ({', '.join(updates)})"


def advancestep(
    conn: sqlalchemy.engine.Connection,
    project: str,
    step: str,
) -> str:
    existing = get_projectstep(conn, project, step)
    if existing is None:
        raise ValueError(
            f"no project step found with id or name {step!r} in project {project!r}"
        )

    current = existing.completion_percent or 0.0
    if current >= 100:
        return f"Project step {existing.name} is already 100% complete"
    new_percent = min(current + 1, 100.0)
    update_projectstep(
        conn, project, existing.id, [f"completion_percent={new_percent}"]
    )

    # Recompute from all steps so the project total stays consistent with
    # each step's weighted contribution (projectvalue * completion / 100).
    steps = list_projectsteps(conn, project) or []
    project_percent = sum(
        (s.projectvalue or 0) * (s.completion_percent or 0.0) / 100 for s in steps
    )
    project_percent = min(round(project_percent, 2), 100.0)
    internal.projects.update_project(
        conn, existing.project_id, [f"completion_percent={project_percent}"]
    )

    return (
        f"Advanced project step {existing.name} to {new_percent}% "
        f"(project now {project_percent}%)"
    )


def set_step_projectvalue(
    conn: sqlalchemy.engine.Connection,
    project: str,
    step: str,
    value: int | str,
) -> str:
    value = int(value)
    if value < 0 or value > 100:
        raise ValueError(f"projectvalue must be between 0 and 100, got {value}")

    steps = list_projectsteps(conn, project)
    if steps is None:
        raise ValueError(f"no project found with id or name {project!r}")

    existing = get_projectstep(conn, project, step)
    if existing is None:
        raise ValueError(
            f"no project step found with id or name {step!r} in project {project!r}"
        )

    # Exclude the step being set, since its current value is being replaced.
    other_total = sum(s.projectvalue or 0 for s in steps if s.id != existing.id)
    available = 100 - other_total
    if value > available:
        raise ValueError(
            f"projectvalue {value} exceeds remaining available value {available} "
            f"(other steps total {other_total})"
        )

    return update_projectstep(conn, project, existing.id, [f"projectvalue={value}"])
