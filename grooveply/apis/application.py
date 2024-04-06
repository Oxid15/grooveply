import sqlite3
from typing import Optional

import pendulum
from pendulum import DateTime

from ..models import (
    Application,
    ApplicationStatus,
    ApplicationUpdate,
    Employer,
    LatestUpdateRow,
)
from ..settings import DB_NAME, TZ


class ApplicationStatusAPI:
    @classmethod
    def get(self, id: int) -> ApplicationStatus:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("SELECT name from application_status WHERE id = ?", (id,))
        data = cur.fetchall()[0]

        return ApplicationStatus(id=id, name=data[0])


class ApplicationUpdateAPI:
    @classmethod
    def get_all(self, app_id: int) -> list[ApplicationUpdate]:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute(
            "SELECT au.id, description, au.created_at, triggerer_type, triggerer_id"
            " FROM application_update au"
            " JOIN application_to_update atu ON au.id = atu.update_id"
            " WHERE atu.application_id = ?"
            " ORDER BY created_at ASC",
            (app_id,),
        )
        data = cur.fetchall()
        updates = []
        for tup in data:
            updates.append(
                ApplicationUpdate(
                    id=tup[0],
                    description=tup[1],
                    created_at=tup[2],
                    triggerer_type=tup[3],
                    triggerer_id=tup[4],
                )
            )
        return updates

    @classmethod
    def get_latest(self, limit: int) -> list[LatestUpdateRow]:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute(
            "SELECT au.description, au.created_at, triggerer_type, triggerer_id,"
            " atu.application_id, emp.name"
            " FROM application_update au"
            " JOIN application_to_update atu ON au.id = atu.update_id"
            " JOIN application app"
            " ON atu.application_id = app.id"
            " JOIN employer emp"
            " ON app.employer_id = emp.id"
            " ORDER BY au.created_at DESC"
            " LIMIT ?",
            (limit,),
        )
        data = cur.fetchall()
        updates = []
        for tup in data:
            updates.append(
                LatestUpdateRow(
                    description=tup[0],
                    created_at=tup[1],
                    triggerer=f"{tup[2]} {tup[3]}",
                    application_id=tup[4],
                    employer=tup[5],
                )
            )
        return updates


class ApplicationAPI:
    @classmethod
    def create(
        cls,
        employer_id: int,
        status_id: int,
        location_id: Optional[int],
        job_board_id: Optional[int],
        description: str,
        url: str,
    ) -> int:
        now = pendulum.now(tz=TZ)
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute(
            "INSERT INTO application"
            " (employer_id, status_id, location_id,"
            " job_board_id,"
            " description, url, status_updated_at, created_at) VALUES"
            " (?, ?, ?, ?, ?, ?, ?, ?)"
            " RETURNING id",
            (
                employer_id,
                status_id,
                location_id,
                job_board_id,
                description,
                url,
                str(now),
                str(now),
            ),
        )
        app_id = cur.fetchall()[0][0]
        con.commit()
        return app_id

    @classmethod
    def get(self, id: int) -> Application:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute(
            "SELECT app.id, emp.name, status.name, loc.name, jb.name, app.description,"
            " app.url,"
            " app.status_updated_at, app.created_at"
            " FROM application app"
            " JOIN employer emp ON app.employer_id = emp.id"
            " JOIN application_status status"
            " ON app.status_id = status.id"
            " LEFT JOIN location loc"
            " ON app.location_id = loc.id"
            " LEFT JOIN job_board jb"
            " ON app.job_board_id = jb.id"
            " WHERE app.id = ?",
            (id,),
        )
        data = cur.fetchall()[0]

        app = Application(
            id=data[0],
            employer=Employer(name=data[1]),
            status=ApplicationStatus(name=data[2]),
            location_name=data[3],
            job_board_name=data[4],
            description=data[5],
            url=data[6],
            status_updated_at=data[7],
            created_at=data[8],
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
    def delete(self, id: int):
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

        cur.execute("DELETE FROM application WHERE id = ?", (id,))
        con.commit()

    @classmethod
    def get_all(cls) -> list[Application]:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute(
            "SELECT app.id, emp.name, status.name, loc.name, "
            " jb.name,"
            " app.description, app.url, app.status_updated_at, app.created_at"
            " FROM application app"
            " JOIN employer emp ON app.employer_id = emp.id"
            " JOIN application_status status"
            " ON app.status_id = status.id"
            " LEFT JOIN location loc"
            " ON app.location_id = loc.id"
            " LEFT JOIN job_board jb"
            " ON app.job_board_id = jb.id"
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
                    location_name=app[3],
                    job_board_name=app[4],
                    description=app[5],
                    url=app[6],
                    status_updated_at=app[7],
                    created_at=app[8],
                )
            )
        return results
