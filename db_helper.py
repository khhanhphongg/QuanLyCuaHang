"""Quản lý kết nối cơ sở dữ liệu SQLite an toàn với Context Manager."""

import sqlite3
import contextlib

DB_PATH = r'ims.db'

@contextlib.contextmanager
def get_db_connection():
    """Tạo kết nối DB với Context Manager đảm bảo tự động đóng."""
    con = sqlite3.connect(database=DB_PATH)
    try:
        yield con
    finally:
        con.close()

def execute_query(query, params=(), fetch_all=False, fetch_one=False, commit=False):
    """Thực thi câu truy vấn SQL an toàn."""
    with get_db_connection() as con:
        cur = con.cursor()
        cur.execute(query, params)
        if commit:
            con.commit()
        if fetch_all:
            return cur.fetchall()
        if fetch_one:
            return cur.fetchone()
        return None
