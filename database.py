"""SQLite: создание таблицы и операции с заявками. Часть студент1."""

import sqlite3
from contextlib import closing
from pathlib import Path

DATABASE = Path(__file__).with_name("applications.db")


def connect():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with closing(connect()) as connection, connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                group_name TEXT NOT NULL,
                project_title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                priority TEXT NOT NULL
            )
        """)


def get_all():
    with closing(connect()) as connection:
        return connection.execute(
            "SELECT * FROM applications ORDER BY id DESC"
        ).fetchall()


def get_by_id(application_id):
    with closing(connect()) as connection:
        return connection.execute(
            "SELECT * FROM applications WHERE id = ?", (application_id,)
        ).fetchone()


def create(data):
    with closing(connect()) as connection, connection:
        cursor = connection.execute("""
            INSERT INTO applications
                (full_name, group_name, project_title, description, category, priority)
            VALUES (?, ?, ?, ?, ?, ?)
        """, tuple(data[key] for key in (
            "full_name", "group_name", "project_title", "description", "category", "priority"
        )))
        return cursor.lastrowid


def update(application_id, data):
    with closing(connect()) as connection, connection:
        connection.execute("""
            UPDATE applications SET full_name = ?, group_name = ?, project_title = ?,
                description = ?, category = ?, priority = ?
            WHERE id = ?
        """, tuple(data[key] for key in (
            "full_name", "group_name", "project_title", "description", "category", "priority"
        )) + (application_id,))


def delete(application_id):
    with closing(connect()) as connection, connection:
        connection.execute("DELETE FROM applications WHERE id = ?", (application_id,))
