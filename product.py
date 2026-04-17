"""Màn hình quản lý sản phẩm và tồn kho."""

import csv
import os
import time
from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from ui_theme import COLORS, FONTS, apply_ttk_theme
from ui_scale import AutoScale
from audit_log import log_action
from search_suggest import SearchSuggest


class productClass:
    """CRUD sản phẩm, lọc theo danh mục/nhà cung cấp."""
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x600+220+130")
        self.root.title("Hệ thống Quản lý Cửa hàng Tiện lợi | Sản phẩm")
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
        PRIMARY_BTN = COLORS["primary_soft"]
        PRIMARY_BTN_ACTIVE = COLORS["primary_soft"]
        ACCENT_BTN = COLORS["success_soft"]
        ACCENT_BTN_ACTIVE = COLORS["success_soft"]
        WARNING_BTN = COLORS["warning_soft"]
        WARNING_BTN_ACTIVE = COLORS["warning_soft"]
        DANGER_BTN = COLORS["danger_soft"]
        DANGER_BTN_ACTIVE = COLORS["danger_soft"]

        # Biến trạng thái cho tìm kiếm và form.
        self.var_searchBy = StringVar()
        self.var_searchtxt = StringVar()
        self.var_pid = StringVar()
        self.var_cat = StringVar()
        self.var_sup = StringVar()
        self.cat_list = []
        self.sup_list = []
        self.var_name = StringVar()
        self.var_price = StringVar()
        self.var_qty = StringVar()
        self.var_status = StringVar()
        self.var_barcode = StringVar()
        self.var_cost_price = StringVar()
        self.var_min_qty = StringVar()
        self.var_unit = StringVar()
        self.var_description = StringVar()

        self.fetch_cat_sup()

        # Header.
        try:
            self.icon_title = Image.open("Images/images/logo1.png")
            self.icon_title = self.icon_title.resize((50, 50), Image.LANCZOS)
            self.icon_title = ImageTk.PhotoImage(self.icon_title)
            title = Label(self.root, text="  SẢN PHẨM", image=self.icon_title, compound=LEFT,
                          font=FONTS["title_large"], bg=HEADER_BG, fg=HEADER_FG, anchor="w", padx=20).place(x=0, y=0,
                                                                                                             relwidth=1,
                                                                                                             height=70)
        except Exception as e:
            title = Label(self.root, text="  SẢN PHẨM", font=FONTS["title_large"], bg=HEADER_BG, fg=HEADER_FG,
                          anchor="w", padx=20).place(x=0, y=0, relwidth=1, height=70)
            print("Lỗi logo:", e)

        self.root.geometry("1200x750+150+50")

        # Khung nội dung chính.
        product_Frame = Frame(self.root, bd=0, bg=CARD_BG)
        product_Frame.place(x=20, y=100, width=1160, height=340)

        # Thanh tìm kiếm.
        SearchFrame = Frame(product_Frame, bg=CARD_BG)
        SearchFrame.place(x=20, y=15, width=1120, height=40)

        self.cmb_search = ttk.Combobox(SearchFrame, textvariable=self.var_searchBy,
                                       values=("Chọn mục...", "Tên SP", "Danh mục", "Nhà cung cấp", "Barcode"), state="readonly",
                                       justify=CENTER, font=ENTRY_FONT)
        self.cmb_search.place(x=0, y=0, width=160, height=30)
        self.cmb_search.current(0)

        self.txt_search = Entry(SearchFrame, textvariable=self.var_searchtxt, font=ENTRY_FONT, bg=ENTRY_BG,
                                highlightthickness=1, bd=0)
        self.txt_search.place(x=170, y=0, width=350, height=30)
        self.txt_search.bind("<Return>", lambda e: self.search())

        btn_search = Button(SearchFrame, text="Tìm kiếm", command=self.search, font=BTN_FONT, bg=PRIMARY_BTN, fg="black",
                            activebackground=PRIMARY_BTN_ACTIVE, activeforeground="white", bd=0, cursor="hand2")
        btn_search.place(x=530, y=0, width=110, height=30)

        btn_show_all = Button(SearchFrame, text="Tất cả", command=self.show, font=BTN_FONT, bg=WARNING_BTN, fg="black",
                              activebackground=WARNING_BTN_ACTIVE, activeforeground="white", bd=0, cursor="hand2")
        btn_show_all.place(x=650, y=0, width=90, height=30)

        btn_export = Button(SearchFrame, text="📥 Xuất CSV", command=self.export_csv, font=BTN_FONT, bg=COLORS["primary_soft"], fg="black",
                            bd=0, cursor="hand2")
        btn_export.place(x=950, y=0, width=140, height=30)

        ROW_H = 40
        # Form nhập liệu: cột 1.
        Label(product_Frame, text="Danh mục:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_COLOR).place(x=20, y=60)
        Label(product_Frame, text="Nhà cung cấp:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_COLOR).place(x=20, y=60+ROW_H)
        Label(product_Frame, text="Tên SP:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_COLOR).place(x=20, y=60+ROW_H*2)
        Label(product_Frame, text="Barcode:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_COLOR).place(x=20, y=60+ROW_H*3)
        Label(product_Frame, text="Mô tả:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_COLOR).place(x=20, y=60+ROW_H*4)

        self.cmb_cat = ttk.Combobox(product_Frame, textvariable=self.var_cat, values=self.cat_list, state="readonly",
                                    justify=CENTER, font=ENTRY_FONT)
        self.cmb_cat.place(x=130, y=60, width=200)
        self.cmb_cat.current(0)

        self.cmb_sup = ttk.Combobox(product_Frame, textvariable=self.var_sup, values=self.sup_list, state="readonly",
                                    justify=CENTER, font=ENTRY_FONT)
        self.cmb_sup.place(x=130, y=60+ROW_H, width=200)
        self.cmb_sup.current(0)

        txt_name = Entry(product_Frame, textvariable=self.var_name, font=ENTRY_FONT, bg=ENTRY_BG, highlightthickness=1, bd=0)
        txt_name.place(x=130, y=60+ROW_H*2, width=200)

        txt_barcode = Entry(product_Frame, textvariable=self.var_barcode, font=ENTRY_FONT, bg=ENTRY_BG, highlightthickness=1, bd=0)
        txt_barcode.place(x=130, y=60+ROW_H*3, width=200)

        txt_desc = Entry(product_Frame, textvariable=self.var_description, font=ENTRY_FONT, bg=ENTRY_BG, highlightthickness=1, bd=0)
        txt_desc.place(x=130, y=60+ROW_H*4, width=200)

        # Form nhập liệu: cột 2.
        COL2_X = 360
        Label(product_Frame, text="Giá bán:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_COLOR).place(x=COL2_X, y=60)
        Label(product_Frame, text="Giá nhập:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_COLOR).place(x=COL2_X, y=60+ROW_H)
        Label(product_Frame, text="Số lượng:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_COLOR).place(x=COL2_X, y=60+ROW_H*2)
        Label(product_Frame, text="Tồn kho min:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_COLOR).place(x=COL2_X, y=60+ROW_H*3)

        txt_price = Entry(product_Frame, textvariable=self.var_price, font=ENTRY_FONT, bg=ENTRY_BG, highlightthickness=1, bd=0)
        txt_price.place(x=COL2_X+110, y=60, width=160)

        txt_cost = Entry(product_Frame, textvariable=self.var_cost_price, font=ENTRY_FONT, bg=ENTRY_BG, highlightthickness=1, bd=0)
        txt_cost.place(x=COL2_X+110, y=60+ROW_H, width=160)

        txt_qty = Entry(product_Frame, textvariable=self.var_qty, font=ENTRY_FONT, bg=ENTRY_BG, highlightthickness=1, bd=0)
        txt_qty.place(x=COL2_X+110, y=60+ROW_H*2, width=160)

        txt_min_qty = Entry(product_Frame, textvariable=self.var_min_qty, font=ENTRY_FONT, bg=ENTRY_BG, highlightthickness=1, bd=0)
        txt_min_qty.place(x=COL2_X+110, y=60+ROW_H*3, width=160)

        # Form nhập liệu: cột 3.
        COL3_X = 660
        Label(product_Frame, text="Trạng thái:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_COLOR).place(x=COL3_X, y=60)
        Label(product_Frame, text="Đơn vị:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_COLOR).place(x=COL3_X, y=60+ROW_H)

        cmb_status = ttk.Combobox(product_Frame, textvariable=self.var_status, values=("Đang bán", "Ngừng bán"),
                                  state="readonly", justify=CENTER, font=ENTRY_FONT)
        cmb_status.place(x=COL3_X+100, y=60, width=160)
        cmb_status.current(0)

        cmb_unit = ttk.Combobox(product_Frame, textvariable=self.var_unit,
                                values=("Cái", "Hộp", "Kg", "Lít", "Gói", "Chai", "Lon", "Túi", "Thùng"),
                                state="readonly", justify=CENTER, font=ENTRY_FONT)
        cmb_unit.place(x=COL3_X+100, y=60+ROW_H, width=160)
        cmb_unit.current(0)

        # Nút thao tác.
        FrameBtns = Frame(product_Frame, bg=CARD_BG)
        FrameBtns.place(x=20, y=275, width=900, height=40)

        Button(FrameBtns, text="Lưu", command=self.add, font=BTN_FONT, bg=ACCENT_BTN, fg="black",
               activebackground=ACCENT_BTN_ACTIVE, activeforeground="white", bd=0, cursor="hand2").pack(
            side=LEFT, expand=True, fill=X, padx=5)
        Button(FrameBtns, text="Cập nhật", command=self.update, font=BTN_FONT, bg=PRIMARY_BTN, fg="black",
               activebackground=PRIMARY_BTN_ACTIVE, activeforeground="white", bd=0, cursor="hand2").pack(
            side=LEFT, expand=True, fill=X, padx=5)
        Button(FrameBtns, text="Xóa", command=self.delete, font=BTN_FONT, bg=DANGER_BTN, fg="black",
               activebackground=DANGER_BTN_ACTIVE, activeforeground="white", bd=0, cursor="hand2").pack(
            side=LEFT, expand=True, fill=X, padx=5)
        Button(FrameBtns, text="Làm mới", command=self.clear, font=BTN_FONT, bg=WARNING_BTN, fg="black",
               activebackground=WARNING_BTN_ACTIVE, activeforeground="white", bd=0, cursor="hand2").pack(
            side=LEFT, expand=True, fill=X, padx=5)

        # Bảng sản phẩm.
        p_frame = Frame(self.root, bd=0, bg=CARD_BG)
        p_frame.place(x=20, y=450, width=1160, height=280)

        scrolly = Scrollbar(p_frame, orient=VERTICAL)
        scrollx = Scrollbar(p_frame, orient=HORIZONTAL)

        self.product_Table = ttk.Treeview(p_frame,
                                          columns=("pid", "Category", "Supplier", "name", "price", "qty", "status", "barcode", "cost_price", "min_qty", "unit"),
                                          yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
        scrollx.pack(side=BOTTOM, fill=X)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.config(command=self.product_Table.xview)
        scrolly.config(command=self.product_Table.yview)

        self.product_Table.heading("pid", text="ID", anchor=CENTER)
        self.product_Table.heading("Category", text="Danh mục", anchor=CENTER)
        self.product_Table.heading("Supplier", text="NCC", anchor=CENTER)
        self.product_Table.heading("name", text="Tên SP", anchor=CENTER)
        self.product_Table.heading("price", text="Giá bán", anchor=CENTER)
        self.product_Table.heading("qty", text="SL", anchor=CENTER)
        self.product_Table.heading("status", text="Trạng thái", anchor=CENTER)
        self.product_Table.heading("barcode", text="Barcode", anchor=CENTER)
        self.product_Table.heading("cost_price", text="Giá nhập", anchor=CENTER)
        self.product_Table.heading("min_qty", text="Tồn min", anchor=CENTER)
        self.product_Table.heading("unit", text="ĐVT", anchor=CENTER)
        self.product_Table["show"] = "headings"

        self.product_Table.column("pid", width=40, anchor=CENTER)
        self.product_Table.column("Category", width=100, anchor=CENTER)
        self.product_Table.column("Supplier", width=100, anchor=CENTER)
        self.product_Table.column("name", width=160, anchor=CENTER)
        self.product_Table.column("price", width=80, anchor=CENTER)
        self.product_Table.column("qty", width=50, anchor=CENTER)
        self.product_Table.column("status", width=80, anchor=CENTER)
        self.product_Table.column("barcode", width=100, anchor=CENTER)
        self.product_Table.column("cost_price", width=80, anchor=CENTER)
        self.product_Table.column("min_qty", width=60, anchor=CENTER)
        self.product_Table.column("unit", width=50, anchor=CENTER)
        self.product_Table.pack(fill=BOTH, expand=1, padx=10, pady=5)
        self.product_Table.bind("<ButtonRelease-1>", self.get_data)

        self.show()
        self.search_suggest = SearchSuggest(
            self.root,
            self.txt_search,
            self._fetch_search_suggestions,
            self._apply_search_suggestion,
        )
        self.cmb_search.bind("<<ComboboxSelected>>", lambda e: self.search_suggest.hide(), add="+")

        self.scaler = AutoScale(self.root, 1200, 750)

    def fetch_cat_sup(self):
        """Nạp danh sách danh mục và nhà cung cấp cho combobox."""
        current_cat = self.var_cat.get()
        current_sup = self.var_sup.get()
        self.cat_list = ["Chọn..."]
        self.sup_list = ["Chọn..."]
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute("Select name from category")
            cat = cur.fetchall()
            for i in cat:
                self.cat_list.append(i[0])

            cur.execute("Select name from supplier")
            sup = cur.fetchall()
            for i in sup:
                self.sup_list.append(i[0])
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()

        if hasattr(self, "cmb_cat"):
            self.cmb_cat.configure(values=self.cat_list)
            self.var_cat.set(current_cat if current_cat in self.cat_list else "Chọn...")
        if hasattr(self, "cmb_sup"):
            self.cmb_sup.configure(values=self.sup_list)
            self.var_sup.set(current_sup if current_sup in self.sup_list else "Chọn...")

    def _load_description(self, pid):
        """Lấy mô tả chi tiết của sản phẩm theo ID."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute("SELECT description FROM product WHERE pid=?", (pid,))
            row = cur.fetchone()
            self.var_description.set(row[0] if row and row[0] else "")
        except Exception:
            self.var_description.set("")
        finally:
            con.close()

    def _parse_product_numbers(self):
        """Đọc và kiểm tra các trường số của sản phẩm."""
        try:
            price = float(self.var_price.get())
            qty = int(self.var_qty.get())
            cost_price = float(self.var_cost_price.get()) if self.var_cost_price.get() else 0
            min_qty = int(self.var_min_qty.get()) if self.var_min_qty.get() else 5
        except ValueError:
            raise ValueError("Giá bán, Giá nhập, Số lượng và Tồn kho min phải là số hợp lệ!")

        if price <= 0:
            raise ValueError("Giá bán phải lớn hơn 0")
        if qty < 0 or cost_price < 0 or min_qty < 0:
            raise ValueError("Số lượng, Giá nhập và Tồn kho min không được âm")

        return price, qty, cost_price, min_qty

    def _get_search_column(self):
        """Ánh xạ tiêu chí tìm kiếm sản phẩm sang cột DB."""
        return {
            "Tên SP": "name",
            "Danh mục": "Category",
            "Nhà cung cấp": "Supplier",
            "Barcode": "barcode",
        }.get(self.var_searchBy.get())

    def _fetch_search_suggestions(self, term):
        """Lấy gợi ý sản phẩm theo tiền tố."""
        db_column = self._get_search_column()
        if not db_column:
            return []

        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute(
                f"SELECT DISTINCT {db_column} FROM product "
                f"WHERE {db_column} LIKE ? "
                f"ORDER BY {db_column} LIMIT 8",
                (f"{term}%",)
            )
            return [row[0] for row in cur.fetchall() if row[0]]
        finally:
            con.close()

    def _apply_search_suggestion(self, value):
        """Điền gợi ý và chạy tìm kiếm."""
        self.var_searchtxt.set(value)
        self.search()

    def add(self):
        """Thêm sản phẩm mới với kiểm tra dữ liệu."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if self.var_cat.get() == "Chọn..." or self.var_sup.get() == "Chọn..." or self.var_name.get().strip() == "":
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin", parent=self.root)
                return

            try:
                price, qty, cost_price, min_qty = self._parse_product_numbers()
            except ValueError as ex:
                messagebox.showerror("Lỗi", str(ex), parent=self.root)
                return

            cur.execute("Select * from product WHERE name = ?", (self.var_name.get(),))
            row = cur.fetchone()
            if row != None:
                messagebox.showerror("Lỗi", "Sản phẩm này đã tồn tại", parent=self.root)
            else:
                status = "Ngừng bán" if qty <= 0 else self.var_status.get()
                cur.execute(
                    "INSERT INTO product(Category,Supplier,name,price,qty,status,barcode,cost_price,min_qty,unit,description) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
                    (self.var_cat.get(), self.var_sup.get(), self.var_name.get(),
                     f"{price:g}", str(qty), status,
                     self.var_barcode.get(), cost_price, min_qty,
                     self.var_unit.get(), self.var_description.get()))
                con.commit()
                messagebox.showinfo("Thành công", "Thêm sản phẩm thành công", parent=self.root)
                log_action("Admin", "ADD_PRODUCT", f"Thêm SP: {self.var_name.get()}")
                self.show()

        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def show(self):
        """Hiển thị danh sách sản phẩm."""
        self.fetch_cat_sup()
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute("SELECT pid,Category,Supplier,name,price,qty,status,barcode,cost_price,min_qty,unit FROM product")
            rows = cur.fetchall()
            self.product_Table.delete(*self.product_Table.get_children())
            for row in rows:
                self.product_Table.insert('', END, values=row)
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hiển thị: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def get_data(self, ev):
        """Lấy dữ liệu sản phẩm từ bảng lên form."""
        f = self.product_Table.focus()
        content = (self.product_Table.item(f))
        row = content['values']
        if not row:
            return
        self.var_pid.set(row[0])
        self.var_cat.set(row[1])
        self.var_sup.set(row[2])
        self.var_name.set(row[3])
        self.var_price.set(row[4])
        self.var_qty.set(row[5])
        self.var_status.set(row[6])
        self.var_barcode.set(row[7] if len(row) > 7 and row[7] else "")
        self.var_cost_price.set(row[8] if len(row) > 8 and row[8] else "")
        self.var_min_qty.set(row[9] if len(row) > 9 and row[9] else "")
        self.var_unit.set(row[10] if len(row) > 10 and row[10] else "Cái")
        self._load_description(row[0])

    def update(self):
        """Cập nhật thông tin sản phẩm."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if self.var_pid.get() == "":
                messagebox.showerror("Lỗi", "Vui lòng chọn sản phẩm cần cập nhật", parent=self.root)
            else:
                try:
                    price, qty, cost_price, min_qty = self._parse_product_numbers()
                except ValueError as ex:
                    messagebox.showerror("Lỗi", str(ex), parent=self.root)
                    return

                status = self.var_status.get()
                if qty <= 0:
                    status = "Ngừng bán"
                elif status == "Ngừng bán":
                    status = "Đang bán"
                cur.execute(
                    "UPDATE product SET Category=?,Supplier=?,name=?,price=?,qty=?,status=?,barcode=?,cost_price=?,min_qty=?,unit=?,description=? WHERE pid=?",
                    (self.var_cat.get(), self.var_sup.get(), self.var_name.get(),
                     f"{price:g}", str(qty), status,
                     self.var_barcode.get(), cost_price, min_qty,
                     self.var_unit.get(), self.var_description.get(), self.var_pid.get()))
                con.commit()
                messagebox.showinfo("Thành công", "Cập nhật sản phẩm thành công", parent=self.root)
                log_action("Admin", "UPDATE_PRODUCT", f"Sửa SP ID={self.var_pid.get()}: {self.var_name.get()}")
                self.show()
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def delete(self):
        """Xoá sản phẩm theo ID."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if self.var_pid.get() == "":
                messagebox.showerror("Lỗi", "Vui lòng chọn sản phẩm cần xóa", parent=self.root)
            else:
                cur.execute("Select * from product WHERE pid = ?", (self.var_pid.get(),))
                row = cur.fetchone()
                if row == None:
                    messagebox.showerror("Lỗi", "Sản phẩm không tồn tại", parent=self.root)
                else:
                    op = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa?", parent=self.root)
                    if op == True:
                        cur.execute("delete from product where pid=?", (self.var_pid.get(),))
                        con.commit()
                        messagebox.showinfo("Đã xóa", "Xóa sản phẩm thành công", parent=self.root)
                        log_action("Admin", "DELETE_PRODUCT", f"Xóa SP ID={self.var_pid.get()}")
                        self.clear()
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def clear(self):
        """Làm mới form và bảng."""
        self.var_cat.set("Chọn...")
        self.var_sup.set("Chọn...")
        self.var_name.set("")
        self.var_price.set("")
        self.var_qty.set("")
        self.var_status.set("Đang bán")
        self.var_pid.set("")
        self.var_searchtxt.set("")
        self.var_searchBy.set("Chọn mục...")
        self.var_barcode.set("")
        self.var_cost_price.set("")
        self.var_min_qty.set("")
        self.var_unit.set("Cái")
        self.var_description.set("")
        if hasattr(self, "search_suggest"):
            self.search_suggest.hide()
        self.show()

    def search(self):
        """Tìm sản phẩm theo tiêu chí đã chọn."""
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
                cur.execute(f"SELECT pid,Category,Supplier,name,price,qty,status,barcode,cost_price,min_qty,unit FROM product WHERE {db_column} LIKE ?", (search_value,))
                rows = cur.fetchall()
                if len(rows) != 0:
                    self.product_Table.delete(*self.product_Table.get_children())
                    for row in rows:
                        self.product_Table.insert('', END, values=row)
                else:
                    messagebox.showerror("Lỗi", "Không tìm thấy sản phẩm nào", parent=self.root)
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def export_csv(self):
        """Xuất danh sách sản phẩm ra file CSV."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"san_pham_{time.strftime('%Y%m%d_%H%M%S')}.csv",
            parent=self.root
        )
        if not file_path:
            return
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute("SELECT pid,Category,Supplier,name,price,qty,status,barcode,cost_price,min_qty,unit,description FROM product")
            rows = cur.fetchall()
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Danh mục', 'NCC', 'Tên SP', 'Giá bán', 'SL', 'Trạng thái', 'Barcode', 'Giá nhập', 'Tồn min', 'ĐVT', 'Mô tả'])
                writer.writerows(rows)
            messagebox.showinfo("Thành công", f"Đã xuất {len(rows)} sản phẩm ra:\n{file_path}", parent=self.root)
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi xuất CSV: {str(ex)}", parent=self.root)
        finally:
            con.close()


if __name__ == "__main__":
    root = Tk()
    obj = productClass(root)
    root.mainloop()
