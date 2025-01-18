import sqlite3
from typing import List, Optional

import pendulum
from pydantic import BaseModel

from ..models import EmployerPage
from ..settings import DB_NAME, TZ


class Employer(BaseModel):
    id: int
    name: str
    application_count: int
    latest_apply: str


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
            "SELECT COUNT(DISTINCT loc.id) FROM location loc"
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

    @classmethod
    def get_all(cls) -> List[Employer]:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute(
            """
            SELECT
                e.id,
                e.name,
                count(a.id) as application_count,
                max(a.created_at) as latest_apply
            FROM employer as e
            JOIN application a
            ON a.employer_id = e.id
            GROUP BY e.id
            ORDER BY a.created_at DESC
            """,
        )
        data = cur.fetchall()

        return [
            Employer(
                id=item[0],
                name=item[1],
                application_count=item[2],
                latest_apply=item[3],
            )
            for item in data
        ]

    @classmethod
    def get_total_count(cls) -> int:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("SELECT COUNT(id) FROM employer")
        return cur.fetchone()[0]
