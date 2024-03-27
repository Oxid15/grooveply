import sqlite3

import pendulum

from .apis.automation import AutomationAPI
from .db import register_update
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
            " RETURNING application.id"
        )

        cur.execute(
            sql,
            (
                auto.change_status_to.id,
                str(pendulum.now(tz=TZ)),
                auto.if_status_is.id,
            ),
        )

        updated_app_ids = cur.fetchall()
        con.commit()

        for id_tup in updated_app_ids:
            i = id_tup[0]
            register_update(
                i,
                f"Changed status {auto.if_status_is.name} -> {auto.change_status_to.name}",
                "automation",
                auto.id,
            )
