import sqlite3

import pendulum

from ..models import Location
from ..settings import DB_NAME, TZ


class LocationAPI:
    @classmethod
    def create(cls, name: str) -> int:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

        now = pendulum.now(tz=TZ)
        cur.execute(
            "INSERT INTO location (name, created_at) VALUES"
            " (?, ?)"
            " ON CONFLICT (name) DO UPDATE set name = excluded.name"
            " RETURNING id",
            (name, str(now)),
        )
        new_id = cur.fetchall()[0][0]
        con.commit()
        return new_id

    @classmethod
    def get_all(self) -> list[Location]:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("SELECT id, name, created_at FROM location")
        data = cur.fetchall()

        locs = []
        for row in data:
            locs.append(Location(id=row[0], name=row[1], created_at=row[2]))
        return locs
