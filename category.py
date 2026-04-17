"""Màn hình quản lý danh mục sản phẩm."""

from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import sqlite3
from ui_theme import COLORS, FONTS, apply_ttk_theme
from ui_scale import AutoScale
from search_suggest import SearchSuggest


class categoryClass:
    """CRUD danh mục: thêm, hiển thị và xoá."""
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x600+220+130")
        self.root.title("Hệ thống Quản lý Cửa hàng Tiện lợi | Danh mục")
        apply_ttk_theme()
        APP_BG = COLORS["bg"]
        self.root.config(bg=APP_BG)
        self.root.focus_force()

        LBL_FONT = FONTS["body"]
        ENTRY_FONT = FONTS["body"]
        ENTRY_BG = COLORS["input_bg"]
        BTN_FONT = FONTS["body_bold"]
        CARD_BG = COLORS["surface"]
        TITLE_COLOR = COLORS["text"]
        SUBTITLE_COLOR = COLORS["text_muted"]
        HEADER_BG = COLORS["surface"]
        HEADER_FG = COLORS["text"]
        PRIMARY_BTN = COLORS["success_soft"]
        PRIMARY_BTN_ACTIVE = COLORS["success_soft"]
        DANGER_BTN = COLORS["danger_soft"]
        DANGER_BTN_ACTIVE = COLORS["danger_soft"]

        self.var_cat_id = StringVar()
        self.var_name = StringVar()
        self.var_searchtxt = StringVar()

        # Header.
        try:
            self.icon_title = Image.open("Images/images/logo1.png")
            self.icon_title = self.icon_title.resize((50, 50), Image.LANCZOS)
            self.icon_title = ImageTk.PhotoImage(self.icon_title)
            title = Label(self.root, text="  DANH MỤC", image=self.icon_title, compound=LEFT,
                          font=FONTS["title_large"], bg=HEADER_BG, fg=HEADER_FG, anchor="w", padx=20).place(x=0, y=0,
                                                                                                             relwidth=1,
                                                                                                             height=70)
        except Exception as e:
            title = Label(self.root, text="  DANH MỤC", font=FONTS["title_large"], bg=HEADER_BG, fg=HEADER_FG,
                          anchor="w", padx=20).place(x=0, y=0, relwidth=1, height=70)
            print("Lỗi logo:", e)

        # Form nhập liệu bên trái.
        form_frame = Frame(self.root, bg=CARD_BG)
        form_frame.place(x=20, y=100, width=330, height=460)
        Label(form_frame, text="Tạo danh mục", font=FONTS["subtitle"], bg=CARD_BG, fg=TITLE_COLOR).place(x=20, y=20)
        Label(form_frame, text="Nhập tên danh mục mới", font=FONTS["body"], bg=CARD_BG, fg=SUBTITLE_COLOR).place(
            x=20, y=55)

        self.txt_name = Entry(form_frame, textvariable=self.var_name, font=ENTRY_FONT, bg=ENTRY_BG,
                              highlightthickness=1, highlightbackground="#E5E7EB", bd=0)
        self.txt_name.place(x=20, y=90, width=290, height=38)

        # Nút chức năng.
        self.btn_add = Button(form_frame, text="THÊM MỚI", command=self.add, font=BTN_FONT, bg=PRIMARY_BTN, fg="black",
                              activebackground=PRIMARY_BTN_ACTIVE, activeforeground="white", bd=0, cursor="hand2")
        self.btn_add.place(x=20, y=150, width=290, height=40)

        self.btn_delete = Button(form_frame, text="XÓA BỎ", command=self.delete, font=BTN_FONT, bg=DANGER_BTN, fg="black",
                                 activebackground=DANGER_BTN_ACTIVE, activeforeground="white", bd=0, cursor="hand2")
        self.btn_delete.place(x=20, y=200, width=290, height=40)

        # Bảng danh sách bên phải.
        cat_frame = Frame(self.root, bd=0, bg=CARD_BG)
        cat_frame.place(x=370, y=100, width=710, height=460)
        header_frame = Frame(cat_frame, bg=CARD_BG)
        header_frame.pack(side=TOP, fill=X, padx=20, pady=(15, 10))

        Label(header_frame, text="Danh sách hiện có", font=FONTS["body_bold"], bg=CARD_BG, fg=TITLE_COLOR).pack(
            side=LEFT)

        self.txt_search = Entry(header_frame, textvariable=self.var_searchtxt, font=ENTRY_FONT, bg=ENTRY_BG,
                                highlightthickness=1, highlightbackground="#E5E7EB", bd=0, width=24)
        self.txt_search.pack(side=LEFT, padx=(20, 8), ipady=4)
        self.txt_search.bind("<Return>", lambda e: self.search())

        Button(header_frame, text="Tìm", command=self.search, font=BTN_FONT, bg=PRIMARY_BTN, fg="black",
               activebackground=PRIMARY_BTN_ACTIVE, activeforeground="white", bd=0, cursor="hand2").pack(
            side=LEFT, padx=(0, 8))
        Button(header_frame, text="Tất cả", command=self.clear_search, font=BTN_FONT, bg=COLORS["warning_soft"],
               fg="black", activebackground=COLORS["warning_soft"], activeforeground="white", bd=0,
               cursor="hand2").pack(side=LEFT)

        scrolly = Scrollbar(cat_frame, orient=VERTICAL)
        scrollx = Scrollbar(cat_frame, orient=HORIZONTAL)

        self.category_table = ttk.Treeview(cat_frame, columns=("cid", "name"), show="headings", yscrollcommand=scrolly.set,
                                           xscrollcommand=scrollx.set)
        scrollx.pack(side=BOTTOM, fill=X)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.config(command=self.category_table.xview)
        scrolly.config(command=self.category_table.yview)

        self.category_table.heading("cid", text="Mã ID", anchor=CENTER)
        self.category_table.heading("name", text="Tên Danh mục", anchor=CENTER)
        self.category_table["show"] = "headings"

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=FONTS["table_heading"], background=COLORS["table_head"],
                        foreground=COLORS["text"], relief="flat")
        style.configure("Treeview", font=FONTS["table"], background=COLORS["surface"],
                        fieldbackground=COLORS["surface"], rowheight=34, borderwidth=0)
        style.map('Treeview', background=[('selected', COLORS["row_selected"])],
                  foreground=[('selected', COLORS["text"])])

        self.category_table.column("cid", width=100, anchor=CENTER)
        self.category_table.column("name", width=380, anchor=CENTER)
        self.category_table.pack(fill=BOTH, expand=1, padx=20, pady=(0, 20))

        self.category_table.bind("<ButtonRelease-1>", self.get_data)

        try:
            self.txt_name.bind('<Return>', lambda e: self.add())
        except Exception as e:
            print("Lỗi binding:", e)

        self.show()
        self.search_suggest = SearchSuggest(
            self.root,
            self.txt_search,
            self._fetch_search_suggestions,
            self._apply_search_suggestion,
        )

        self.scaler = AutoScale(self.root, 1100, 600)

    def _fetch_search_suggestions(self, term):
        """Gợi ý tên danh mục theo tiền tố."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute(
                "SELECT DISTINCT name FROM category "
                "WHERE name LIKE ? "
                "ORDER BY name LIMIT 8",
                (f"{term}%",)
            )
            return [row[0] for row in cur.fetchall() if row[0]]
        finally:
            con.close()

    def _apply_search_suggestion(self, value):
        """Đổ gợi ý và chạy lọc danh mục."""
        self.var_searchtxt.set(value)
        self.search()

    def add(self):
        """Thêm danh mục mới."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if self.var_name.get() == "":
                messagebox.showerror("Lỗi", "Vui lòng nhập tên danh mục", parent=self.root)
            else:
                cur.execute("Select * from category WHERE name = ?", (self.var_name.get(),))
                row = cur.fetchone()
                if row != None:
                    messagebox.showerror("Lỗi", "Danh mục này đã tồn tại", parent=self.root)
                else:
                    cur.execute("Insert into category(name) values(?)", (self.var_name.get(),))
                    con.commit()
                    messagebox.showinfo("Thành công", "Thêm danh mục thành công", parent=self.root)
                    self.show()
                    self.var_name.set("")
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def show(self):
        """Tải lại danh sách danh mục."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute("Select * from category")
            rows = cur.fetchall()
            self.category_table.delete(*self.category_table.get_children())
            for row in rows:
                self.category_table.insert('', END, values=row)
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hiển thị: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def get_data(self, ev):
        """Lấy ID danh mục khi click vào bảng."""
        f = self.category_table.focus()
        content = (self.category_table.item(f))
        row = content['values']
        if not row:
            return
        self.var_cat_id.set(row[0])
        self.var_name.set(row[1])

    def clear_search(self):
        """Trả bảng danh mục về trạng thái đầy đủ."""
        self.var_searchtxt.set("")
        if hasattr(self, "search_suggest"):
            self.search_suggest.hide()
        self.show()

    def search(self):
        """Lọc danh mục theo tên."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if hasattr(self, "search_suggest"):
                self.search_suggest.hide()
            term = self.var_searchtxt.get().strip()
            if term == "":
                self.show()
                return

            cur.execute("SELECT * FROM category WHERE name LIKE ? ORDER BY name", (f"%{term}%",))
            rows = cur.fetchall()
            self.category_table.delete(*self.category_table.get_children())
            if rows:
                for row in rows:
                    self.category_table.insert('', END, values=row)
            else:
                messagebox.showerror("Lỗi", "Không tìm thấy danh mục", parent=self.root)
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def delete(self):
        """Xoá danh mục theo ID đã chọn."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if self.var_cat_id.get() == "":
                messagebox.showerror("Lỗi", "Vui lòng chọn danh mục cần xóa", parent=self.root)
            else:
                cur.execute("Select * from category WHERE cid = ?", (self.var_cat_id.get(),))
                row = cur.fetchone()
                if row == None:
                    messagebox.showerror("Lỗi", "Danh mục không hợp lệ", parent=self.root)
                else:
                    op = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa?", parent=self.root)
                    if op == True:
                        cur.execute("delete from category where cid=?", (self.var_cat_id.get(),))
                        con.commit()
                        messagebox.showinfo("Đã xóa", "Xóa danh mục thành công", parent=self.root)
                        self.show()
                        self.var_cat_id.set("")
                        self.var_name.set("")
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()


if __name__ == "__main__":
    root = Tk()
    obj = categoryClass(root)
    root.mainloop()
