"""Màn hình bán hàng: chọn sản phẩm, giỏ hàng, tạo và in hóa đơn."""

from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import sqlite3
import time
import os
import tempfile
import platform
from ui_theme import COLORS, FONTS, apply_ttk_theme
from ui_scale import AutoScale
from db_helper import get_db_connection
from search_suggest import SearchSuggest


class BillClass:
    """Xử lý luồng bán hàng từ giỏ đến thanh toán."""
    def __init__(self, root):
        self.root = root
        self.root.geometry("1350x700+0+0")
        self.root.title("Hệ thống Quản lý Cửa hàng Tiện lợi | Bán hàng")
        apply_ttk_theme()
        APP_BG = COLORS["bg"]
        self.root.config(bg=APP_BG)

        # Trạng thái giỏ hàng và quyền in hóa đơn.
        self.cart_list = []
        self.chk_print = 0
        self.bill_amnt = 0
        self.current_invoice_id = ""
        self.file_path = ""
        self._bill_update_after_id = None

        # Biến nhập liệu khách hàng.
        self.var_search = StringVar()
        self.var_cname = StringVar()
        self.var_ccontact = StringVar()
        self.var_discount = StringVar()
        self.var_discount.set("0")

        # Biến sản phẩm được chọn.
        self.var_pid = StringVar()
        self.var_pname = StringVar()
        self.var_price = StringVar()
        self.var_qty = StringVar()
        self.var_stock = StringVar()

        # Header.
        HEADER_BG = COLORS["surface"]
        HEADER_FG = COLORS["text"]
        SOFT_BG = COLORS["surface_muted"]
        SOFT_TEXT = COLORS["text"]
        try:
            self.icon_title = Image.open("Images/images/logo1.png")
            self.icon_title = self.icon_title.resize((50, 50), Image.LANCZOS)
            self.icon_title = ImageTk.PhotoImage(self.icon_title)
            title = Label(self.root, text="  HÓA ĐƠN & BÁN HÀNG", image=self.icon_title, compound=LEFT,
                          font=FONTS["title_large"], bg=HEADER_BG, fg=HEADER_FG, anchor="w", padx=20).place(x=0, y=0,
                                                                                                             relwidth=1,
                                                                                                             height=70)
        except Exception as e:
            title = Label(self.root, text="  HÓA ĐƠN & BÁN HÀNG",
                          font=FONTS["title_large"], bg=HEADER_BG, fg=HEADER_FG, anchor="w", padx=20).place(x=0, y=0,
                                                                                                             relwidth=1,
                                                                                                             height=70)
            print("Lỗi logo:", e)

        btn_logout = Button(self.root, text="Đóng", command=self.root.destroy, font=FONTS["body_bold"],
                            bg=COLORS["danger"], fg="black", cursor="hand2").place(x=1200, y=10, width=120, height=50)

        # Đồng hồ trạng thái.
        self.lbl_clock = Label(self.root, text="...", font=FONTS["small"], bg=SOFT_BG, fg=SOFT_TEXT)
        self.lbl_clock.place(x=0, y=70, relwidth=1, height=30)
        self.update_date_time()

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception as e:
            print("Lỗi theme:", e)
        style.configure("Treeview", background=COLORS["surface"], fieldbackground=COLORS["surface"],
                        foreground=COLORS["text"],
                        rowheight=24, borderwidth=0)
        style.map("Treeview", background=[("selected", COLORS["row_selected"])],
                  foreground=[("selected", COLORS["text"])])
        style.configure("Treeview.Heading", background=COLORS["table_head"], foreground=COLORS["text"],
                        font=FONTS["table_heading"])

        # Khung trái: tìm kiếm và danh sách sản phẩm.
        ProductFrame = Frame(self.root, bd=4, relief=RIDGE, bg=COLORS["surface"])
        ProductFrame.place(x=6, y=110, width=410, height=550)

        Label(ProductFrame, text="Tìm kiếm Sản phẩm", font=FONTS["section"], bg=COLORS["table_head"],
              fg=COLORS["text"]).pack(
            side=TOP, fill=X)

        # Ô tìm kiếm.
        ProductFrame2 = Frame(ProductFrame, bd=2, relief=RIDGE, bg=COLORS["surface"])
        ProductFrame2.place(x=2, y=42, width=398, height=90)

        Label(ProductFrame2, text="Tên SP:", font=FONTS["body_bold"], bg=COLORS["surface"]).place(x=2, y=5)
        self.txt_search = Entry(ProductFrame2, textvariable=self.var_search, font=FONTS["body"],
                                bg=COLORS["input_bg"])
        self.txt_search.place(x=70, y=5, width=140, height=22)
        self.txt_search.bind("<Return>", lambda e: self.search())

        btn_search = Button(ProductFrame2, text="Tìm", command=self.search, font=FONTS["small"],
                            bg=COLORS["primary"], fg="black").place(x=220, y=5, width=80, height=22)
        btn_show = Button(ProductFrame2, text="Tất cả", command=self.show, font=FONTS["small"],
                          bg=COLORS["neutral_btn"], fg=COLORS["text"]).place(x=310, y=5, width=80, height=22)

        # Bảng sản phẩm.
        ProductFrame3 = Frame(ProductFrame, bd=3, relief=RIDGE, bg=COLORS["surface"])
        ProductFrame3.place(x=2, y=140, width=398, height=400)

        scrolly = Scrollbar(ProductFrame3, orient=VERTICAL)
        scrollx = Scrollbar(ProductFrame3, orient=HORIZONTAL)

        self.product_Table = ttk.Treeview(ProductFrame3, columns=("pid", "name", "price", "qty", "status"),
                                          yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
        scrollx.pack(side=BOTTOM, fill=X)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.config(command=self.product_Table.xview)
        scrolly.config(command=self.product_Table.yview)

        self.product_Table.heading("pid", text="ID", anchor=CENTER)
        self.product_Table.heading("name", text="Tên Hàng", anchor=W)
        self.product_Table.heading("price", text="Giá", anchor=E)
        self.product_Table.heading("qty", text="Kho", anchor=CENTER)
        self.product_Table.heading("status", text="TT", anchor=CENTER)
        self.product_Table["show"] = "headings"
        self.product_Table.column("pid", width=40, anchor=CENTER)
        self.product_Table.column("name", width=120, anchor=W)
        self.product_Table.column("price", width=80, anchor=E)
        self.product_Table.column("qty", width=50, anchor=CENTER)
        self.product_Table.column("status", width=70, anchor=CENTER)

        self.product_Table.pack(fill=BOTH, expand=1)
        self.product_Table.bind("<ButtonRelease-1>", self.get_data)

        # Khung giữa: thông tin khách hàng và giỏ hàng.
        CartFrame = Frame(self.root, bd=4, relief=RIDGE, bg=COLORS["surface"])
        CartFrame.place(x=420, y=110, width=450, height=550)
        Label(CartFrame, text="Thông tin Khách hàng", font=FONTS["section"], bg=COLORS["table_head"],
              fg=COLORS["text"]).pack(
            side=TOP, fill=X)

        # Thông tin khách hàng.
        F_Info = Frame(CartFrame, bg=COLORS["surface"])
        F_Info.place(x=5, y=35, width=430, height=60)
        Label(F_Info, text="Tên:", font=FONTS["body_bold"], bg=COLORS["surface"]).place(x=0, y=5)
        Entry(F_Info, textvariable=self.var_cname, font=FONTS["body"], bg=COLORS["input_bg"]).place(x=40, y=5, width=160)
        Label(F_Info, text="SĐT:", font=FONTS["body_bold"], bg=COLORS["surface"]).place(x=210, y=5)
        Entry(F_Info, textvariable=self.var_ccontact, font=FONTS["body"], bg=COLORS["input_bg"]).place(x=250, y=5, width=160)

        # Khu vực chọn số lượng sản phẩm.
        F_PInfo = Frame(CartFrame, bd=2, relief=RIDGE, bg=COLORS["surface"])
        F_PInfo.place(x=5, y=75, width=430, height=100)

        Label(F_PInfo, text="Tên SP:", font=FONTS["body_bold"], bg=COLORS["surface"]).place(x=5, y=5)
        Entry(F_PInfo, textvariable=self.var_pname, font=FONTS["body"], bg=COLORS["surface_muted"], state='readonly').place(x=5, y=30,
                                                                                                              width=180)

        Label(F_PInfo, text="Giá:", font=FONTS["body_bold"], bg=COLORS["surface"]).place(x=200, y=5)
        Entry(F_PInfo, textvariable=self.var_price, font=FONTS["body"], bg=COLORS["surface_muted"], state='readonly').place(x=200,
                                                                                                              y=30,
                                                                                                              width=100)

        Label(F_PInfo, text="Số lượng:", font=FONTS["body_bold"], bg=COLORS["surface"]).place(x=310, y=5)
        Entry(F_PInfo, textvariable=self.var_qty, font=FONTS["body"], bg=COLORS["input_bg"]).place(x=310, y=30, width=80)

        self.lbl_instock = Label(F_PInfo, text="Kho: [?]", font=FONTS["small"], bg=COLORS["surface"], fg=COLORS["text"])
        self.lbl_instock.place(x=310, y=60)

        Button(F_PInfo, text="Thêm vào Giỏ", command=self.add_cart, bg=COLORS["primary"], fg="black",
               font=FONTS["body_bold"]).place(x=100, y=60, width=180, height=30)
        Button(F_PInfo, text="Xóa", command=self.clear_cart_item, bg=COLORS["danger"], fg="black",
               font=FONTS["body_bold"]).place(x=290, y=60, width=80, height=30)

        # Bảng giỏ hàng.
        F_CartTable = Frame(CartFrame, bd=3, relief=RIDGE, bg=COLORS["surface"])
        F_CartTable.place(x=5, y=180, width=430, height=360)

        scrolly_cart = Scrollbar(F_CartTable, orient=VERTICAL)
        scrollx_cart = Scrollbar(F_CartTable, orient=HORIZONTAL)

        self.CartTable = ttk.Treeview(F_CartTable, columns=("pid", "name", "price", "qty"),
                                      yscrollcommand=scrolly_cart.set, xscrollcommand=scrollx_cart.set)
        scrolly_cart.pack(side=RIGHT, fill=Y)
        scrollx_cart.pack(side=BOTTOM, fill=X)
        scrolly_cart.config(command=self.CartTable.yview)
        scrollx_cart.config(command=self.CartTable.xview)

        self.CartTable.heading("pid", text="ID", anchor=CENTER)
        self.CartTable.heading("name", text="Tên Hàng", anchor=W)
        self.CartTable.heading("price", text="Đơn Giá", anchor=E)
        self.CartTable.heading("qty", text="SL", anchor=CENTER)
        self.CartTable["show"] = "headings"
        self.CartTable.column("pid", width=40, anchor=CENTER)
        self.CartTable.column("name", width=150, anchor=W)
        self.CartTable.column("price", width=90, anchor=E)
        self.CartTable.column("qty", width=40, anchor=CENTER)
        self.CartTable.pack(fill=BOTH, expand=1)
        self.CartTable.bind("<ButtonRelease-1>", self.get_cart_data)

        # Khung phải: hóa đơn và thanh toán.
        BillFrame = Frame(self.root, bd=4, relief=RIDGE, bg=COLORS["surface"])
        BillFrame.place(x=875, y=110, width=460, height=550)
        Label(BillFrame, text="Hóa Đơn Thanh Toán", font=FONTS["section"], bg=COLORS["table_head"],
              fg=COLORS["text"]).pack(side=TOP,
                                                                                                               fill=X)

        self.txt_bill_area = Text(BillFrame, font=FONTS["mono"], bg=COLORS["surface_muted"], fg=COLORS["text"], bd=0)
        self.txt_bill_area.pack(fill=BOTH, expand=1)

        BillMenuFrame = Frame(BillFrame, bd=2, relief=RIDGE, bg=COLORS["surface"])
        BillMenuFrame.pack(side=BOTTOM, fill=X)

        self.lbl_amnt = Label(BillMenuFrame, text="Thanh toán:\n0 VNĐ", font=FONTS["body_bold"], bg=COLORS["surface"],
                              fg=COLORS["text"])
        self.lbl_amnt.pack(side=LEFT, padx=5)

        # Nhập giảm giá theo phần trăm.
        discount_frame = Frame(BillMenuFrame, bg=COLORS["surface"])
        discount_frame.pack(side=LEFT, padx=5, pady=5)
        Label(discount_frame, text="Giảm giá (%)", font=FONTS["small"], bg=COLORS["surface"],
              fg=COLORS["text"]).pack(anchor="w")
        self.txt_discount = Entry(discount_frame, textvariable=self.var_discount, font=FONTS["body"],
                                  bg=COLORS["input_bg"], width=6)
        self.txt_discount.pack()
        self.txt_discount.bind("<KeyRelease>", self._schedule_bill_updates)

        Button(BillMenuFrame, text="Thanh toán", command=self.generate_bill, bg=COLORS["success"], fg="black",
               font=FONTS["body_bold"]).pack(side=LEFT, padx=5, pady=5, fill=Y)
        Button(BillMenuFrame, text="Lưu/In", command=self.print_bill, bg=COLORS["neutral_btn"], fg=COLORS["text"],
               font=FONTS["body_bold"]).pack(side=LEFT, padx=5, pady=5, fill=Y)
        Button(BillMenuFrame, text="Làm mới", command=self.clear_all, bg=COLORS["neutral_btn"], fg=COLORS["text"],
               font=FONTS["body_bold"]).pack(side=LEFT, padx=5, pady=5, fill=Y)

        self.show()
        self.search_suggest = SearchSuggest(
            self.root,
            self.txt_search,
            self._fetch_search_suggestions,
            self._apply_search_suggestion,
        )

        self.scaler = AutoScale(self.root, 1350, 700)

    def update_date_time(self):
        """Cập nhật đồng hồ trên header."""
        self.lbl_clock.config(text=f"Ngày: {time.strftime('%d-%m-%Y')} | Giờ: {time.strftime('%I:%M:%S %p')}")
        self.lbl_clock.after(1000, self.update_date_time)

    def show(self):
        """Hiển thị danh sách sản phẩm đang bán."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute("SELECT pid, name, price, qty, status FROM product WHERE status='Đang bán'")
            rows = cur.fetchall()
            self.product_Table.delete(*self.product_Table.get_children())
            for row in rows:
                self.product_Table.insert('', END, values=row)
        except Exception as ex:
            messagebox.showerror("Lỗi", f"DB Error: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def _fetch_search_suggestions(self, term):
        """Gợi ý tên sản phẩm theo tiền tố để tìm nhanh hơn."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute(
                "SELECT DISTINCT name FROM product "
                "WHERE status='Đang bán' AND name LIKE ? "
                "ORDER BY name LIMIT 8",
                (f"{term}%",)
            )
            return [row[0] for row in cur.fetchall() if row[0]]
        finally:
            con.close()

    def _apply_search_suggestion(self, value):
        """Đổ gợi ý vào ô tìm kiếm và chạy lọc."""
        self.var_search.set(value)
        self.search()

    def _schedule_bill_updates(self, event=None):
        """Debounce cập nhật hóa đơn để nhập giảm giá không bị khựng."""
        if self._bill_update_after_id is not None:
            self.root.after_cancel(self._bill_update_after_id)
        self._bill_update_after_id = self.root.after(120, self._flush_bill_updates)

    def _flush_bill_updates(self):
        """Chạy cập nhật hóa đơn đã gom theo đợt."""
        self._bill_update_after_id = None
        self.bill_updates()

    def search(self):
        """Tìm sản phẩm theo tên trong danh sách đang bán."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if hasattr(self, "search_suggest"):
                self.search_suggest.hide()
            if self.var_search.get() == "":
                messagebox.showerror("Lỗi", "Nhập tên sản phẩm", parent=self.root)
            else:
                search_value = f"%{self.var_search.get()}%"
                cur.execute(
                    "SELECT pid, name, price, qty, status FROM product WHERE name LIKE ? AND status='Đang bán'",
                    (search_value,))
                rows = cur.fetchall()
                self.product_Table.delete(*self.product_Table.get_children())
                if rows:
                    for row in rows: self.product_Table.insert('', END, values=row)
                else:
                    messagebox.showerror("Lỗi", "Không tìm thấy!", parent=self.root)
        except Exception as ex:
            messagebox.showerror("Lỗi", f"DB Error: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def get_data(self, ev):
        """Lấy sản phẩm từ bảng và đưa vào form chọn số lượng."""
        f = self.product_Table.focus()
        content = (self.product_Table.item(f))
        row = content['values']
        if row:
            self.var_pid.set(row[0])
            self.var_pname.set(row[1])
            self.var_price.set(row[2])
            self.var_stock.set(row[3])
            self.lbl_instock.config(text=f"Kho: [{row[3]}]")
            self.var_qty.set('1')

    def get_cart_data(self, ev):
        """Lấy dòng giỏ hàng khi người dùng chọn."""
        f = self.CartTable.focus()
        content = (self.CartTable.item(f))
        row = content['values']
        if row:
            self.var_pid.set(row[0])
            self.var_pname.set(row[1])
            self.var_price.set(row[2])
            self.var_qty.set(row[3])
            self.lbl_instock.config(text="Kho: [Trong giỏ]")

    def add_cart(self):
        """Thêm/cập nhật sản phẩm trong giỏ."""
        if self.var_pid.get() == '':
            return messagebox.showerror('Lỗi', "Vui lòng chọn sản phẩm")
        if self.var_qty.get() == '':
            return messagebox.showerror('Lỗi', "Nhập số lượng")

        try:
            qty = int(self.var_qty.get())
            stock = int(self.var_stock.get())
        except Exception:
            return messagebox.showerror('Lỗi', "Số lượng không hợp lệ")

        if qty < 0:
            return messagebox.showerror('Lỗi', "Số lượng phải lớn hơn hoặc bằng 0")

        if qty > stock:
            return messagebox.showerror('Lỗi', "Kho không đủ hàng!")

        price = float(self.var_price.get())
        for i, item in enumerate(self.cart_list):
            if item[0] == self.var_pid.get():
                if messagebox.askyesno('Cập nhật', "Sản phẩm đã có. Cập nhật số lượng?"):
                    if qty == 0:
                        self.cart_list.pop(i)
                    else:
                        if qty > int(item[4]): return messagebox.showerror('Lỗi', "Kho không đủ!")
                        self.cart_list[i][3] = qty
                    self.show_cart()
                    self.bill_updates()
                return

        if qty == 0:
            return messagebox.showerror('Lỗi', "Số lượng phải lớn hơn 0")

        self.cart_list.append([self.var_pid.get(), self.var_pname.get(), price, qty, stock])
        self.show_cart()
        self.bill_updates()

    def show_cart(self):
        """Hiển thị giỏ hàng lên bảng."""
        self.CartTable.delete(*self.CartTable.get_children())
        for row in self.cart_list:
            self.CartTable.insert('', END, values=row[:4])

    def clear_cart_item(self):
        """Xoá lựa chọn hiện tại trong khu chọn sản phẩm."""
        self.var_pid.set('')
        self.var_pname.set('')
        self.var_price.set('')
        self.var_qty.set('')
        self.lbl_instock.config(text="Kho: [?]")

    def get_discount_percent(self):
        """Đọc và kiểm tra phần trăm giảm giá."""
        try:
            discount = float(self.var_discount.get())
        except Exception:
            return None
        if discount < 0 or discount > 100:
            return None
        return discount

    def _ensure_invoice_id(self):
        """Tạo mã hóa đơn tạm ổn định cho toàn bộ phiên thanh toán."""
        if not self.current_invoice_id:
            self.current_invoice_id = time.strftime("%d%m%Y%H%M%S")
        return self.current_invoice_id

    def bill_updates(self):
        """Tính tổng tiền, giảm giá và cập nhật nội dung hóa đơn."""
        self.bill_amnt = 0
        for row in self.cart_list:
            self.bill_amnt += (float(row[2]) * int(row[3]))
        if not self.cart_list:
            self.current_invoice_id = ""

        discount_percent = self.get_discount_percent()
        if discount_percent is None:
            discount_percent = 0
        discount_amount = self.bill_amnt * discount_percent / 100
        net_pay = self.bill_amnt - discount_amount

        self.lbl_amnt.config(text=f"Thanh toán:\n{net_pay:,.0f} VNĐ")

        W = 58
        self.txt_bill_area.delete('1.0', END)
        self.txt_bill_area.insert(END, "\n" + "=" * W + "\n")
        self.txt_bill_area.insert(END, f"{'CỬA HÀNG TIỆN LỢI TUFO':^{W}}\n")
        self.txt_bill_area.insert(END, f"{'SĐT: 0987654321':^{W}}\n")
        self.txt_bill_area.insert(END, "=" * W + "\n")
        invoice_id = self._ensure_invoice_id() if self.cart_list else ""
        self.txt_bill_area.insert(END, f"Hóa đơn: {invoice_id}\n")
        self.txt_bill_area.insert(END, f"Khách hàng: {self.var_cname.get()}\n")
        self.txt_bill_area.insert(END, f"SĐT KH    : {self.var_ccontact.get()}\n")
        self.txt_bill_area.insert(END, "-" * W + "\n")
        self.txt_bill_area.insert(END, f"{'Tên SP':<24} {'SL':^6} {'Đơn Giá':>12} {'Thành Tiền':>14}\n")
        self.txt_bill_area.insert(END, "-" * W + "\n")

        for row in self.cart_list:
            name = row[1][:24]
            qty = int(row[3])
            price = float(row[2])
            total = price * qty
            self.txt_bill_area.insert(END, f"{name:<24} {qty:^6} {price:>12,.0f} {total:>14,.0f}\n")

        self.txt_bill_area.insert(END, "-" * W + "\n")
        total_str = f"TỔNG CỘNG: {self.bill_amnt:,.0f} VNĐ"
        self.txt_bill_area.insert(END, f"{total_str:>{W}}\n")
        discount_str = f"GIẢM GIÁ ({discount_percent:.0f}%): {discount_amount:,.0f} VNĐ"
        self.txt_bill_area.insert(END, f"{discount_str:>{W}}\n")
        net_pay_str = f"THANH TOÁN: {net_pay:,.0f} VNĐ"
        self.txt_bill_area.insert(END, f"{net_pay_str:>{W}}\n")
        self.txt_bill_area.insert(END, "=" * W + "\n")
        self.txt_bill_area.insert(END, f"{'Cảm ơn quý khách!':^{W}}\n")

    def generate_bill(self):
        """Thanh toán, trừ kho, lưu DB và xuất file hóa đơn."""
        if not self.cart_list:
            return messagebox.showerror("Lỗi", "Giỏ hàng trống!")
        if self.var_cname.get() == '':
            return messagebox.showerror("Lỗi", "Nhập tên Khách hàng")

        discount_percent = self.get_discount_percent()
        if discount_percent is None:
            return messagebox.showerror("Lỗi", "Giảm giá phải là số từ 0 đến 100", parent=self.root)

        if messagebox.askyesno("Xác nhận", "Thanh toán hóa đơn này?"):
            try:
                with get_db_connection() as con:
                    cur = con.cursor()
                    try:
                        invoice_id = self._ensure_invoice_id()
                        self.bill_updates()
                        # Transaction: Trừ kho
                        for row in self.cart_list:
                            pid = row[0]
                            qty_buy = int(row[3])
                            # Lấy tồn kho hiện tại để kiểm tra
                            cur.execute("SELECT qty FROM product WHERE pid=?", (pid,))
                            stock_row = cur.fetchone()
                            if stock_row and int(stock_row[0]) < qty_buy:
                                raise ValueError(f"Sản phẩm {row[1]} không đủ số lượng trong kho.")
                                
                            cur.execute("UPDATE product SET qty = qty - ? WHERE pid=?", (qty_buy, pid))

                        # Nhóm D: Tự động ngừng bán SP hết hàng (qty <= 0).
                        cur.execute("UPDATE product SET status='Ngừng bán' WHERE CAST(qty AS INTEGER) <= 0 AND status='Đang bán'")

                        # Transaction: Tạo hóa đơn
                        discount_amount = round(self.bill_amnt * discount_percent / 100)
                        net_pay = round(self.bill_amnt - discount_amount)
                        cur.execute("INSERT INTO bill(invoice,date,cname,contact,amount,discount,net_pay) VALUES(?,?,?,?,?,?,?)", (
                            invoice_id,
                            time.strftime("%d/%m/%Y"),
                            self.var_cname.get(),
                            self.var_ccontact.get(),
                            str(self.bill_amnt),
                            str(int(discount_amount)),
                            str(int(net_pay))
                        ))
                        # Lưu chi tiết từng sản phẩm trong hoá đơn.
                        for row in self.cart_list:
                            item_name = row[1]
                            item_qty = int(row[3])
                            item_price = float(row[2])
                            item_subtotal = item_qty * item_price
                            cur.execute("INSERT INTO bill_item(invoice,pid,name,price,qty,total) VALUES(?,?,?,?,?,?)",
                                        (invoice_id, row[0], item_name, item_price, item_qty, item_subtotal))
                        # Tự động commit được quản lý bởi context manager nếu không có lỗi, 
                        # nhưng tốt nhất gọi rõ ràng
                        con.commit()

                        # In / Lưu hóa đơn ra file
                        if not os.path.exists('bills'): os.mkdir('bills')
                        self.file_path = f"bills/{invoice_id}.txt"
                        with open(self.file_path, 'w', encoding='utf-8') as f:
                            f.write(self.txt_bill_area.get('1.0', END))

                        # Nhóm E: Ghi audit log.
                        try:
                            from audit_log import log_action
                            log_action("Cashier", "CREATE_BILL",
                                       f"HĐ {invoice_id} | KH: {self.var_cname.get()} | {int(net_pay):,}₫")
                        except Exception:
                            pass

                        # Tích điểm khách hàng: 1 điểm / 10,000₫.
                        points_earned = int(net_pay) // 10000
                        loyalty_msg = ""
                        if points_earned > 0 and self.var_ccontact.get().strip():
                            contact = self.var_ccontact.get().strip()
                            cur.execute("SELECT cid, points FROM customer WHERE phone=?", (contact,))
                            cust_row = cur.fetchone()
                            if cust_row:
                                new_points = cust_row[1] + points_earned
                                cur.execute("UPDATE customer SET points=?, updated_at=? WHERE cid=?",
                                            (new_points, time.strftime("%Y-%m-%d %H:%M:%S"), cust_row[0]))
                                loyalty_msg = f"\n +{points_earned} điểm → Tổng: {new_points} điểm"
                            else:
                                # Tạo khách hàng mới nếu chưa tồn tại.
                                now = time.strftime("%Y-%m-%d %H:%M:%S")
                                cur.execute(
                                    "INSERT INTO customer(name,phone,points,created_at,updated_at) VALUES(?,?,?,?,?)",
                                    (self.var_cname.get(), contact, points_earned, now, now))
                                loyalty_msg = f"\n +{points_earned} điểm (khách hàng mới)"
                            con.commit()

                        messagebox.showinfo("Thành công",
                                            f"Đã thanh toán và lưu hóa đơn!{loyalty_msg}")
                        self.chk_print = 1
                        self.show()
                        self.clear_cart_item()
                        self.cart_list = []
                        self.current_invoice_id = ""
                    except Exception as e:
                        con.rollback()
                        raise e # Bắn lỗi ra ngoài để messagebox.showerror bắt được

            except Exception as ex:
                messagebox.showerror("Lỗi", f"Lỗi hệ thống hoặc kho: {str(ex)}")

    def print_bill(self):
        """Mở file hóa đơn theo hệ điều hành để in/xem."""
        if self.chk_print == 1:
            if platform.system() == "Windows":
                os.startfile(self.file_path, "print")
            elif platform.system() == "Darwin":
                import subprocess
                subprocess.call(['open', self.file_path])
            else:
                import subprocess
                subprocess.call(['xdg-open', self.file_path])
        else:
            messagebox.showerror("Lỗi", "Chưa có hóa đơn được tạo")

    def clear_all(self):
        """Đặt lại toàn bộ trạng thái bán hàng."""
        if self._bill_update_after_id is not None:
            self.root.after_cancel(self._bill_update_after_id)
            self._bill_update_after_id = None
        self.cart_list = []
        self.var_cname.set('')
        self.var_ccontact.set('')
        self.var_discount.set("0")
        self.txt_bill_area.delete('1.0', END)
        self.lbl_amnt.config(text="Thanh toán:\n0 VNĐ")
        self.clear_cart_item()
        self.show()
        self.chk_print = 0
        self.current_invoice_id = ""
        self.file_path = ""
        if hasattr(self, "search_suggest"):
            self.search_suggest.hide()


if __name__ == "__main__":
    root = Tk()
    obj = BillClass(root)
    root.mainloop()
