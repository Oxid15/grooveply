import sqlite3
from typing import Optional

import pendulum
from pendulum import DateTime

from .models import Application, ApplicationStatus, Automation, Employer
from .settings import DB_NAME, TZ


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


class ApplicationAPI:
    @classmethod
    def create(
        cls,
        employer_id: int,
        status_id: int,
        description: str,
        url: str
    ) -> int:
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


class ApplicationStatusAPI:
    @classmethod
    def get(self, id: int) -> ApplicationStatus:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("SELECT name from application_status WHERE id = ?", (id,))
        data = cur.fetchall()[0]

        return ApplicationStatus(id=id, name=data[0])

    @classmethod
    def get_by_name(self, name: str) -> ApplicationStatus:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("SELECT id from application_status WHERE name = ?", (name,))
        data = cur.fetchall()[0]

        return ApplicationStatus(id=data[0], name=name)


class AutomationAPI:
    @classmethod
    def create(self, auto: Automation) -> int:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

        cur.execute(
            "INSERT INTO automation "
            "(if_status_is, change_status_to, after, period, created_at) VALUES"
            " (?, ?, ?, ?, ?)"
            " RETURNING id",
            (
                auto.if_status_is.id,
                auto.change_status_to.id,
                auto.after,
                auto.period,
                auto.created_at,
            ),
        )
        auto_id = cur.fetchall()[0][0]
        con.commit()
        return auto_id

    @classmethod
    def get_all(self) -> list[Automation]:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute(
            "SELECT id, if_status_is, change_status_to, after, period, created_at"
            " FROM automation"
        )
        data = cur.fetchall()

        # TODO: make joins instead of fetching a lot of times
        results = []
        for auto in data:
            results.append(
                Automation(
                    id=auto[0],
                    if_status_is=ApplicationStatusAPI.get(auto[1]),
                    change_status_to=ApplicationStatusAPI.get(auto[2]),
                    after=auto[3],
                    period=auto[4],
                    created_at=auto[5],
                )
            )
        return results
