# ProjectManager

Command line Project manager program written in python

## Prerequisites

- Python 3.10+
- [uv](https://github.com/astral-sh/uv) Python package manager
- Shell (zsh or bash)

## Commands

Usage: `uv run main.py <command> <type> [args...]`

Types: `project`, `area`, `tool`, `step`, `projectarea`, `steptool`

| Command   | Description                        | Arguments                                                                                                             |
| --------- | ---------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `create`  | Create a new record                | `<type> <args...>`                                                                                                    |
| `get`     | Get a single record                | `<type> <name\|id>`, `step <project> <step>`, `projectarea <project> <area>`, `steptool <project> <step> <tool>`      |
| `list`    | List records                       | `<type>`, `step <project>`, `projectarea <project\|area>`, `steptool <project> [step]`                                |
| `update`  | Update fields on a record          | `<type> <name> field=value...`, `step <project> <step> field=value...`, `projectarea <project> <area> field=value...` |
| `delete`  | Delete a record                    | `<type> <name>`, `projectarea <project> <area>`, `steptool <project> <step> <tool>`                                   |
| `display` | Display a project with its details | `project <name\|id>`                                                                                                  |
| `advance` | Advance a project step             | `step <project> <step>`                                                                                               |

## Example Commands

The test_commands.sh has example commands for building project data.

### Notes

This was a for fun project that was intentionally constrained to the CLI. A webserver with a proper GUI would have been far more visually appealing, more easily used, and easier to implement. It was fun though!
