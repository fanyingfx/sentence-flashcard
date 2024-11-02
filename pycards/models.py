import sqlite3
from flask import g, current_app
from contextlib import contextmanager
from datetime import datetime

TODAY_STR = datetime.today().strftime("%Y-%m-%d")


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db_name = current_app.config["DATABASE"]
        g._database = sqlite3.connect(db_name)
        db = g._database
    return db


@contextmanager
def get_db_connection():
    db = get_db()
    try:
        yield db
    except Exception as e:
        print("Error",e)
    finally:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource("schema.sql", mode="r") as f:
        db.cursor().executescript(f.read())
    db.commit()
