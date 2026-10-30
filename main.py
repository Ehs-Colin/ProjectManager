# main python program for ProjectManager
import sys
from collections.abc import Callable

import sqlalchemy

import internal.areas
import internal.project_areas
import internal.project_step_tools
import internal.projects
import internal.projectsteps
import internal.tools

DB_URL = "sqlite:///projects.db"

Command = tuple[str, Callable[..., str], list[str]]


def create(conn: sqlalchemy.engine.Connection, table_name: str, args: list[str]) -> str:
    result = None
    match table_name:
        case "project":
            result = internal.projects.create_project(conn, args)
        case "area":
            result = internal.areas.create_area(conn, args)
        case "tool":
            result = internal.tools.create_tool(conn, args)
        case "step":
            result = internal.projectsteps.create_projectstep(conn, args)
        case "projectarea":
            result = internal.project_areas.create_project_area(conn, args)
        case "steptool":
            result = internal.project_step_tools.create_project_step_tool(conn, args)
        case _:
            return f"Invalid {table_name}: create aborted"

    if result is None:
        return f"Invalid {table_name}: create aborted"
    return f"Created '{table_name}' {result}"


def get(conn: sqlalchemy.engine.Connection, table_name: str, args: list[str]) -> str:
    if table_name in ("project", "area", "tool") and len(args) != 1:
        raise TypeError("get expects '<name|id>'")
    result = None
    match table_name:
        case "project":
            result = internal.projects.get_project(conn, args[0])
        case "area":
            result = internal.areas.get_area(conn, args[0])
        case "tool":
            result = internal.tools.get_tool(conn, args[0])
        case "step":
            if len(args) != 2:
                raise TypeError("get step expects '<project> <step>'")
            project, step = args
            result = internal.projectsteps.get_projectstep(conn, project, step)
        case "projectarea":
            if len(args) != 2:
                raise TypeError("get projectarea expects '<project> <area>'")
            project, area = args
            result = internal.project_areas.get_project_area(conn, project, area)
        case "steptool":
            if len(args) != 3:
                raise TypeError("get steptool expects '<project> <step> <tool>'")
            project, step, tool = args
            result = internal.project_step_tools.get_project_step_tool(
                conn, project, step, tool
            )
        case _:
            return f"Invalid {table_name}: get aborted"
    if result is None:
        return f"{table_name} not found"
    return str(result)


def get_list(
    conn: sqlalchemy.engine.Connection, table_name: str, args: list[str]
) -> str:
    match table_name:
        case "project":
            return str(internal.projects.list_projects(conn))
        case "area":
            return str(internal.areas.list_areas(conn))
        case "tool":
            return str(internal.tools.list_tools(conn))
        case "step":
            if len(args) != 1:
                raise TypeError("list step expects '<project>'")
            steps = internal.projectsteps.list_projectsteps(conn, args[0])
            if steps is None:
                return "project not found"
            return "".join(str(step) for step in steps)
        case "projectarea":
            if len(args) != 1:
                raise TypeError("list projectarea expects '<project|area>'")
            project_areas = internal.project_areas.list_project_areas(conn, args[0])
            return "".join(str(pa) for pa in project_areas)
        case "steptool":
            if len(args) not in (1, 2):
                raise TypeError("list steptool expects '<project> [step]'")
            step_tools = internal.project_step_tools.list_project_step_tools(
                conn, *args
            )
            return "".join(str(pst) for pst in step_tools)
        case _:
            return f"Invalid {table_name}: list aborted"


def update(conn: sqlalchemy.engine.Connection, table_name: str, args: list[str]) -> str:
    if table_name in ("project", "area", "tool") and len(args) < 2:
        raise TypeError("update expects '<name> field=value...'")
    result = None
    match table_name:
        case "project":
            result = internal.projects.update_project(conn, args[0], args[1:])
        case "area":
            result = internal.areas.update_area(conn, args[0], args[1:])
        case "tool":
            result = internal.tools.update_tool(conn, args[0], args[1:])
        case "step":
            if len(args) < 3:
                raise TypeError("update step expects '<project> <step> field=value...'")
            project, step, *fields = args
            result = internal.projectsteps.update_projectstep(
                conn, project, step, fields
            )
        case "projectarea":
            if len(args) < 3:
                raise TypeError(
                    "update projectarea expects '<project> <area> field=value...'"
                )
            project, area, *fields = args
            result = internal.project_areas.update_project_area(
                conn, project, area, fields
            )
        case _:
            return f"Invalid {table_name}: update aborted"
    return str(result)


