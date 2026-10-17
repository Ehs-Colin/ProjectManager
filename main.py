# main python program for ProjectManager
import sys
from collections.abc import Callable

Command = tuple[str, Callable[..., str], list[str]]


def create_project(name: str, description: str = "") -> str:
    # TODO: persist the project
    return f"Created project '{name}'"


def get_project(name: str) -> str:
    # TODO: look up the project
    return f"Project '{name}'"


def update_project(name: str, field: str, value: str) -> str:
    # TODO: apply the update
    return f"Updated '{field}' on project '{name}' to '{value}'"


def delete_project(name: str) -> str:
    # TODO: remove the project
    return f"Deleted project '{name}'"


def get_commands() -> list[Command]:
    """Return the available user commands as (name, function, arg_names) tuples."""
    return [
        ("create_project", create_project, ["name", "description"]),
        ("get_project", get_project, ["name"]),
        ("update_project", update_project, ["name", "field", "value"]),
        ("delete_project", delete_project, ["name"]),
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
    try:
        print(func(*command_args))
    except TypeError as e:
        print(f"Error: Bad arguments for {command_name}: {e}")
        sys.exit(1)

    if __name__ == "__main__":
        main()
