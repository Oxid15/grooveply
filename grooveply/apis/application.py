import sqlite3
from typing import Optional

import pendulum
from pendulum import DateTime

from ..models import Application, ApplicationStatus, Employer
from ..settings import DB_NAME, TZ


class ApplicationStatusAPI:
    @classmethod
    def get(self, id: int) -> ApplicationStatus:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("SELECT name from application_status WHERE id = ?", (id,))
        data = cur.fetchall()[0]

        return ApplicationStatus(id=id, name=data[0])


class ApplicationAPI:
    @classmethod
    def create(cls, employer_id: int, status_id: int, description: str, url: str) -> int:
        now = pendulum.now(tz=TZ)
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO application "
            "(employer_id, status_id, description, url, status_updated_at, created_at) VALUES"
            " (?, ?, ?, ?, ?, ?)"
            " RETURNING id",
            (employer_id, status_id, description, url, str(now), str(now)),
        )
        app_id = cur.fetchall()[0][0]
        con.commit()
        return app_id

    @classmethod
    def get(self, id: int) -> Application:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute(
            "SELECT app.id, emp.name, aps.name, app.description,"
            " app.url,"
            " app.status_updated_at, app.created_at"
            " FROM application app"
            " JOIN employer emp ON app.employer_id = emp.id"
            " JOIN application_status aps"
            " ON app.status_id = aps.id"
            " WHERE app.id = ?",
            (id,),
        )
        data = cur.fetchall()[0]

        app = Application(
            id=data[0],
            employer=Employer(name=data[1]),
            status=ApplicationStatus(name=data[2]),
            description=data[3],
            url=data[4],
            status_updated_at=data[5],
            created_at=data[6],
        )
        return app

    @classmethod
    def update(
        self,
        id: int,
        status_id: Optional[int],
        status_updated_at: Optional[DateTime],
        description: Optional[str],
        url: Optional[str],
    ):
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

        cur.execute(
            """
            UPDATE application
            SET status_id = COALESCE(?, status_id),
            status_updated_at = COALESCE(?, status_updated_at),
            description = COALESCE(?, description),
            url = COALESCE(?, url)
            WHERE id = ?;
            """,
            (status_id, status_updated_at, description, url, id),
        )
        con.commit()

    @classmethod
    def get_all(cls) -> list[Application]:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute(
            "SELECT app.id, emp.name, aps.name, app.description, app.url, app.created_at"
            " FROM application app"
            " JOIN employer emp ON app.employer_id = emp.id"
            " JOIN application_status aps"
            " ON app.status_id = aps.id"
            " ORDER BY app.created_at DESC"
        )
        data = cur.fetchall()

        results = []
        for app in data:
            results.append(
                Application(
                    id=app[0],
                    employer=Employer(name=app[1]),
                    status=ApplicationStatus(name=app[2]),
                    description=app[3],
                    url=app[4],
                    created_at=app[5],
                )
            )
        return results
