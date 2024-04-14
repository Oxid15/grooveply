import sqlite3

import pendulum

from ..models import EmployerPage
from ..settings import DB_NAME, TZ


class EmployerAPI:
    @classmethod
    def create(cls, name: str) -> int:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

        now = str(pendulum.now(tz=TZ))
        cur.execute(
            "INSERT INTO employer (name, created_at) VALUES"
            " (?, ?)"
            " ON CONFLICT (name) DO UPDATE set name = excluded.name,"
            " created_at = employer.created_at"
            " RETURNING id",
            (name, now),
        )
        new_id = cur.fetchall()[0][0]
        con.commit()
        return new_id

    @classmethod
    def get_page(cls, id: int) -> EmployerPage:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute(
            "SELECT id, name, created_at FROM employer WHERE id = ?",
            (id,),
        )
        emp_data = cur.fetchone()

        cur.execute(
            "SELECT COUNT(*) FROM application app"
            " JOIN employer emp"
            " ON app.employer_id = emp.id"
            " WHERE emp.id = ?",
            (id,),
        )
        app_cnt = cur.fetchone()[0]

        cur.execute(
            "SELECT COUNT(*) FROM location loc"
            " JOIN application app"
            " ON loc.id = app.location_id"
            " JOIN employer emp"
            " ON app.employer_id = emp.id"
            " WHERE emp.id = ?",
            (id,),
        )
        loc_cnt = cur.fetchone()[0]

        return EmployerPage(
            name=emp_data[1],
            created_at=emp_data[2],
            total_applications=app_cnt,
            total_locations=loc_cnt,
        )
