import sqlite3

import pendulum

from .settings import DB_NAME


def create_tables():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS application("
        "id INTEGER PRIMARY KEY NOT NULL,"
        "employer_id BIGINT NOT NULL,"
        "location_id BIGINT,"
        "job_board_id BIGINT,"
        "status_id BIGINT NOT NULL,"
        "status_updated_at TEXT NOT NULL,"
        "description TEXT,"
        "url TEXT,"
        "created_at TEXT"
        ")"
    )

    cur.execute(
        "CREATE TABLE IF NOT EXISTS employer("
        "id INTEGER PRIMARY KEY NOT NULL,"
        "name VARCHAR(255) NOT NULL,"
        "created_at TEXT,"
        "CONSTRAINT unique_name UNIQUE (name)"
        ")"
    )

    cur.execute(
        "CREATE TABLE IF NOT EXISTS application_status("
        "id INTEGER PRIMARY KEY NOT NULL,"
        "name VARCHAR(255) NOT NULL"
        ")"
    )

    cur.execute(
        "INSERT INTO application_status VALUES"
        " (0, 'TO APPLY'), (1, 'APPLIED'),"
        " (2, 'ACTIVE'), (3, 'STALE'),"
        " (4, 'REJECT'), (5, 'CLOSED')"
        " ON CONFLICT (id) DO NOTHING "
        ""
    )

    cur.execute(
        "CREATE TABLE IF NOT EXISTS automation("
        "id INTEGER PRIMARY KEY NOT NULL,"
        "if_status_is INTEGER NOT NULL,"
        "change_status_to INTEGER NOT NULL,"
        "after INTEGER NOT NULL,"
        "period TEXT NOT NULL,"
        "created_at TEXT NOT NULL"
        ")"
    )

    cur.execute(
        "CREATE TABLE IF NOT EXISTS location("
        "id INTEGER PRIMARY KEY NOT NULL,"
        "name TEXT UNIQUE NOT NULL,"
        "created_at TEXT NOT NULL"
        ")"
    )

    cur.execute(
        "CREATE TABLE IF NOT EXISTS job_board("
        "id INTEGER PRIMARY KEY NOT NULL,"
        "name TEXT UNIQUE NOT NULL,"
        "url TEXT UNIQUE,"
        "created_at TEXT NOT NULL"
        ")"
    )

    cur.execute(
        "CREATE TABLE IF NOT EXISTS application_update("
        "id INTEGER PRIMARY KEY NOT NULL,"
        "description TEXT NOT NULL,"
        "created_at TEXT NOT NULL,"
        "triggerer_type VARCHAR NOT NULL,"
        "triggerer_id VARCHAR NOT NULL"
        ")"
    )

    cur.execute(
        "CREATE TABLE IF NOT EXISTS application_to_update("
        "id INTEGER PRIMARY KEY NOT NULL,"
        "application_id INTEGER NOT NULL,"
        "update_id INTEGER NOT NULL"
        ")"
    )

    cur.execute("CREATE TABLE IF NOT EXISTS schema_history (version INTEGER NOT NULL)")
    cur.execute("INSERT INTO schema_history (version) VALUES (0)")

    con.commit()


def register_update(app_id: int, description: str, triggerer_type: str, triggerer_id: int):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    now = str(pendulum.now())
    cur.execute(
        "INSERT INTO application_update"
        " (description, created_at, triggerer_type, triggerer_id) VALUES"
        " (?, ?, ?, ?)"
        " RETURNING id",
        (description, now, triggerer_type, triggerer_id),
    )
    inserted = cur.fetchall()[0][0]

    cur.execute(
        "INSERT INTO application_to_update" " (application_id, update_id) VALUES (?, ?)",
        (app_id, inserted),
    )

    con.commit()
