# main python program for ProjectManager
import sys
from collections.abc import Callable

import sqlalchemy

import internal.projects

DB_URL = "sqlite:///projects.db"

Command = tuple[str, Callable[..., str], list[str]]


def create(conn: sqlalchemy.engine.Connection, table_name: str, args: list[str]) -> str:
    result = None
    if table_name == "project":
        result = internal.projects.create_project(conn, args)
    # TODO:
    return f"Created '{table_name}'\n{result}"


def get(conn: sqlalchemy.engine.Connection, table_name: str, args: list[str]) -> str:
    result = None
    if table_name == "project":
        result = internal.projects.get_project(conn, args[0])
    # TODO:
    return str(result)


def update(conn: sqlalchemy.engine.Connection, table_name: str, args: list[str]) -> str:
    # TODO:
    return f"Updated table '{table_name}'"


def delete(conn: sqlalchemy.engine.Connection, table_name: str, args: list[str]) -> str:
    if table_name == "project":
        return internal.projects.delete_project(conn, args[0])
    # TODO:
    return f"Deleted table '{table_name}'"


def get_commands() -> list[Command]:
    """Return the available user commands as (name, function, arg_names) tuples."""
    return [
        ("create", create, ["name", "description"]),
        ("get", get, ["name"]),
        ("update", update, ["name", "field", "value"]),
        ("delete", delete, ["name"]),
    ]


def main():
    print("Welcom to Project Manager!")

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
