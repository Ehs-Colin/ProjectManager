# Project step tools module for project manager
import sqlalchemy

import internal.db.models
import internal.db.project_step_tools
import internal.projects
import internal.projectsteps
import internal.tools


class HomeProjectStepTool(internal.db.models.Projectsteptool):
    def __init__(self, project_id="", step_id="", tool_id=""):
        super().__init__(project_id=project_id, step_id=step_id, tool_id=tool_id)

    def ConvertFromSql(
        self, sqlProjectStepTool: internal.db.models.Projectsteptool
    ) -> None:
        self.project_id = sqlProjectStepTool.project_id
        self.step_id = sqlProjectStepTool.step_id
        self.tool_id = sqlProjectStepTool.tool_id

    def __str__(self) -> str:
        return f"""
=== PROJECT STEP TOOL: project {self.project_id} / step {self.step_id} / tool {self.tool_id} ===
"""


def _get_step_id(conn: sqlalchemy.engine.Connection, project_id: str, step: str) -> str:
    found = internal.projectsteps.get_projectstep(conn, project_id, step)
    if found is None:
        raise ValueError(
            f"no project step found with id or name {step!r} in project {project_id!r}"
        )
    return found.id


def _resolve_ids(
    conn: sqlalchemy.engine.Connection, project: str, step: str, tool: str
) -> tuple[str, str, str]:
    project_id = internal.projects.get_project_id(conn, project)
    step_id = _get_step_id(conn, project_id, step)
    tool_id = internal.tools.find_tool(conn, tool).id
    return project_id, step_id, tool_id


def _get_existing(
    query: internal.db.project_step_tools.Querier,
    project_id: str,
    step_id: str,
    tool_id: str,
) -> internal.db.models.Projectsteptool | None:
    for pst in query.get_tools_project_step(project_id=project_id, step_id=step_id):
        if pst.tool_id == tool_id:
            return pst
    return None


def create_project_step_tool(
    conn: sqlalchemy.engine.Connection, args: list[str]
) -> HomeProjectStepTool | str:
    if len(args) != 3:
        raise TypeError(
            f"create project step tool expects 3 arguments "
            f"(project, step, tool), got {len(args)}"
        )
    project, step, tool = args
    project_id, step_id, tool_id = _resolve_ids(conn, project, step, tool)

    query = internal.db.project_step_tools.Querier(conn)
    if _get_existing(query, project_id, step_id, tool_id) is not None:
        return (
            f"step {step!r} in project {project!r} is already linked to tool {tool!r}"
        )
    sqlProjectStepTool = query.create_project_step_tool(
        project_id=project_id, step_id=step_id, tool_id=tool_id
    )
    if sqlProjectStepTool is None:
        return f"failed to link step {step!r} in project {project!r} to tool {tool!r}"
    projectStepTool = HomeProjectStepTool()
    projectStepTool.ConvertFromSql(sqlProjectStepTool)
    return projectStepTool


def delete_project_step_tool(
    conn: sqlalchemy.engine.Connection, project: str, step: str, tool: str
) -> bool:
    project_id, step_id, tool_id = _resolve_ids(conn, project, step, tool)
    query = internal.db.project_step_tools.Querier(conn)
    query.delete_project_step_tool(
        project_id=project_id, step_id=step_id, tool_id=tool_id
    )
    return True


def get_project_step_tool(
    conn: sqlalchemy.engine.Connection, project: str, step: str, tool: str
) -> HomeProjectStepTool | None:
    project_id, step_id, tool_id = _resolve_ids(conn, project, step, tool)
    query = internal.db.project_step_tools.Querier(conn)
    sqlProjectStepTool = _get_existing(query, project_id, step_id, tool_id)
    if sqlProjectStepTool is None:
        return None
    projectStepTool = HomeProjectStepTool()
    projectStepTool.ConvertFromSql(sqlProjectStepTool)
    return projectStepTool


def list_project_step_tools(
    conn: sqlalchemy.engine.Connection, project: str, step: str | None = None
) -> list[HomeProjectStepTool]:
    """List tool links for a project, or for a single step within it."""
    project_id = internal.projects.get_project_id(conn, project)
    query = internal.db.project_step_tools.Querier(conn)
    if step is None:
        rows = query.get_project_step_tools(project_id=project_id)
    else:
        step_id = _get_step_id(conn, project_id, step)
        rows = query.get_tools_project_step(project_id=project_id, step_id=step_id)

    projectStepTools: list[HomeProjectStepTool] = []
    for sqlProjectStepTool in rows:
        projectStepTool = HomeProjectStepTool()
        projectStepTool.ConvertFromSql(sqlProjectStepTool)
        projectStepTools.append(projectStepTool)
    return projectStepTools
