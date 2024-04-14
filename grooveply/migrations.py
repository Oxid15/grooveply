import sqlite3

import pendulum

from .db import DB_NAME
from .settings import TZ


def get_current_schema_version() -> int:
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT version FROM schema_history ORDER BY version DESC LIMIT 1")
    return int(cur.fetchone()[0])


def migration_1():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    cur.execute("PRAGMA foreign_keys=off")
    cur.execute("BEGIN TRANSACTION")
    cur.execute("ALTER TABLE application_to_update RENAME TO application_to_update_old")

    cur.execute(
        "CREATE TABLE application_to_update("
        "id INTEGER PRIMARY KEY NOT NULL,"
        "application_id INTEGER NOT NULL,"
        "update_id INTEGER NOT NULL,"
        "CONSTRAINT fk_application"
        " FOREIGN KEY (application_id)"
        " REFERENCES application(id)"
        " ON DELETE CASCADE"
        ")"
    )

    cur.execute("INSERT INTO application_to_update SELECT * FROM application_to_update_old")
    cur.execute("DROP TABLE application_to_update_old")
    cur.execute("END TRANSACTION")
    cur.execute("PRAGMA foreign_keys=on")
    cur.execute("INSERT INTO schema_history VALUES (?)", (1,))

    cur.execute(
        "UPDATE employer SET created_at = ? WHERE created_at is NULL", (str(pendulum.now(tz=TZ)))
    )
    con.commit()


MIGRATIONS = {1: migration_1}


def apply_migrations():
    ver = get_current_schema_version()
    for num in [ver_num for ver_num in MIGRATIONS if ver_num > ver]:
        MIGRATIONS[num]()
