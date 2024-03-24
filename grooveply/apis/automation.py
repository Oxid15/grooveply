import sqlite3

import pendulum

from ..models import Automation, TimePeriod
from ..settings import DB_NAME, TZ
from .application import ApplicationStatusAPI


class AutomationAPI:
    @classmethod
    def create(
        self, if_status_is_id: int, change_status_to_id: int, after: int, period: TimePeriod
    ) -> int:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

        now = pendulum.now(tz=TZ)
        cur.execute(
            "INSERT INTO automation "
            "(if_status_is, change_status_to, after, period, created_at) VALUES"
            " (?, ?, ?, ?, ?)"
            " RETURNING id",
            (
                if_status_is_id,
                change_status_to_id,
                after,
                period,
                now,
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
