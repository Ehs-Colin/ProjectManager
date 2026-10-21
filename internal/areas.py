import uuid
from datetime import datetime

import sqlalchemy

import internal.db.areas
import internal.db.models


class Area:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.id = uuid.uuid4()
        self.create_at = datetime.now()
        self.update_at = datetime.now()

    def ConvertFromSql(self, sqlArea: internal.db.models.Area) -> None:
        self.id = sqlArea.id
        self.create_at = sqlArea.create_at
        self.update_at = sqlArea.update_at
        self.name = sqlArea.name
        self.description = sqlArea.description

    def __repr__(self) -> str:
        return f"""
=== {self.name} - ({self.id}) ===
    * description:        {self.description}
    * Created:            {self.create_at}
    * Updated:            {self.update_at}
"""


# CREATE TABLE Areas (
#     id TEXT PRIMARY KEY,
#     create_at TIMESTAMP NOT NULL,
#     update_at TIMESTAMP NOT NULL,
#     name TEXT NOT NULL,
#     description TEXT
# );
