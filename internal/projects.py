# Projects module for project manager
import sys
from collections.abc import Callable


class Project:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.id = None


def create_project(name: str, description: str = "") -> Project:
    # TODO: persist the project
    return Project(name, description)


# CREATE TABLE Projects (
#     id uuid PRIMARY KEY,
#     name TEXT,
#     description TEXT,
#     budget INTEGER,
#     completion_percent REAL,
#     active BOOLEAN,
#     complete BOOLEAN
# );
