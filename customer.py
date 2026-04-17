"""Màn hình quản lý khách hàng và điểm tích luỹ."""

from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import sqlite3
import re
import time
from ui_theme import COLORS, FONTS, apply_ttk_theme
from ui_scale import AutoScale
from search_suggest import SearchSuggest


class customerClass:
    """CRUD khách hàng, tìm kiếm theo tên và SĐT."""
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x550+220+130")
        self.root.title("Hệ thống Quản lý Cửa hàng Tiện lợi | Khách hàng")
        apply_ttk_theme()
        APP_BG = COLORS["bg"]
        CARD_BG = COLORS["surface"]
        CARD_BORDER = COLORS["border"]
        SOFT_BG = COLORS["input_bg"]
        TITLE_FG = COLORS["text"]
        HEADER_BG = COLORS["surface"]
        HEADER_FG = COLORS["text"]
        BTN_GREEN_BG = COLORS["success_soft"]
        BTN_BLUE_BG = COLORS["primary_soft"]
        BTN_RED_BG = COLORS["danger_soft"]
        BTN_YELLOW_BG = COLORS["warning_soft"]
        LBL_FONT = FONTS["body"]
        ENTRY_FONT = FONTS["body"]
        BTN_FONT = FONTS["body_bold"]
        TABLE_HEAD_BG = COLORS["table_head"]
        TABLE_HEAD_FG = COLORS["text"]

        self.root.config(bg=APP_BG)
        self.root.focus_force()

        # Biến trạng thái cho form và tìm kiếm.
        self.var_searchBy = StringVar()
        self.var_searchtxt = StringVar()
        self.var_cid = StringVar()
        self.var_name = StringVar()
        self.var_phone = StringVar()
        self.var_email = StringVar()
        self.var_points = StringVar()
        self.var_points.set("0")

        # Header.
        try:
            self.icon_title = Image.open("Images/images/logo1.png")
            self.icon_title = self.icon_title.resize((50, 50), Image.LANCZOS)
            self.icon_title = ImageTk.PhotoImage(self.icon_title)
            title = Label(self.root, text="  QUẢN LÝ KHÁCH HÀNG", image=self.icon_title, compound=LEFT,
                          font=FONTS["title_large"], bg=HEADER_BG, fg=HEADER_FG, anchor="w", padx=20).place(x=0, y=0,
                                                                                                           relwidth=1,
                                                                                                           height=70)
        except Exception as e:
            title = Label(self.root, text="  QUẢN LÝ KHÁCH HÀNG", font=FONTS["title_large"], bg=HEADER_BG,
                          fg=HEADER_FG, anchor="w", padx=20).place(x=0, y=0, relwidth=1, height=70)
            print("Lỗi logo:", e)

        # Thanh tìm kiếm.
        SearchFrame = Frame(self.root, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER)
        SearchFrame.place(x=250, y=70, width=600, height=50)

        self.cmb_search = ttk.Combobox(SearchFrame, textvariable=self.var_searchBy,
                                       values=("Chọn mục...", "Tên", "SĐT"), state="readonly", justify=CENTER,
                                       font=FONTS["body"])
        self.cmb_search.place(x=30, y=10, width=150, height=30)
        self.cmb_search.current(0)

        self.txt_search = Entry(SearchFrame, textvariable=self.var_searchtxt, font=ENTRY_FONT, bg=SOFT_BG,
                                highlightthickness=1, highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER, bd=0,
                                justify=CENTER)
        self.txt_search.place(x=190, y=10, width=250, height=30)
        self.txt_search.bind("<Return>", lambda e: self.search())

        btn_search = Button(SearchFrame, text="Tìm kiếm", command=self.search, font=BTN_FONT, bg=BTN_BLUE_BG,
                            fg=TITLE_FG, bd=1, relief=SOLID, cursor="hand2")
        btn_search.place(x=450, y=10, width=120, height=30)

        # Form nhập liệu.
        FrameContent = Frame(self.root, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER)
        FrameContent.place(x=50, y=130, width=1000, height=230)

        Label(FrameContent, text="Họ Tên:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_FG).place(x=0, y=10)
        self.txt_name = Entry(FrameContent, textvariable=self.var_name, font=ENTRY_FONT, bg=SOFT_BG,
                              highlightthickness=1, highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER, bd=0)
        self.txt_name.place(x=80, y=10, width=220)

        Label(FrameContent, text="SĐT:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_FG).place(x=340, y=10)
        self.txt_phone = Entry(FrameContent, textvariable=self.var_phone, font=ENTRY_FONT, bg=SOFT_BG,
                               highlightthickness=1, highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER, bd=0)
        self.txt_phone.place(x=400, y=10, width=220)

        Label(FrameContent, text="Email:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_FG).place(x=660, y=10)
        self.txt_email = Entry(FrameContent, textvariable=self.var_email, font=ENTRY_FONT, bg=SOFT_BG,
                               highlightthickness=1, highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER, bd=0)
        self.txt_email.place(x=720, y=10, width=220)

        Label(FrameContent, text="Điểm:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_FG).place(x=0, y=60)
        self.txt_points = Entry(FrameContent, textvariable=self.var_points, font=ENTRY_FONT, bg=SOFT_BG,
                                highlightthickness=1, highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER, bd=0)
        self.txt_points.place(x=80, y=60, width=220)

        Label(FrameContent, text="Địa chỉ:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_FG).place(x=340, y=60)
        self.txt_address = Text(FrameContent, font=ENTRY_FONT, bg=SOFT_BG, highlightthickness=1,
                                highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER, bd=0)
        self.txt_address.place(x=400, y=60, width=540, height=80)

        # Nút thao tác.
        FrameBtns = Frame(FrameContent, bg=CARD_BG)
        FrameBtns.place(x=80, y=160, width=860, height=40)

        btn_save = Button(FrameBtns, text="Lưu", command=self.add, font=BTN_FONT, bg=BTN_GREEN_BG, fg=TITLE_FG,
                          bd=1, relief=SOLID, cursor="hand2").pack(side=LEFT, expand=True, fill=X, padx=5)
        btn_update = Button(FrameBtns, text="Cập nhật", command=self.update, font=BTN_FONT, bg=BTN_BLUE_BG, fg=TITLE_FG,
                            bd=1, relief=SOLID, cursor="hand2").pack(side=LEFT, expand=True, fill=X, padx=5)
        btn_delete = Button(FrameBtns, text="Xóa", command=self.delete, font=BTN_FONT, bg=BTN_RED_BG, fg=TITLE_FG,
                            bd=1, relief=SOLID, cursor="hand2").pack(side=LEFT, expand=True, fill=X, padx=5)
        btn_clear = Button(FrameBtns, text="Làm mới", command=self.clear, font=BTN_FONT, bg=BTN_YELLOW_BG, fg=TITLE_FG,
                           bd=1, relief=SOLID, cursor="hand2").pack(side=LEFT, expand=True, fill=X, padx=5)

        # Bảng danh sách khách hàng.
        cus_frame = Frame(self.root, bd=0, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER)
        cus_frame.place(x=0, y=370, relwidth=1, height=170)

        scrolly = Scrollbar(cus_frame, orient=VERTICAL)
        scrollx = Scrollbar(cus_frame, orient=HORIZONTAL)

        self.CustomerTable = ttk.Treeview(cus_frame, columns=("cid", "name", "phone", "email", "points", "address"),
                                          yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
        scrollx.pack(side=BOTTOM, fill=X)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.config(command=self.CustomerTable.xview)
        scrolly.config(command=self.CustomerTable.yview)

        self.CustomerTable.heading("cid", text="ID", anchor=CENTER)
        self.CustomerTable.heading("name", text="Họ Tên", anchor=CENTER)
        self.CustomerTable.heading("phone", text="SĐT", anchor=CENTER)
        self.CustomerTable.heading("email", text="Email", anchor=CENTER)
        self.CustomerTable.heading("points", text="Điểm", anchor=CENTER)
        self.CustomerTable.heading("address", text="Địa chỉ", anchor=CENTER)
        self.CustomerTable["show"] = "headings"

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=FONTS["table_heading"], background=TABLE_HEAD_BG,
                        foreground=TABLE_HEAD_FG, relief="flat")
        style.configure("Treeview", font=FONTS["table"], background=CARD_BG, fieldbackground=CARD_BG, rowheight=28)
        style.map('Treeview', background=[('selected', COLORS["row_selected"])], foreground=[('selected', TITLE_FG)])

        self.CustomerTable.column("cid", width=60, anchor=CENTER)
        self.CustomerTable.column("name", width=180, anchor=CENTER)
        self.CustomerTable.column("phone", width=120, anchor=CENTER)
        self.CustomerTable.column("email", width=180, anchor=CENTER)
        self.CustomerTable.column("points", width=80, anchor=CENTER)
        self.CustomerTable.column("address", width=300, anchor=CENTER)
        self.CustomerTable.pack(fill=BOTH, expand=1)
        self.CustomerTable.bind("<ButtonRelease-1>", self.get_data)

        self.show()
        self.search_suggest = SearchSuggest(
            self.root,
            self.txt_search,
            self._fetch_search_suggestions,
            self._apply_search_suggestion,
        )
        self.cmb_search.bind("<<ComboboxSelected>>", lambda e: self.search_suggest.hide(), add="+")

        self.scaler = AutoScale(self.root, 1100, 550)

    def _get_search_column(self):
        """Ánh xạ tiêu chí tìm kiếm khách hàng sang cột DB."""
        return {
            "Tên": "name",
            "SĐT": "phone",
        }.get(self.var_searchBy.get())

    def _fetch_search_suggestions(self, term):
        """Lấy gợi ý tìm kiếm khách hàng theo tiền tố."""
        db_column = self._get_search_column()
        if not db_column:
            return []

        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute(
                f"SELECT DISTINCT {db_column} FROM customer "
                f"WHERE {db_column} LIKE ? "
                f"ORDER BY {db_column} LIMIT 8",
                (f"{term}%",)
            )
            return [row[0] for row in cur.fetchall() if row[0]]
        finally:
            con.close()

    def _apply_search_suggestion(self, value):
        """Áp dụng gợi ý và chạy lọc."""
        self.var_searchtxt.set(value)
        self.search()

    def add(self):
        """Thêm khách hàng mới."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if self.var_name.get() == "" or self.var_phone.get() == "":
                messagebox.showerror("Lỗi", "Vui lòng nhập Họ tên và SĐT", parent=self.root)
                return

            if not re.match(r"^\d{10,11}$", self.var_phone.get()):
                messagebox.showerror("Lỗi", "SĐT phải gồm 10-11 chữ số", parent=self.root)
                return

            if self.var_email.get() != "" and not re.match(r"[^@]+@[^@]+\.[^@]+", self.var_email.get()):
                messagebox.showerror("Lỗi", "Email không hợp lệ", parent=self.root)
                return

            try:
                points_val = int(float(self.var_points.get())) if self.var_points.get() != "" else 0
            except Exception:
                messagebox.showerror("Lỗi", "Điểm phải là số", parent=self.root)
                return

            if points_val < 0:
                messagebox.showerror("Lỗi", "Điểm không được âm", parent=self.root)
                return

            cur.execute("Select * from customer WHERE phone = ?", (self.var_phone.get(),))
            row = cur.fetchone()
            if row is not None:
                messagebox.showerror("Lỗi", "SĐT này đã tồn tại", parent=self.root)
                return

            now_str = time.strftime("%d/%m/%Y %H:%M:%S")
            cur.execute(
                "Insert into customer(name, phone, email, address, points, created_at, updated_at) values(?,?,?,?,?,?,?)",
                (
                    self.var_name.get(),
                    self.var_phone.get(),
                    self.var_email.get(),
                    self.txt_address.get('1.0', END),
                    str(points_val),
                    now_str,
                    now_str,
                ))
            con.commit()
            messagebox.showinfo("Thành công", "Thêm khách hàng thành công", parent=self.root)
            self.show()
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def show(self):
        """Tải lại danh sách khách hàng."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute("Select cid, name, phone, email, points, address from customer")
            rows = cur.fetchall()
            self.CustomerTable.delete(*self.CustomerTable.get_children())
            for row in rows:
                self.CustomerTable.insert('', END, values=row)
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hiển thị: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def get_data(self, ev):
        """Đổ dữ liệu khách hàng từ bảng lên form."""
        f = self.CustomerTable.focus()
        content = (self.CustomerTable.item(f))
        row = content['values']
        if not row:
            return
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute("Select cid, name, phone, email, points, address from customer WHERE cid = ?", (row[0],))
            db_row = cur.fetchone()
            if not db_row:
                return
            self.var_cid.set(db_row[0])
            self.var_name.set(db_row[1])
            self.var_phone.set(db_row[2] if db_row[2] is not None else "")
            self.var_email.set(db_row[3] if db_row[3] is not None else "")
            self.var_points.set(db_row[4] if db_row[4] is not None else "0")
            self.txt_address.delete('1.0', END)
            self.txt_address.insert(END, db_row[5] if db_row[5] else "")
        finally:
            con.close()

    def update(self):
        """Cập nhật thông tin khách hàng."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if self.var_cid.get() == "":
                messagebox.showerror("Lỗi", "Vui lòng chọn khách hàng cần cập nhật", parent=self.root)
                return

            if self.var_name.get() == "" or self.var_phone.get() == "":
                messagebox.showerror("Lỗi", "Vui lòng nhập Họ tên và SĐT", parent=self.root)
                return

            if not re.match(r"^\d{10,11}$", self.var_phone.get()):
                messagebox.showerror("Lỗi", "SĐT phải gồm 10-11 chữ số", parent=self.root)
                return

            if self.var_email.get() != "" and not re.match(r"[^@]+@[^@]+\.[^@]+", self.var_email.get()):
                messagebox.showerror("Lỗi", "Email không hợp lệ", parent=self.root)
                return

            try:
                points_val = int(float(self.var_points.get())) if self.var_points.get() != "" else 0
            except Exception:
                messagebox.showerror("Lỗi", "Điểm phải là số", parent=self.root)
                return

            if points_val < 0:
                messagebox.showerror("Lỗi", "Điểm không được âm", parent=self.root)
                return

            cur.execute("Select cid from customer WHERE phone = ? AND cid <> ?", (self.var_phone.get(), self.var_cid.get()))
            if cur.fetchone() is not None:
                messagebox.showerror("Lỗi", "SĐT đã được dùng cho khách khác", parent=self.root)
                return

            now_str = time.strftime("%d/%m/%Y %H:%M:%S")
            cur.execute(
                "update customer set name=?, phone=?, email=?, address=?, points=?, updated_at=? WHERE cid = ?",
                (
                    self.var_name.get(),
                    self.var_phone.get(),
                    self.var_email.get(),
                    self.txt_address.get('1.0', END),
                    str(points_val),
                    now_str,
                    self.var_cid.get(),
                ))
            con.commit()
            messagebox.showinfo("Thành công", "Cập nhật khách hàng thành công", parent=self.root)
            self.show()
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def delete(self):
        """Xoá khách hàng theo ID."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if self.var_cid.get() == "":
                messagebox.showerror("Lỗi", "Vui lòng chọn khách hàng cần xóa", parent=self.root)
                return

            op = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa khách hàng này?", parent=self.root)
            if op:
                cur.execute("delete from customer where cid=?", (self.var_cid.get(),))
                con.commit()
                messagebox.showinfo("Đã xóa", "Xóa khách hàng thành công", parent=self.root)
                self.clear()
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def clear(self):
        """Làm mới form và trạng thái tìm kiếm."""
        self.var_cid.set("")
        self.var_name.set("")
        self.var_phone.set("")
        self.var_email.set("")
        self.var_points.set("0")
        self.var_searchtxt.set("")
        self.var_searchBy.set("Chọn mục...")
        self.txt_address.delete('1.0', END)
        if hasattr(self, "search_suggest"):
            self.search_suggest.hide()
        self.show()

    def search(self):
        """Tìm khách hàng theo tên hoặc SĐT."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if hasattr(self, "search_suggest"):
                self.search_suggest.hide()
            if self.var_searchBy.get() == "Chọn mục...":
                messagebox.showerror("Lỗi", "Vui lòng chọn tiêu chí tìm kiếm", parent=self.root)
            elif self.var_searchtxt.get() == "":
                messagebox.showerror("Lỗi", "Vui lòng nhập nội dung tìm kiếm", parent=self.root)
            else:
                db_column = self._get_search_column()
                search_value = f"%{self.var_searchtxt.get()}%"
                cur.execute(
                    "Select cid, name, phone, email, points, address from customer WHERE " + db_column + " LIKE ?",
                    (search_value,))
                rows = cur.fetchall()
                if len(rows) != 0:
                    self.CustomerTable.delete(*self.CustomerTable.get_children())
                    for row in rows:
                        self.CustomerTable.insert('', END, values=row)
                else:
                    messagebox.showerror("Lỗi", "Không tìm thấy kết quả", parent=self.root)
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()


if __name__ == "__main__":
    root = Tk()
    obj = customerClass(root)
    root.mainloop()
