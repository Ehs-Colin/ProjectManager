import uuid
from datetime import datetime

import sqlalchemy

import internal.db.areas
import internal.db.models


class HomeArea(internal.db.models.Area):
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

    def ConvertFromSql(self, sqlArea: internal.db.models.Area) -> None:
        self.id = sqlArea.id
        self.name = sqlArea.name
        self.description = sqlArea.description
        self.create_at = sqlArea.create_at
        self.update_at = sqlArea.update_at

    def __repr__(self) -> str:
        return f"""
=== AREA: {self.name} - ({self.id}) ===
 * description:        {self.description}
 * Created:            {self.create_at}
 * Updated:            {self.update_at}
"""


def create_area(conn: sqlalchemy.engine.Connection, args: list[str]) -> str:
    if len(args) != 2:
        raise TypeError(
            f"create area expects 2 arguments (name, description), got {len(args)}"
        )
    name, description = args
    area = HomeArea(name=name, description=description)
    query = internal.db.areas.Querier(conn)
    query.create_area(id=area.id, name=area.name, description=area.description)
    return f"Created area '{area.name}' with id {area.id}"


def delete_area(conn: sqlalchemy.engine.Connection, area_id: str) -> bool:
    query = internal.db.areas.Querier(conn)
    query.delete_area(id=area_id)
    return True


def get_area(
    conn: sqlalchemy.engine.Connection, lookup: str, by: str = "name"
) -> HomeArea | None:
    query = internal.db.areas.Querier(conn)
    if by == "name":
        sqlArea = query.get_area_by_name(name=lookup)
    elif by == "id":
        sqlArea = query.get_area_by_id(id=lookup)
    else:
        raise ValueError(f"invalid lookup type {by}; expected 'name' or 'id'")
    if sqlArea is None:
        return None
    area = HomeArea()
    area.ConvertFromSql(sqlArea)
    return area


def list_areas(conn: sqlalchemy.engine.Connection) -> list[HomeArea] | None:
    query = internal.db.areas.Querier(conn)
    areas: list[HomeArea] = []
    for sqlArea in query.get_areas():
        area = HomeArea()
        area.ConvertFromSql(sqlArea)
        areas.append(area)
    return areas


_UPDATABLE_FIELDS = {
    "name": str,
    "description": str,
}


def update_area(
    conn: sqlalchemy.engine.Connection, area_name: str, args: list[str]
) -> str:
    if not args:
        raise TypeError(
            f"update area expects at least 1 field=value argument "
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

    query = internal.db.areas.Querier(conn)
    existing = query.get_area_by_name(name=area_name)
    if existing is None:
        raise ValueError(f"no area found with name {area_name}")

    params = {field: getattr(existing, field) for field in _UPDATABLE_FIELDS}
    params.update(updates)

    query.update_area(id=existing.id, **params)
    return f"Updated area with name {area_name} ({', '.join(updates)})"
