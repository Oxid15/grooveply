import sqlite3
from typing import Optional

import pendulum

from ..models import JobBoard
from ..settings import DB_NAME, TZ


class JobBoardAPI:
    @classmethod
    def create(cls, name: str, url: Optional[str]) -> int:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()

        now = pendulum.now(tz=TZ)
        cur.execute(
            "INSERT INTO job_board (name, url, created_at) VALUES"
            " (?, ?, ?)"
            " ON CONFLICT (name) DO UPDATE set name = excluded.name"
            " ON CONFLICT (url) DO UPDATE set url = excluded.url"
            " RETURNING id",
            (name, url, str(now)),
        )
        new_id = cur.fetchall()[0][0]
        con.commit()
        return new_id

    @classmethod
    def get_all(self) -> list[JobBoard]:
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("SELECT id, name, url, created_at FROM job_board")
        data = cur.fetchall()

        jbs = []
        for row in data:
            jbs.append(JobBoard(id=row[0], name=row[1], url=row[2], created_at=row[3]))
        return jbs
