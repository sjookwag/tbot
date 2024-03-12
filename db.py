import sqlite3
import contextlib
from constants import path_to_file

def execute_statement(statement):
    with contextlib.closing(sqlite3.connect(path_to_file)) as conn: # auto-closes
        with conn: # auto-commits
            with contextlib.closing(conn.cursor()) as cursor: # auto-closes
                cursor.execute(statement)