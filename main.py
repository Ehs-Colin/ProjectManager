# main python program for ProjectManager
import sys
from collections.abc import Callable

import sqlalchemy

import internal.areas
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
        case _:
            return f"Invalid {table_name}: create aborted"

    if result is None:
        return f"Invalid {table_name}: create aborted"
    return f"Created '{table_name}'\n{result}"


def get(conn: sqlalchemy.engine.Connection, table_name: str, args: list[str]) -> str:
    if table_name != "step" and (len(args) != 2 or args[0] not in ("--name", "--id")):
        raise TypeError("get expects '--name <name>' or '--id <id>'")
    result = None
    match table_name:
        case "project":
            flag, value = args
            result = internal.projects.get_project(
                conn, value, by=flag.removeprefix("--")
            )
        case "area":
            flag, value = args
            result = internal.areas.get_area(conn, value, by=flag.removeprefix("--"))
        case "tool":
            flag, value = args
            result = internal.tools.get_tool(conn, value, by=flag.removeprefix("--"))
        case "step":
            if len(args) != 4 or args[0] not in ("--project-name", "--project-id"):
                raise TypeError(
                    "get step expects '--project-name <name>' or '--project-id <id>' "
                    "followed by '--name <name>' or '--id <id>'"
                )
            project_flag, project, *args = args
            flag, value = args
            result = internal.projectsteps.get_projectstep(
                conn,
                project,
                value,
                by=flag.removeprefix("--"),
                project_by=project_flag.removeprefix("--project-"),
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
            if len(args) != 2 or args[0] not in ("--project-name", "--project-id"):
                raise TypeError(
                    "list step expects '--project-name <name>' or '--project-id <id>'"
                )
            project_flag, project_value = args
            steps = internal.projectsteps.list_projectsteps(
                conn,
                project_value,
                project_by=project_flag.removeprefix("--project-"),
            )
            if steps is None:
                return "project not found"
            return "".join(str(step) for step in steps)
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
            if len(args) < 4 or args[0] not in ("--project-name", "--project-id"):
                raise TypeError(
                    "update step expects '--project-name <name>' or "
                    "'--project-id <id>' followed by '<step_name> field=value...'"
                )
            project_flag, project, step_name, *fields = args
            result = internal.projectsteps.update_projectstep(
                conn,
                project,
                step_name,
                fields,
                project_by=project_flag.removeprefix("--project-"),
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
        case _:
            return f"Invalid {table_name}: delete aborted"


def get_commands() -> list[Command]:
    """Return the available user commands as (name, function, arg_names) tuples."""
    return [
        ("create", create, ["name", "description"]),
        ("get", get, ["[--project-name|--project-id project]", "--name|--id", "value"]),
        (
            "update",
            update,
            ["[--project-name|--project-id project]", "name", "field=value..."],
        ),
        ("delete", delete, ["name"]),
        ("list", get_list, ["type", "[--project-name|--project-id project]"]),
    ]


def main():
    # print("Welcom to Project Manager!")

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
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
