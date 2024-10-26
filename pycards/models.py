import sqlite3
from flask import g, current_app
from contextlib import contextmanager


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        g._database = sqlite3.connect(current_app.config["DATABASE"])
        db = g._database
    return db


@contextmanager
def get_db_connection():
    db = get_db()
    yield db
    db.close()


def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql", mode="r") as f:
        db.cursor().executescript(f.read())
    db.commit()
