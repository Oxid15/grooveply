import sqlite3

import pendulum

from ..models import Goal, TimePeriod
from ..settings import DB_NAME, TZ


class GoalAPI:
    @classmethod
    def create(
        cls, value: int, each: int, period: TimePeriod, start_date: str, end_date: str
    ) -> int:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

        now = str(pendulum.now(tz=TZ))
        cur.execute(
            "INSERT INTO application_goal"
            " (value, each, period, start_date, end_date, created_at) VALUES"
            " (?, ?, ?, ?, ?, ?)"
            " RETURNING id",
            (value, each, period, start_date, end_date, now),
        )
        new_id = cur.fetchall()[0][0]
        con.commit()
        return new_id

    @classmethod
    def get(cls, id: int) -> Goal:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute(
            "SELECT id, value, each, period,"
            " start_date, end_date, created_at"
            " FROM application_goal WHERE id = ?",
            (id,),
        )
        data = cur.fetchone()

        return Goal(
            id=data[0],
            value=data[1],
            each=data[2],
            period=data[3],
            start_date=data[4],
            end_date=data[5],
            created_at=data[6],
        )

    @classmethod
    def get_all(cls) -> list[Goal]:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute(
            "SELECT id, value, each, period,"
            " start_date, end_date, created_at"
            " FROM application_goal"
        )
        data = cur.fetchall()

        goals = []
        for item in data:
            goals.append(
                Goal(
                    id=item[0],
                    value=item[1],
                    each=item[2],
                    period=item[3],
                    start_date=item[4],
                    end_date=item[5],
                    created_at=item[6],
                )
            )
        return goals

    @classmethod
    def delete(self, id: int):
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute(
            "DELETE FROM application_goal WHERE id = ?",
            (id,),
        )
        con.commit()
