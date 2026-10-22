import uuid
from datetime import datetime

import sqlalchemy

import internal.db.models
import internal.db.tools


class HomeTool(internal.db.models.Tool):
    def __init__(self, name="", description=""):
        new_id = str(uuid.uuid4())
        if name == "":
            name = new_id
        super().__init__(
            id=new_id,
            name=name,
            description=description,
            create_at=datetime.now(),
            update_at=datetime.now(),
        )

    def ConvertFromSql(self, sqlTool: internal.db.models.Tool) -> None:
        self.id = sqlTool.id
        self.name = sqlTool.name
        self.description = sqlTool.description
        self.create_at = sqlTool.create_at
        self.update_at = sqlTool.update_at

    def __repr__(self) -> str:
        return f"""
=== TOOL: {self.name} - ({self.id}) ===
 * description:        {self.description}
 * Created:            {self.create_at}
 * Updated:            {self.update_at}
"""


def create_tool(conn: sqlalchemy.engine.Connection, args: list[str]) -> str:
    if len(args) != 2:
        raise TypeError(
            f"create tool expects 2 arguments (name, description), got {len(args)}"
        )
    name, description = args
    tool = HomeTool(name=name, description=description)
    query = internal.db.tools.Querier(conn)
    query.create_tool(id=tool.id, name=tool.name, description=tool.description)
    return f"Created tool '{tool.name}' with id {tool.id}"


def delete_tool(conn: sqlalchemy.engine.Connection, tool_id: str) -> bool:
    query = internal.db.tools.Querier(conn)
    query.delete_tool(id=tool_id)
    return True


def get_tool(
    conn: sqlalchemy.engine.Connection, lookup: str, by: str = "name"
) -> HomeTool | None:
    query = internal.db.tools.Querier(conn)
    if by == "name":
        sqlTool = query.get_tool_by_name(name=lookup)
    elif by == "id":
        sqlTool = query.get_tool_by_id(id=lookup)
    else:
        raise ValueError(f"invalid lookup type {by}; expected 'name' or 'id'")
    if sqlTool is None:
        return None
    tool = HomeTool()
    tool.ConvertFromSql(sqlTool)
    return tool


def list_tools(conn: sqlalchemy.engine.Connection) -> list[HomeTool] | None:
    query = internal.db.tools.Querier(conn)
    tools: list[HomeTool] = []
    for sqlTool in query.get_tools():
        tool = HomeTool()
        tool.ConvertFromSql(sqlTool)
        tools.append(tool)
    return tools


_UPDATABLE_FIELDS = {
    "name": str,
    "description": str,
}


def update_tool(
    conn: sqlalchemy.engine.Connection, tool_name: str, args: list[str]
) -> str:
    if not args:
        raise TypeError(
            f"update tool expects at least 1 field=value argument "
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

    query = internal.db.tools.Querier(conn)
    existing = query.get_tool_by_name(name=tool_name)
    if existing is None:
        raise ValueError(f"no tool found with name {tool_name}")

    params = {field: getattr(existing, field) for field in _UPDATABLE_FIELDS}
    params.update(updates)

    query.update_tool(id=existing.id, **params)
    return f"Updated tool with name {tool_name} ({', '.join(updates)})"
