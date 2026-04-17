"""Sao lưu tự động cơ sở dữ liệu khi khởi động hệ thống."""

import os
import shutil
import time
import glob


BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "backups")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ims.db")
MAX_BACKUPS = 7


def auto_backup():
    """Sao lưu ims.db vào backups/, giữ tối đa MAX_BACKUPS bản gần nhất.

    Returns:
        str: Thông báo kết quả sao lưu.
    """
    try:
        if not os.path.exists(DB_PATH):
            return "⚠ Không tìm thấy ims.db"

        os.makedirs(BACKUP_DIR, exist_ok=True)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_name = f"ims_backup_{timestamp}.db"
        backup_path = os.path.join(BACKUP_DIR, backup_name)

        shutil.copy2(DB_PATH, backup_path)

        # Xoá bản backup cũ nếu vượt quá MAX_BACKUPS.
        backups = sorted(glob.glob(os.path.join(BACKUP_DIR, "ims_backup_*.db")))
        while len(backups) > MAX_BACKUPS:
            os.remove(backups.pop(0))

        return f"✅ Đã sao lưu lúc {time.strftime('%H:%M')}"
    except Exception as ex:
        return f"⚠ Lỗi sao lưu: {str(ex)}"


if __name__ == "__main__":
    print(auto_backup())
