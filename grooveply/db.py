import sqlite3

from .settings import DB_NAME


def create_tables():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS application("
        "id INTEGER PRIMARY KEY NOT NULL,"
        "employer_id BIGINT NOT NULL,"
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

    con.commit()
