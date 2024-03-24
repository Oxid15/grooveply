import sqlite3

from ..settings import DB_NAME


class EmployerAPI:
    @classmethod
    def create(cls, name: str) -> int:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO employer (name) VALUES"
            " (?)"
            " ON CONFLICT (name) DO UPDATE set name = excluded.name"
            " RETURNING id",
            (name,),
        )
        new_id = cur.fetchall()[0][0]
        con.commit()
        return new_id
