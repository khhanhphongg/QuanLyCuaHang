"""Màn hình đăng nhập và chuyển sang Dashboard theo vai trò người dùng."""

import hashlib
from tkinter import *
from PIL import Image, ImageTk
from tkinter import messagebox
import sqlite3
import sys
import subprocess
from ui_theme import COLORS, FONTS, apply_ttk_theme
from ui_scale import AutoScale
from audit_log import log_action
from create_db import create_db


def hash_password(password: str) -> str:
    """Băm mật khẩu bằng SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


class loginClass:
    """Hiển thị form đăng nhập và gọi main.py sau khi xác thực."""
    def __init__(self, root):
        self.root = root
        self.root.title("Đăng nhập Hệ thống - Cửa hàng Tiện lợi")
        self.root.geometry("1000x500")
        apply_ttk_theme()
        APP_BG = COLORS["bg"]
        CARD_BG = COLORS["surface"]
        TITLE_FG = COLORS["text"]
        LABEL_FG = COLORS["text"]
        MUTED_FG = COLORS["text_muted"]
        INPUT_BG = COLORS["input_bg"]
        INPUT_BORDER = COLORS["border"]
        ACCENT_BG = COLORS["primary"]
        ACCENT_ACTIVE = COLORS["primary_hover"]
        self.root.config(bg=APP_BG)

        self.center_window(1000, 500)
        self.root.resizable(True, True)

        # Cột trái: ảnh minh họa.
        img_frame = Frame(self.root, bg=CARD_BG)
        img_frame.place(x=50, y=50, width=400, height=400)

        try:
            self.im = Image.open("Images/images/im1.png")
            self.im = self.im.resize((400, 400), Image.LANCZOS)
            self.im = ImageTk.PhotoImage(self.im)
            lbl_img = Label(img_frame, image=self.im, bg=CARD_BG, bd=0)
            lbl_img.place(x=0, y=0)
        except Exception as e:
            print(f"Lỗi tải ảnh im1.png: {str(e)}")
            lbl_img = Label(img_frame, text="Chưa có ảnh im1.png", bg=APP_BG, fg=MUTED_FG)
            lbl_img.place(x=0, y=0, width=400, height=400)

        # Cột phải: form đăng nhập.
        login_frame = Frame(self.root, bd=0, bg=CARD_BG)
        login_frame.place(x=450, y=50, width=500, height=400)

        Label(login_frame, text="ĐĂNG NHẬP HỆ THỐNG", font=FONTS["title"], bg=CARD_BG, fg=TITLE_FG).pack(
            pady=40)

        # Mã nhân viên.
        Label(login_frame, text="Mã Nhân Viên (ID):", font=FONTS["body"], bg=CARD_BG, fg=LABEL_FG).place(x=50, y=120)
        self.employee_id = Entry(login_frame, font=FONTS["body"], bg=INPUT_BG, highlightthickness=1,
                                 highlightbackground=INPUT_BORDER, highlightcolor=ACCENT_BG, bd=0)
        self.employee_id.place(x=50, y=150, width=400, height=40)
        self.employee_id.insert(0, "NV01")

        # Mật khẩu + nút hiện/ẩn.
        Label(login_frame, text="Mật khẩu:", font=FONTS["body"], bg=CARD_BG, fg=LABEL_FG).place(x=50, y=210)

        self._pw_visible = False
        self.password = Entry(login_frame, font=FONTS["body"], bg=INPUT_BG, show="*", highlightthickness=1,
                              highlightbackground=INPUT_BORDER, highlightcolor=ACCENT_BG, bd=0)
        self.password.place(x=50, y=240, width=355, height=40)
        self.password.insert(0, "123456")

        self.btn_eye = Button(login_frame, text="👁", font=FONTS["body"], bg=INPUT_BG, bd=0,
                              cursor="hand2", command=self.toggle_password,
                              highlightthickness=1, highlightbackground=INPUT_BORDER)
        self.btn_eye.place(x=408, y=240, width=42, height=40)

        Button(login_frame, text="ĐĂNG NHẬP NGAY", command=self.login, font=FONTS["body_bold"], bg=ACCENT_BG,
               fg="black", activebackground=ACCENT_ACTIVE, activeforeground="white", bd=0, cursor="hand2").place(
            x=50, y=320, width=400, height=50)

        self.root.bind('<Return>', lambda e: self.login())

        self.scaler = AutoScale(self.root, 1000, 500)

    def toggle_password(self):
        """Hiện/ẩn mật khẩu."""
        self._pw_visible = not self._pw_visible
        self.password.config(show="" if self._pw_visible else "*")
        self.btn_eye.config(text="🙈" if self._pw_visible else "👁")

    def center_window(self, w, h):
        """Canh giữa cửa sổ trên màn hình."""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = int((screen_width / 2) - (w / 2))
        y = int((screen_height / 2) - (h / 2))
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def login(self):
        """Xác thực tài khoản và mở Dashboard với vai trò tương ứng."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if self.employee_id.get() == "" or self.password.get() == "":
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin", parent=self.root)
            else:
                raw_password = self.password.get()
                hashed = hash_password(raw_password)
                cur.execute("SELECT utype, password FROM employee WHERE eid=?",
                            (self.employee_id.get(),))
                user = cur.fetchone()

                if user is None:
                    messagebox.showerror("Thất bại", "Sai Mã Nhân Viên hoặc Mật khẩu", parent=self.root)
                    log_action(self.employee_id.get(), "LOGIN_FAIL", "Sai thông tin đăng nhập")
                else:
                    user_type, stored_password = user
                    if stored_password == raw_password:
                        cur.execute("UPDATE employee SET password=? WHERE eid=?", (hashed, self.employee_id.get()))
                        con.commit()
                        log_action(self.employee_id.get(), "LOGIN_MIGRATE", "Tự động chuyển mật khẩu cũ sang SHA-256")
                    elif stored_password != hashed:
                        messagebox.showerror("Thất bại", "Sai Mã Nhân Viên hoặc Mật khẩu", parent=self.root)
                        log_action(self.employee_id.get(), "LOGIN_FAIL", "Sai thông tin đăng nhập")
                        return

                    log_action(self.employee_id.get(), "LOGIN_OK", f"Vai trò: {user_type}")
                    self.root.destroy()
                    # Truyền vai trò sang main.py để phân quyền giao diện.
                    subprocess.Popen([sys.executable, "main.py", user_type])

        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()


if __name__ == "__main__":
    create_db(verbose=False)
    root = Tk()
    obj = loginClass(root)
    root.mainloop()
