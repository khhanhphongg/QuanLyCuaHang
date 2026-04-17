"""Hộp thoại xác nhận thoát ứng dụng."""

from tkinter import messagebox


class exitClass:
    """Hiển thị hộp thoại xác nhận và đóng cửa sổ chính."""
    def __init__(self, root):
        self.root = root
        self.confirm_exit()

    def confirm_exit(self):
        """Hỏi người dùng trước khi thoát."""
        answer = messagebox.askyesno("Xác nhận thoát", "Bạn có chắc chắn muốn thoát chương trình không?")
        if answer:
            self.root.destroy()