def delete(conn: sqlalchemy.engine.Connection, table_name: str, args: list[str]) -> str:
    match table_name:
        case "project":
            success = internal.projects.delete_project(conn, args[0])
            return (
                f"Deleted {table_name} '{args[0]}'"
                if success
                else f"Failed to delete {table_name} '{args[0]}'"
            )
        case "area":
            success = internal.areas.delete_area(conn, args[0])
            return (
                f"Deleted {table_name} '{args[0]}'"
                if success
                else f"Failed to delete {table_name} '{args[0]}'"
            )
        case "tool":
            success = internal.tools.delete_tool(conn, args[0])
            return (
                f"Deleted {table_name} '{args[0]}'"
                if success
                else f"Failed to delete {table_name} '{args[0]}'"
            )
        case "step":
            success = internal.projectsteps.delete_projectstep(conn, args[0])
            return (
                f"Deleted {table_name} '{args[0]}'"
                if success
                else f"Failed to delete {table_name} '{args[0]}'"
            )
        case "projectarea":
            if len(args) != 2:
                raise TypeError("delete projectarea expects '<project> <area>'")
            project, area = args
            success = internal.project_areas.delete_project_area(conn, project, area)
            return (
                f"Deleted {table_name} '{project}' / '{area}'"
                if success
                else f"Failed to delete {table_name} '{project}' / '{area}'"
            )
        case "steptool":
            if len(args) != 3:
                raise TypeError("delete steptool expects '<project> <step> <tool>'")
            project, step, tool = args
            success = internal.project_step_tools.delete_project_step_tool(
                conn, project, step, tool
            )
            return (
                f"Deleted {table_name} '{project}' / '{step}' / '{tool}'"
                if success
                else f"Failed to delete {table_name} '{project}' / '{step}' / '{tool}'"
            )
        case _:
            return f"Invalid {table_name}: delete aborted"


def display(
    conn: sqlalchemy.engine.Connection, table_name: str, args: list[str]
) -> str:
    if table_name != "project":
        return f"Invalid {table_name}: display only supports project"
    if len(args) != 1:
        raise TypeError("display project expects '<name|id>'")
    result = internal.projects.display_project(conn, args[0])
    if not result:
        return f"{table_name} not found"
    return result


def advance(
    conn: sqlalchemy.engine.Connection, table_name: str, args: list[str]
) -> str:
    if table_name != "step":
        return f"Invalid {table_name}: advance only supports step"
    if len(args) != 2:
        raise TypeError("advance step expects '<project> <step>'")
    project, step = args
    return internal.projectsteps.advancestep(conn, project, step)


def get_commands() -> list[Command]:
    """Return the available user commands as (name, function, arg_names) tuples."""
    return [
        ("create", create, ["name", "description"]),
        ("get", get, ["[project]", "name|id"]),
        ("update", update, ["[project]", "name|id", "field=value..."]),
        ("delete", delete, ["name"]),
        ("list", get_list, ["type", "[project]"]),
        ("display", display, ["project", "name|id"]),
        ("advance", advance, ["step", "project", "step"]),
    ]


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <command>")
        sys.exit(1)

    command_name, *command_args = sys.argv[1:]
    commands = {name: (func, args) for name, func, args in get_commands()}

    if command_name not in commands:
        print(f"Error: Unknown command: {command_name}")
        sys.exit(1)

    func, _ = commands[command_name]
    engine = sqlalchemy.create_engine(DB_URL)
    try:
        table_name, *rest = command_args
        with engine.begin() as conn:
            print(func(conn, table_name, rest))
    except TypeError as e:
        print(f"Error: Bad arguments for {command_name}: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {command_name} failed: {e}")
        sys.exit(1)
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
