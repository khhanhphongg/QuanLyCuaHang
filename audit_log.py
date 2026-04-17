"""Nhật ký hoạt động hệ thống (Audit Log)."""

import sqlite3
import time
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ims.db")


def log_action(user: str, action: str, detail: str = ""):
    """Ghi một dòng nhật ký vào bảng audit_log.

    Args:
        user: Mã hoặc tên người dùng thực hiện.
        action: Loại thao tác (LOGIN, ADD_PRODUCT, CREATE_BILL, ...).
        detail: Mô tả chi tiết (tuỳ chọn).
    """
    try:
        con = sqlite3.connect(database=DB_PATH)
        cur = con.cursor()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        cur.execute(
            "INSERT INTO audit_log(timestamp, user, action, detail) VALUES(?,?,?,?)",
            (timestamp, user, action, detail)
        )
        con.commit()
    except Exception:
        pass  # Không để lỗi log làm crash ứng dụng
    finally:
        try:
            con.close()
        except Exception:
            pass


def get_recent_logs(limit: int = 50):
    """Lấy các dòng nhật ký gần nhất.

    Returns:
        list[tuple]: Danh sách (id, timestamp, user, action, detail).
    """
    try:
        con = sqlite3.connect(database=DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        con.close()
        return rows
    except Exception:
        return []
