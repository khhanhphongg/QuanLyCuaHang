"""Màn hình quản lý nhà cung cấp."""

from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import sqlite3
from ui_theme import COLORS, FONTS, apply_ttk_theme
from ui_scale import AutoScale
from search_suggest import SearchSuggest


class supplierClass:
    """CRUD nhà cung cấp và tìm kiếm theo mã hóa đơn."""
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x550+220+130")
        self.root.title("Hệ thống Quản lý Cửa hàng Tiện lợi | Nhà cung cấp")
        apply_ttk_theme()
        APP_BG = COLORS["bg"]
        CARD_BG = COLORS["surface"]
        CARD_BORDER = COLORS["border"]
        SOFT_BG = COLORS["input_bg"]
        TITLE_BG = COLORS["surface"]
        TITLE_FG = COLORS["text"]
        HEADER_BG = COLORS["surface"]
        HEADER_FG = COLORS["text"]
        LABEL_FG = COLORS["text"]
        BTN_GREEN_BG = COLORS["success_soft"]
        BTN_GREEN_FG = COLORS["text"]
        BTN_GREEN_ACTIVE = COLORS["success_soft"]
        BTN_BLUE_BG = COLORS["primary_soft"]
        BTN_BLUE_FG = COLORS["text"]
        BTN_BLUE_ACTIVE = COLORS["primary_soft"]
        BTN_RED_BG = COLORS["danger_soft"]
        BTN_RED_FG = COLORS["text"]
        BTN_RED_ACTIVE = COLORS["danger_soft"]
        BTN_YELLOW_BG = COLORS["warning_soft"]
        BTN_YELLOW_FG = COLORS["text"]
        BTN_YELLOW_ACTIVE = COLORS["warning_soft"]
        LBL_FONT = FONTS["body"]
        ENTRY_FONT = FONTS["body"]
        ENTRY_BG = SOFT_BG
        BTN_FONT = FONTS["body_bold"]
        TABLE_HEAD_BG = COLORS["table_head"]
        TABLE_HEAD_FG = COLORS["text"]

        self.root.config(bg=APP_BG)
        self.root.focus_force()

        self.var_searchBy = StringVar()
        self.var_searchtxt = StringVar()
        self.var_sup_invoice = StringVar()
        self.var_name = StringVar()
        self.var_contact = StringVar()

        # Header.
        try:
            self.icon_title = Image.open("Images/images/logo1.png")
            self.icon_title = self.icon_title.resize((50, 50), Image.LANCZOS)
            self.icon_title = ImageTk.PhotoImage(self.icon_title)
            title = Label(self.root, text="  QUẢN LÝ NHÀ CUNG CẤP", image=self.icon_title, compound=LEFT,
                          font=FONTS["title_large"], bg=HEADER_BG, fg=HEADER_FG, anchor="w", padx=20).place(x=0, y=0,
                                                                                                             relwidth=1,
                                                                                                             height=70)
        except Exception as e:
            title = Label(self.root, text="  QUẢN LÝ NHÀ CUNG CẤP", font=FONTS["title_large"], bg=HEADER_BG,
                          fg=HEADER_FG, anchor="w", padx=20).place(x=0, y=0, relwidth=1, height=70)
            print("Lỗi logo:", e)

        # Bố cục tổng.
        BodyFrame = Frame(self.root, bg=APP_BG)
        BodyFrame.place(x=40, y=70, width=1020, height=450)

        BodyFrame.grid_rowconfigure(0, weight=1)
        BodyFrame.grid_columnconfigure(0, weight=3, uniform="body")
        BodyFrame.grid_columnconfigure(1, weight=2, uniform="body")

        LeftFrame = Frame(BodyFrame, bg=APP_BG)
        LeftFrame.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        LeftFrame.grid_rowconfigure(0, weight=1)
        LeftFrame.grid_columnconfigure(0, weight=1)

        RightFrame = Frame(BodyFrame, bg=APP_BG)
        RightFrame.grid(row=0, column=1, sticky="nsew")
        RightFrame.grid_columnconfigure(0, weight=1)
        RightFrame.grid_rowconfigure(0, weight=0)
        RightFrame.grid_rowconfigure(1, weight=1)

        # Khung tìm kiếm.
        SearchFrame = Frame(RightFrame, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER, height=50)
        SearchFrame.grid(row=0, column=0, sticky="ew")
        SearchFrame.grid_propagate(False)

        self.cmb_search = ttk.Combobox(
            SearchFrame,
            textvariable=self.var_searchBy,
            values=("Chọn mục...", "Mã HĐ", "Tên NCC", "SĐT"),
            state="readonly",
            justify=CENTER,
            font=ENTRY_FONT
        )
        self.cmb_search.place(x=0, y=8, width=110, height=30)
        self.cmb_search.current(0)

        self.txt_search = Entry(SearchFrame, textvariable=self.var_searchtxt, font=ENTRY_FONT, bg=ENTRY_BG,
                                highlightthickness=1, highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER,
                                bd=0)
        self.txt_search.place(x=120, y=8, width=150, height=30)

        btn_search = Button(SearchFrame, text="Tìm kiếm", command=self.search, font=BTN_FONT, bg=BTN_BLUE_BG,
                            fg=BTN_BLUE_FG, activebackground=BTN_BLUE_ACTIVE, activeforeground=BTN_BLUE_FG,
                            bd=1, relief=SOLID, cursor="hand2")
        btn_search.place(x=280, y=8, width=100, height=30)

        # Form nhập liệu.
        FrameContent = Frame(LeftFrame, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER, height=450)
        FrameContent.grid(row=0, column=0, sticky="nsew")
        FrameContent.grid_propagate(False)

        FORM_TOP_PAD = 12

        Label(FrameContent, text="Mã Hóa đơn:", font=LBL_FONT, bg=CARD_BG, fg=LABEL_FG).place(x=0, y=FORM_TOP_PAD)
        self.txt_invoice = Entry(FrameContent, textvariable=self.var_sup_invoice, font=ENTRY_FONT, bg=ENTRY_BG,
                                 highlightthickness=1, highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER,
                                 bd=0)
        self.txt_invoice.place(x=130, y=FORM_TOP_PAD, width=400)

        Label(FrameContent, text="Tên Nhà CC:", font=LBL_FONT, bg=CARD_BG, fg=LABEL_FG).place(x=0, y=50 + FORM_TOP_PAD)
        self.txt_name = Entry(FrameContent, textvariable=self.var_name, font=ENTRY_FONT, bg=ENTRY_BG,
                              highlightthickness=1, highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER,
                              bd=0)
        self.txt_name.place(x=130, y=50 + FORM_TOP_PAD, width=400)

        Label(FrameContent, text="Liên hệ (SĐT):", font=LBL_FONT, bg=CARD_BG, fg=LABEL_FG).place(x=0, y=100 + FORM_TOP_PAD)
        self.txt_contact = Entry(FrameContent, textvariable=self.var_contact, font=ENTRY_FONT, bg=ENTRY_BG,
                                 highlightthickness=1, highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER,
                                 bd=0)
        self.txt_contact.place(x=130, y=100 + FORM_TOP_PAD, width=400)

        Label(FrameContent, text="Mô tả/Ghi chú:", font=LBL_FONT, bg=CARD_BG, fg=LABEL_FG).place(x=0, y=150 + FORM_TOP_PAD)
        self.txt_desc = Text(FrameContent, font=ENTRY_FONT, bg=ENTRY_BG, highlightthickness=1,
                             highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER, bd=0)
        self.txt_desc.place(x=130, y=150 + FORM_TOP_PAD, width=400, height=100)

        # Nút thao tác.
        FrameBtns = Frame(FrameContent, bg=CARD_BG)
        FrameBtns.place(x=130, y=270 + FORM_TOP_PAD, width=400, height=40)

        self.btn_save = Button(FrameBtns, text="Lưu", command=self.add, font=BTN_FONT, bg=BTN_GREEN_BG,
                               fg=BTN_GREEN_FG, activebackground=BTN_GREEN_ACTIVE,
                               activeforeground=BTN_GREEN_FG, bd=1, relief=SOLID, cursor="hand2")
        self.btn_save.pack(side=LEFT, expand=True, fill=X, padx=5)

        btn_update = Button(FrameBtns, text="Cập nhật", command=self.update, font=BTN_FONT, bg=BTN_BLUE_BG,
                            fg=BTN_BLUE_FG, activebackground=BTN_BLUE_ACTIVE, activeforeground=BTN_BLUE_FG,
                            bd=1, relief=SOLID, cursor="hand2").pack(side=LEFT, expand=True, fill=X, padx=5)
        btn_delete = Button(FrameBtns, text="Xóa", command=self.delete, font=BTN_FONT, bg=BTN_RED_BG, fg=BTN_RED_FG,
                            activebackground=BTN_RED_ACTIVE, activeforeground=BTN_RED_FG, bd=1, relief=SOLID,
                            cursor="hand2").pack(side=LEFT, expand=True, fill=X, padx=5)
        btn_clear = Button(FrameBtns, text="Làm mới", command=self.clear, font=BTN_FONT, bg=BTN_YELLOW_BG,
                           fg=BTN_YELLOW_FG, activebackground=BTN_YELLOW_ACTIVE,
                           activeforeground=BTN_YELLOW_FG, bd=1, relief=SOLID, cursor="hand2").pack(side=LEFT,
                                                                                                    expand=True,
                                                                                                    fill=X,
                                                                                                    padx=5)

        # Bảng danh sách nhà cung cấp.
        emp_frame = Frame(RightFrame, bd=0, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER)
        emp_frame.grid(row=1, column=0, sticky="nsew", pady=(10, 0))

        scrolly = Scrollbar(emp_frame, orient=VERTICAL)
        scrollx = Scrollbar(emp_frame, orient=HORIZONTAL)
        self.SupplierTable = ttk.Treeview(emp_frame, columns=("invoice", "name", "contact", "desc"),
                                          yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
        scrollx.pack(side=BOTTOM, fill=X)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.config(command=self.SupplierTable.xview)
        scrolly.config(command=self.SupplierTable.yview)
        self.SupplierTable.heading("invoice", text="Mã HĐ", anchor=CENTER)
        self.SupplierTable.heading("name", text="Tên Nhà CC", anchor=W)
        self.SupplierTable.heading("contact", text="Liên hệ", anchor=CENTER)
        self.SupplierTable.heading("desc", text="Mô tả", anchor=W)
        self.SupplierTable["show"] = "headings"

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=FONTS["table_heading"], background=TABLE_HEAD_BG,
                        foreground=TABLE_HEAD_FG, relief="flat")
        style.configure("Treeview", font=FONTS["table"], background=CARD_BG, fieldbackground=CARD_BG, rowheight=28)
        style.map('Treeview', background=[('selected', COLORS["row_selected"])], foreground=[('selected', TITLE_FG)])

        self.SupplierTable.column("invoice", anchor=CENTER)
        self.SupplierTable.column("name", anchor=W)
        self.SupplierTable.column("contact", anchor=CENTER)
        self.SupplierTable.column("desc", anchor=W)
        self.SupplierTable.pack(fill=BOTH, expand=1)
        self.SupplierTable.bind("<ButtonRelease-1>", self.get_data)

        # Điều hướng form bằng Enter và mũi tên.
        try:
            self.txt_invoice.bind('<Return>', lambda e: self.txt_name.focus())
            self.txt_invoice.bind('<Down>', lambda e: self.txt_name.focus())
            self.txt_invoice.bind('<Right>', lambda e: self.cmb_search.focus())

            self.txt_name.bind('<Return>', lambda e: self.txt_contact.focus())
            self.txt_name.bind('<Down>', lambda e: self.txt_contact.focus())
            self.txt_name.bind('<Up>', lambda e: self.txt_invoice.focus())

            self.txt_contact.bind('<Return>', lambda e: self.txt_desc.focus())
            self.txt_contact.bind('<Down>', lambda e: self.txt_desc.focus())
            self.txt_contact.bind('<Up>', lambda e: self.txt_name.focus())

            self.txt_desc.bind('<Down>', lambda e: self.btn_save.focus())
            self.txt_desc.bind('<Up>', lambda e: self.txt_contact.focus())

            self.txt_search.bind('<Return>', lambda e: self.search())
            self.txt_search.bind('<Left>', lambda e: self.cmb_search.focus())

        except Exception as e:
            print("Lỗi binding:", e)

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
        """Ánh xạ tiêu chí tìm kiếm NCC sang cột DB."""
        return {
            "Mã HĐ": "invoice",
            "Tên NCC": "name",
            "SĐT": "contact",
        }.get(self.var_searchBy.get())

    def _fetch_search_suggestions(self, term):
        """Lấy gợi ý tìm kiếm NCC theo tiền tố."""
        db_column = self._get_search_column()
        if not db_column:
            return []

        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute(
                f"SELECT DISTINCT {db_column} FROM supplier "
                f"WHERE {db_column} LIKE ? "
                f"ORDER BY {db_column} LIMIT 8",
                (f"{term}%",)
            )
            return [row[0] for row in cur.fetchall() if row[0]]
        finally:
            con.close()

    def _apply_search_suggestion(self, value):
        """Điền gợi ý được chọn và chạy lọc."""
        self.var_searchtxt.set(value)
        self.search()

    def add(self):
        """Thêm nhà cung cấp mới."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if self.var_sup_invoice.get() == "":
                messagebox.showerror("Lỗi", "Vui lòng nhập Mã Hóa Đơn", parent=self.root)
            else:
                cur.execute("Select * from supplier WHERE invoice = ?", (self.var_sup_invoice.get(),))
                row = cur.fetchone()
                if row != None:
                    messagebox.showerror("Lỗi", "Mã Hóa Đơn này đã tồn tại, hãy thử mã khác", parent=self.root)
                else:
                    cur.execute("Insert into supplier(invoice,name,contact,desc) values(?,?,?,?)", (
                        self.var_sup_invoice.get(),
                        self.var_name.get(),
                        self.var_contact.get(),
                        self.txt_desc.get('1.0', END),
                    ))
                    con.commit()
                    messagebox.showinfo("Thành công", "Thêm Nhà cung cấp thành công", parent=self.root)
                    self.show()
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def show(self):
        """Hiển thị danh sách nhà cung cấp."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute("Select * from supplier")
            rows = cur.fetchall()
            self.SupplierTable.delete(*self.SupplierTable.get_children())
            for row in rows:
                self.SupplierTable.insert('', END, values=row)
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hiển thị: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def get_data(self, ev):
        """Đổ dữ liệu từ bảng lên form."""
        f = self.SupplierTable.focus()
        content = (self.SupplierTable.item(f))
        row = content['values']
        if not row:
            return
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute("Select invoice, name, contact, desc from supplier WHERE invoice = ?", (row[0],))
            db_row = cur.fetchone()
            if not db_row:
                return
            self.var_sup_invoice.set(db_row[0])
            self.var_name.set(db_row[1])
            self.var_contact.set(db_row[2] if db_row[2] is not None else "")
            self.txt_desc.delete('1.0', END)
            self.txt_desc.insert(END, db_row[3] if db_row[3] else "")
        finally:
            con.close()

    def update(self):
        """Cập nhật nhà cung cấp."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if self.var_sup_invoice.get() == "":
                messagebox.showerror("Lỗi", "Cần nhập Mã Hóa Đơn", parent=self.root)
            else:
                cur.execute("Select * from supplier WHERE invoice = ?", (self.var_sup_invoice.get(),))
                row = cur.fetchone()
                if row == None:
                    messagebox.showerror("Lỗi", "Mã Hóa Đơn không tồn tại", parent=self.root)
                else:
                    cur.execute("update supplier set name=?,contact=?,desc=? WHERE invoice = ?", (
                        self.var_name.get(),
                        self.var_contact.get(),
                        self.txt_desc.get('1.0', END),
                        self.var_sup_invoice.get(),
                    ))
                    con.commit()
                    messagebox.showinfo("Thành công", "Cập nhật dữ liệu thành công", parent=self.root)
                    self.show()
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def delete(self):
        """Xoá nhà cung cấp theo mã hóa đơn."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if self.var_sup_invoice.get() == "":
                messagebox.showerror("Lỗi", "Cần nhập Mã Hóa Đơn", parent=self.root)
            else:
                cur.execute("Select * from supplier WHERE invoice = ?", (self.var_sup_invoice.get(),))
                row = cur.fetchone()
                if row == None:
                    messagebox.showerror("Lỗi", "Mã Hóa Đơn không tồn tại", parent=self.root)
                else:
                    op = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa nhà cung cấp này?", parent=self.root)
                    if op == True:
                        cur.execute("delete from supplier where invoice=?", (self.var_sup_invoice.get(),))
                        con.commit()
                        messagebox.showinfo("Đã xóa", "Xóa thành công", parent=self.root)
                        self.clear()
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def clear(self):
        """Làm mới form và kết quả tìm kiếm."""
        self.var_sup_invoice.set("")
        self.var_name.set("")
        self.var_contact.set("")
        self.txt_desc.delete('1.0', END)
        self.var_searchtxt.set("")
        self.var_searchBy.set("Chọn mục...")
        if hasattr(self, "search_suggest"):
            self.search_suggest.hide()
        self.show()

    def search(self):
        """Tìm nhà cung cấp theo mã hóa đơn."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if hasattr(self, "search_suggest"):
                self.search_suggest.hide()
            if self.var_searchBy.get() == "Chọn mục...":
                messagebox.showerror("Lỗi", "Vui lòng chọn tiêu chí tìm kiếm", parent=self.root)
            elif self.var_searchtxt.get() == "":
                messagebox.showerror("Lỗi", "Vui lòng nhập nội dung cần tìm", parent=self.root)
            else:
                db_column = self._get_search_column()
                cur.execute(f"Select * from supplier WHERE {db_column} LIKE ?", (f"%{self.var_searchtxt.get()}%",))
                rows = cur.fetchall()
                if rows:
                    self.SupplierTable.delete(*self.SupplierTable.get_children())
                    for row in rows:
                        self.SupplierTable.insert('', END, values=row)
                else:
                    messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu", parent=self.root)
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()


if __name__ == "__main__":
    root = Tk()
    obj = supplierClass(root)
    root.mainloop()
