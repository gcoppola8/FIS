import os
import uuid

from sqlalchemy import create_engine, text
from sqlalchemy.orm import create_session

db_name = "db.sqlite"

if "PYTEST_RUN_CONFIG" in os.environ:
    db_name = str(uuid.uuid1()) + '.sqlite'

print(f"database name: {db_name}")

engine = create_engine("sqlite+pysqlite:///%s" % db_name, echo=True)
session = create_session(engine)

from data.models import *

Base.metadata.create_all(engine)

if session.query(User).get(1) is None:
    import sqlite3
    connection = sqlite3.connect(db_name)

    with open("script.sql", 'r') as s:
        sql_script = s.read()
        connection.executescript(sql_script)
    s.closed
