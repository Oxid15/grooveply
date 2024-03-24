import sqlite3

import pendulum

from .apis.automation import AutomationAPI
from .settings import DB_NAME, TZ


def update_statuses():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    automations = AutomationAPI.get_all()

    for auto in automations:
        sql = (
            "UPDATE application SET"
            " status_id = ?,"
            " status_updated_at = ?"
            "WHERE id IN "
            "(SELECT id FROM application"
            f" WHERE datetime(status_updated_at, '+{auto.after} {auto.period}') <= datetime()"
            " AND status_id = ?)"
        )

        cur.execute(
            sql,
            (
                auto.change_status_to.id,
                str(pendulum.now(tz=TZ)),
                auto.if_status_is.id,
            ),
        )
        con.commit()
