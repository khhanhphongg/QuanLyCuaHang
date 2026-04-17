"""Dashboard chính và điều hướng đến các màn hình nghiệp vụ."""

import csv
import os
import sqlite3
import sys
import subprocess
import time
from tkinter import *
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from ui_theme import COLORS, FONTS, apply_ttk_theme
from ui_scale import AutoScale

from employee import employeeClass
from supplier import supplierClass
from category import categoryClass
from product import productClass
from billing import BillClass
from exit import exitClass
from sales import salesClass
from customer import customerClass
from auto_backup import auto_backup
from audit_log import log_action
from create_db import create_db

# matplotlib nhúng vào Tkinter (tuỳ chọn – bỏ qua nếu chưa cài).
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MPL = True
except ImportError:
    HAS_MPL = False


class IMS:
    """Dashboard tổng quan và điều hướng các module quản lý."""
    def __init__(self, root):
        self.root = root
        self.root.geometry("1350x900+0+0")
        self.root.title("Hệ thống Quản lý Cửa hàng Tiện lợi | Dashboard")
        apply_ttk_theme()
        self.root.config(bg=COLORS["bg"])
        self._counts_after_id = None

        HEADER_BG = COLORS["surface"]
        HEADER_FG = COLORS["text"]
        CARD_BG = COLORS["surface"]
        CARD_BORDER = COLORS["border"]
        APP_BG = COLORS["bg"]
        SOFT_BG = COLORS["surface_muted"]
        SOFT_TEXT = COLORS["text_muted"]
        MENU_TEXT = COLORS["text"]
        MENU_TITLE_BG = COLORS["primary_soft"]
        BTN_YELLOW_BG = COLORS["warning_soft"]
        BTN_YELLOW_FG = COLORS["text"]

        # ── HEADER ────────────────────────────────────────────────────────
        try:
            self.icon_title = Image.open("Images/images/logo1.png")
            self.icon_title = self.icon_title.resize((50, 50), Image.LANCZOS)
            self.icon_title = ImageTk.PhotoImage(self.icon_title)
            Label(self.root, text="  QUẢN LÝ CỬA HÀNG TIỆN LỢI",
                  image=self.icon_title, compound=LEFT,
                  font=FONTS["title_large"], bg=HEADER_BG, fg=HEADER_FG,
                  anchor="w", padx=20).place(x=0, y=0, relwidth=1, height=70)
        except Exception as e:
            Label(self.root, text="  QUẢN LÝ CỬA HÀNG TIỆN LỢI",
                  font=FONTS["title_large"], bg=HEADER_BG, fg=HEADER_FG,
                  anchor="w", padx=20).place(x=0, y=0, relwidth=1, height=70)
            print("Lỗi logo:", e)

        Button(self.root, text="Đăng xuất", command=self.logout,
               font=FONTS["body_bold"], bg=COLORS["danger_soft"],
               fg=COLORS["danger"], bd=1, relief=SOLID,
               cursor="hand2").place(x=1190, y=15, height=40, width=130)

        # Đồng hồ trạng thái.
        self.lbl_clock = Label(self.root, text="...", font=FONTS["small"], bg=SOFT_BG, fg=SOFT_TEXT)
        self.lbl_clock.place(x=0, y=70, relwidth=1, height=30)
        self.update_clock()

        # Nút làm mới dữ liệu thống kê.
        btn_refresh = Button(self.root, text="Làm mới dữ liệu", command=self.update_content, font=FONTS["small"],
                             bg=BTN_YELLOW_BG, fg=BTN_YELLOW_FG, activebackground="#FFE9B6",
                             activeforeground="#8A5A00", bd=1, relief=SOLID, cursor="hand2")
        btn_refresh.place(x=1180, y=70, width=150, height=30)

        # Menu điều hướng bên trái.
        LeftMenu = Frame(self.root, bg="white", bd=0)
        LeftMenu.place(x=0, y=100, width=230, height=760)

        try:
            self.MenuLogo = Image.open("Images/images/menu_im.png")
            self.MenuLogo = self.MenuLogo.resize((150, 150), Image.LANCZOS)
            self.MenuLogo = ImageTk.PhotoImage(self.MenuLogo)
            lbl_MenuLogo = Label(LeftMenu, image=self.MenuLogo, bg="white", pady=20)
            lbl_MenuLogo.pack(side=TOP, fill=X)
        except Exception as e:
            print("Lỗi menu:", e)

        try:
            self.icon_side = PhotoImage(file="Images/images/side.png")
        except Exception as e:
            self.icon_side = None

        MENU_BTN_STYLE = {"font": FONTS["subtitle"], "bg": "white", "fg": MENU_TEXT, "activebackground": "#F0F2F4",
                          "activeforeground": MENU_TEXT, "bd": 0, "cursor": "hand2", "compound": LEFT, "padx": 20,
                          "anchor": "w"}

        Label(LeftMenu, text="MENU CHÍNH", font=FONTS["section"], bg=MENU_TITLE_BG, fg=MENU_TEXT,
              pady=10).pack(side=TOP, fill=X)

        btn_employee = Button(LeftMenu, text="  Nhân viên", command=self.employee, image=self.icon_side,
                              **MENU_BTN_STYLE)
        btn_employee.pack(side=TOP, fill=X, pady=2)

        btn_supplier = Button(LeftMenu, text="  Nhà cung cấp", command=self.supplier, image=self.icon_side,
                              **MENU_BTN_STYLE)
        btn_supplier.pack(side=TOP, fill=X, pady=2)

        btn_category = Button(LeftMenu, text="  Danh mục", command=self.category, image=self.icon_side,
                              **MENU_BTN_STYLE)
        btn_category.pack(side=TOP, fill=X, pady=2)

        btn_product = Button(LeftMenu, text="  Sản phẩm", command=self.product, image=self.icon_side, **MENU_BTN_STYLE)
        btn_product.pack(side=TOP, fill=X, pady=2)

        btn_sales = Button(LeftMenu, text="  Bán hàng", command=self.billing, image=self.icon_side, **MENU_BTN_STYLE)
        btn_sales.pack(side=TOP, fill=X, pady=2)

        btn_customer = Button(LeftMenu, text="  Khách hàng", command=self.customer, image=self.icon_side, **MENU_BTN_STYLE)
        btn_customer.pack(side=TOP, fill=X, pady=2)

        btn_history = Button(LeftMenu, text="  Lịch sử HĐ", command=self.sales, image=self.icon_side, **MENU_BTN_STYLE)
        btn_history.pack(side=TOP, fill=X, pady=2)

        btn_exit = Button(LeftMenu, text="  Thoát", command=self.exit, image=self.icon_side, **MENU_BTN_STYLE)
        btn_exit.pack(side=TOP, fill=X, pady=2)

        # Xác định vai trò người dùng từ tham số đăng nhập.
        if len(sys.argv) > 1:
            user_type = sys.argv[1]
        else:
            user_type = "Admin"

        Label(self.root, text=f"Xin chào: {user_type}", font=FONTS["body_bold"], bg=APP_BG,
              fg=MENU_TEXT).place(
            x=1000, y=85)

        # Khoá các chức năng quản trị nếu là nhân viên.
        if user_type == "Employee" or user_type == "Nhân viên":
            btn_employee.config(state="disabled", bg="#E4E7EC", fg="#98A2B3")
            btn_supplier.config(state="disabled", bg="#E4E7EC", fg="#98A2B3")
            btn_category.config(state="disabled", bg="#E4E7EC", fg="#98A2B3")
            btn_product.config(state="disabled", bg="#E4E7EC", fg="#98A2B3")

        # Khu vực thống kê dashboard.
        BOX_FONT = (FONTS["section"][0], 18, "bold")

        stats_area = Frame(self.root, bg=APP_BG, bd=0)
        stats_area.place(x=260, y=145, width=1060, height=520)

        stats_area.grid_rowconfigure(0, weight=1, uniform="stats")
        stats_area.grid_rowconfigure(1, weight=1, uniform="stats")
        stats_area.grid_rowconfigure(2, weight=1, uniform="stats")
        stats_area.grid_columnconfigure(0, weight=1, uniform="stats")
        stats_area.grid_columnconfigure(1, weight=1, uniform="stats")

        can_manage = user_type not in ("Employee", "Nhân viên")
        card_cursor = "hand2" if can_manage else "arrow"
        card_text = MENU_TEXT if can_manage else "#98A2B3"

        employee_box = Frame(stats_area, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER,
                             cursor=card_cursor)
        employee_box.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.lbl_employee = Label(employee_box, text="Tổng Nhân viên\n[ 0 ]", bd=0, bg=CARD_BG, fg=card_text,
                                  font=BOX_FONT, cursor=card_cursor)
        self.lbl_employee.pack(expand=True, fill=BOTH)

        supplier_box = Frame(stats_area, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER,
                             cursor=card_cursor)
        supplier_box.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.lbl_supplier = Label(supplier_box, text="Tổng Nhà cung cấp\n[ 0 ]", bd=0, bg=CARD_BG, fg=card_text,
                                  font=BOX_FONT, cursor=card_cursor)
        self.lbl_supplier.pack(expand=True, fill=BOTH)

        category_box = Frame(stats_area, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER,
                             cursor=card_cursor)
        category_box.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        self.lbl_category = Label(category_box, text="Tổng Danh mục\n[ 0 ]", bd=0, bg=CARD_BG, fg=card_text,
                                  font=BOX_FONT, cursor=card_cursor)
        self.lbl_category.pack(expand=True, fill=BOTH)

        product_box = Frame(stats_area, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER,
                            cursor=card_cursor)
        product_box.grid(row=1, column=1, padx=15, pady=15, sticky="nsew")
        self.lbl_product = Label(product_box, text="Tổng Sản phẩm\n[ 0 ]", bd=0, bg=CARD_BG, fg=card_text,
                                 font=BOX_FONT, cursor=card_cursor)
        self.lbl_product.pack(expand=True, fill=BOTH)

        if can_manage:
            employee_box.bind("<Button-1>", lambda event: self.employee())
            self.lbl_employee.bind("<Button-1>", lambda event: self.employee())
            supplier_box.bind("<Button-1>", lambda event: self.supplier())
            self.lbl_supplier.bind("<Button-1>", lambda event: self.supplier())
            category_box.bind("<Button-1>", lambda event: self.category())
            self.lbl_category.bind("<Button-1>", lambda event: self.category())
            product_box.bind("<Button-1>", lambda event: self.product())
            self.lbl_product.bind("<Button-1>", lambda event: self.product())

        # Hàng 3: Tổng Khách hàng + Doanh thu hôm nay.
        customer_box = Frame(stats_area, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER,
                             cursor="hand2")
        customer_box.grid(row=2, column=0, padx=15, pady=15, sticky="nsew")
        self.lbl_customer = Label(customer_box, text="Tổng Khách hàng\n[ 0 ]", bd=0, bg=CARD_BG, fg=MENU_TEXT,
                                  font=BOX_FONT, cursor="hand2")
        self.lbl_customer.pack(expand=True, fill=BOTH)
        customer_box.bind("<Button-1>", lambda event: self.customer())
        self.lbl_customer.bind("<Button-1>", lambda event: self.customer())

        revenue_box = Frame(stats_area, bg="#DBEAFE", highlightthickness=1, highlightbackground=CARD_BORDER)
        revenue_box.grid(row=2, column=1, padx=15, pady=15, sticky="nsew")
        self.lbl_revenue = Label(revenue_box, text="Doanh thu hôm nay\n[ 0₫ ]", bd=0, bg="#DBEAFE",
                                 fg=COLORS["primary"], font=BOX_FONT)
        self.lbl_revenue.pack(expand=True, fill=BOTH)

        # Thanh tiện ích dưới Dashboard.
        util_bar = Frame(self.root, bg=APP_BG, bd=0)
        util_bar.place(x=260, y=680, width=1060, height=40)

        btn_reorder = Button(util_bar, text="📋 Đề xuất nhập hàng", command=self.show_reorder_popup,
                             font=FONTS["body_bold"], bg=COLORS["accent"], fg="black", bd=0, cursor="hand2",
                             activebackground=COLORS["accent_dark"])
        btn_reorder.pack(side=LEFT, padx=(0, 10), ipady=4, ipadx=10)

        btn_report = Button(util_bar, text="📊 Xem báo cáo hôm qua", command=self.show_yesterday_report,
                            font=FONTS["body_bold"], bg=COLORS["primary_soft"], fg="black", bd=0, cursor="hand2")
        btn_report.pack(side=LEFT, padx=5, ipady=4, ipadx=10)

        self.lbl_backup_status = Label(util_bar, text="", font=FONTS["small"], bg=APP_BG, fg="#48BB78")
        self.lbl_backup_status.pack(side=RIGHT, padx=10)

        lbl_footer = Label(self.root, text="Hệ thống quản lý Kho & Bán hàng", font=FONTS["small"],
                           bg=HEADER_BG, fg="#98A2B3", pady=5).pack(side=BOTTOM, fill=X)

        self.scaler = AutoScale(self.root, 1350, 700)

        # Tự động hoá khi khởi động.
        backup_msg = auto_backup()
        self.lbl_backup_status.config(text=backup_msg)
        self.generate_daily_report()
        self.update_counts()

    def update_clock(self):
        date_now = time.strftime("%d-%m-%Y")
        time_now = time.strftime("%H:%M:%S")
        self.lbl_clock.config(text=f"   Hệ thống quản lý  |  Ngày: {date_now}  |  Giờ: {time_now}")
        self.root.after(1000, self.update_clock)

    def update_counts(self):
        """Đếm số lượng bản ghi và cập nhật các ô thống kê."""
        if self._counts_after_id is not None:
            try:
                self.root.after_cancel(self._counts_after_id)
            except Exception:
                pass
            self._counts_after_id = None

        con = sqlite3.connect(database="ims.db")
        cur = con.cursor()
        try:
            cur.execute(
                "SELECT "
                "(SELECT COUNT(*) FROM employee), "
                "(SELECT COUNT(*) FROM category), "
                "(SELECT COUNT(*) FROM product), "
                "(SELECT COUNT(*) FROM supplier), "
                "(SELECT COUNT(*) FROM customer)"
            )
            counts = cur.fetchone()
            employee_count = counts[0]
            category_count = counts[1]
            product_count = counts[2]
            supplier_count = counts[3]
            customer_count = counts[4]

            self.lbl_employee.config(text=f"Tổng Nhân viên\n\n[ {employee_count} ]")
            self.lbl_category.config(text=f"Tổng Danh mục\n\n[ {category_count} ]")
            self.lbl_product.config(text=f"Tổng Sản phẩm\n\n[ {product_count} ]")
            self.lbl_supplier.config(text=f"Tổng Nhà cung cấp\n\n[ {supplier_count} ]")
            self.lbl_customer.config(text=f"Tổng Khách hàng\n\n[ {customer_count} ]")

            # Doanh thu hôm nay.
            import time
            today = time.strftime("%d/%m/%Y")
            cur.execute("SELECT SUM(CAST(net_pay AS REAL)) FROM bill WHERE date=?", (today,))
            revenue_row = cur.fetchone()
            revenue = revenue_row[0] if revenue_row[0] else 0
            revenue_str = f"{revenue:,.0f}₫"
            self.lbl_revenue.config(text=f"Doanh thu hôm nay\n\n[ {revenue_str} ]")

            # Cảnh báo tồn kho thấp.
            cur.execute("SELECT COUNT(*) FROM product WHERE CAST(qty AS INTEGER) <= min_qty AND status='Đang bán'")
            low_stock_count = cur.fetchone()[0]
            if low_stock_count > 0:
                self.lbl_product.config(
                    text=f"Tổng Sản phẩm\n[ {product_count} ]\n⚠ {low_stock_count} SP sắp hết",
                    fg=COLORS["danger"])
            else:
                self.lbl_product.config(fg=COLORS["text"])

        except Exception as ex:
            pass
        finally:
            con.close()
        self._counts_after_id = self.root.after(10000, self.update_counts)

    def update_content(self):
        """Làm mới dữ liệu thống kê theo yêu cầu người dùng."""
        self.update_counts()
        messagebox.showinfo("Thông báo", "Đã làm mới dữ liệu hệ thống!", parent=self.root)

    # ─── Nhóm B: Đề xuất nhập hàng ───
    def show_reorder_popup(self):
        """Hiển thị popup danh sách SP cần nhập thêm hàng."""
        popup = Toplevel(self.root)
        popup.title("📋 Đề xuất nhập hàng")
        popup.geometry("750x450+300+200")
        popup.config(bg=COLORS["bg"])
        popup.focus_force()
        popup.grab_set()

        Label(popup, text="SẢN PHẨM CẦN NHẬP THÊM", font=FONTS["title"], bg=COLORS["surface"],
              fg=COLORS["text"], pady=10).pack(fill=X)

        tree_frame = Frame(popup, bg=COLORS["bg"])
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=5)

        scrolly = Scrollbar(tree_frame, orient=VERTICAL)
        tree = ttk.Treeview(tree_frame,
                            columns=("pid", "name", "supplier", "qty", "min_qty", "suggest", "unit"),
                            yscrollcommand=scrolly.set, show="headings")
        scrolly.pack(side=RIGHT, fill=Y)
        scrolly.config(command=tree.yview)

        tree.heading("pid", text="ID")
        tree.heading("name", text="Tên SP")
        tree.heading("supplier", text="NCC")
        tree.heading("qty", text="Tồn kho")
        tree.heading("min_qty", text="Tối thiểu")
        tree.heading("suggest", text="Đề xuất nhập")
        tree.heading("unit", text="ĐVT")

        tree.column("pid", width=40, anchor=CENTER)
        tree.column("name", width=180)
        tree.column("supplier", width=120)
        tree.column("qty", width=70, anchor=CENTER)
        tree.column("min_qty", width=70, anchor=CENTER)
        tree.column("suggest", width=90, anchor=CENTER)
        tree.column("unit", width=50, anchor=CENTER)
        tree.pack(fill=BOTH, expand=True)

        con = sqlite3.connect(database="ims.db")
        cur = con.cursor()
        rows = []
        try:
            cur.execute(
                "SELECT pid, name, Supplier, CAST(qty AS INTEGER), min_qty, unit "
                "FROM product WHERE CAST(qty AS INTEGER) <= min_qty AND status='Đang bán'"
            )
            rows = cur.fetchall()
            for row in rows:
                qty_now = row[3]
                min_q = row[4]
                suggest = max(min_q * 2 - qty_now, min_q)
                tree.insert('', END, values=(row[0], row[1], row[2], qty_now, min_q, suggest, row[5]))
        except Exception:
            pass
        finally:
            con.close()

        if not rows:
            Label(popup, text="✅ Tất cả sản phẩm đều đủ hàng!", font=FONTS["section"],
                  bg=COLORS["bg"], fg="#48BB78", pady=20).pack()

        btn_frame = Frame(popup, bg=COLORS["bg"])
        btn_frame.pack(fill=X, padx=10, pady=8)

        def export_reorder_csv():
            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV", "*.csv")],
                initialfile=f"de_xuat_nhap_{time.strftime('%Y%m%d')}.csv",
                parent=popup
            )
            if not path:
                return
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Tên SP', 'NCC', 'Tồn kho', 'Tối thiểu', 'Đề xuất nhập', 'ĐVT'])
                for child in tree.get_children():
                    writer.writerow(tree.item(child)['values'])
            messagebox.showinfo("Thành công", f"Đã xuất đề xuất nhập hàng!\n{path}", parent=popup)
            log_action("System", "EXPORT_REORDER", f"Xuất CSV đề xuất nhập: {path}")

        Button(btn_frame, text="📥 Xuất CSV đề xuất", command=export_reorder_csv,
               font=FONTS["body_bold"], bg=COLORS["accent"], fg="black", bd=0, cursor="hand2",
               padx=15, pady=5).pack(side=LEFT)
        Button(btn_frame, text="Đóng", command=popup.destroy,
               font=FONTS["body_bold"], bg=COLORS["surface_muted"], fg=COLORS["text"], bd=0,
               cursor="hand2", padx=15, pady=5).pack(side=RIGHT)

    # ─── Nhóm C: Báo cáo doanh thu tự động ───
    def generate_daily_report(self):
        """Tự động tạo file báo cáo ngày hôm qua nếu chưa có."""
        import datetime
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%d/%m/%Y")
        yesterday_file = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, f"bao_cao_{yesterday_file}.txt")

        if os.path.exists(report_path):
            return  # Đã tạo rồi

        con = sqlite3.connect(database="ims.db")
        cur = con.cursor()
        try:
            cur.execute("SELECT COUNT(*), SUM(CAST(net_pay AS REAL)) FROM bill WHERE date=?", (yesterday,))
            row = cur.fetchone()
            total_bills = row[0] if row[0] else 0
            total_revenue = row[1] if row[1] else 0

            # Top 5 SP bán chạy hôm qua.
            cur.execute(
                "SELECT name, SUM(CAST(qty AS INTEGER)) as total_qty, SUM(CAST(total AS REAL)) as total_amt "
                "FROM bill_item WHERE invoice IN (SELECT invoice FROM bill WHERE date=?) "
                "GROUP BY name ORDER BY total_qty DESC LIMIT 5",
                (yesterday,)
            )
            top_products = cur.fetchall()

            # Ghi file báo cáo.
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write("=" * 50 + "\n")
                f.write(f"  BÁO CÁO DOANH THU NGÀY {yesterday}\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Tổng số đơn hàng: {total_bills}\n")
                f.write(f"Tổng doanh thu:   {total_revenue:,.0f}₫\n\n")
                f.write("-" * 50 + "\n")
                f.write("TOP 5 SẢN PHẨM BÁN CHẠY:\n")
                f.write("-" * 50 + "\n")
                if top_products:
                    for i, p in enumerate(top_products, 1):
                        f.write(f"  {i}. {p[0]:20s}  SL: {p[1]}  |  {p[2]:,.0f}₫\n")
                else:
                    f.write("  (Không có dữ liệu)\n")
                f.write("\n" + "=" * 50 + "\n")
                f.write(f"Tạo tự động lúc {time.strftime('%H:%M:%S %d/%m/%Y')}\n")

            log_action("System", "AUTO_REPORT", f"Tạo báo cáo ngày {yesterday}")
        except Exception:
            pass
        finally:
            con.close()

    def show_yesterday_report(self):
        """Mở popup hiển thị nội dung báo cáo ngày hôm qua."""
        import datetime
        yesterday_file = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        report_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", f"bao_cao_{yesterday_file}.txt")

        if not os.path.exists(report_path):
            messagebox.showinfo("Thông báo", "Chưa có báo cáo ngày hôm qua.\n(Không có đơn hàng nào)", parent=self.root)
            return

        popup = Toplevel(self.root)
        popup.title(f"📊 Báo cáo ngày {yesterday_file}")
        popup.geometry("500x400+400+200")
        popup.config(bg=COLORS["surface"])
        popup.focus_force()

        text = Text(popup, font=FONTS["mono"], bg=COLORS["surface"], fg=COLORS["text"],
                    wrap=WORD, bd=0, padx=15, pady=15)
        text.pack(fill=BOTH, expand=True)

        with open(report_path, 'r', encoding='utf-8') as f:
            text.insert('1.0', f.read())
        text.config(state=DISABLED)

        Button(popup, text="Đóng", command=popup.destroy, font=FONTS["body_bold"],
               bg=COLORS["surface_muted"], fg=COLORS["text"], bd=0, cursor="hand2",
               padx=15, pady=5).pack(pady=10)

    def employee(self):
        self.new_win = Toplevel(self.root)
        self.new_obj = employeeClass(self.new_win)

    def supplier(self):
        self.new_win = Toplevel(self.root)
        self.new_obj = supplierClass(self.new_win)

    def category(self):
        self.new_win = Toplevel(self.root)
        self.new_obj = categoryClass(self.new_win)

    def product(self):
        self.new_win = Toplevel(self.root)
        self.new_obj = productClass(self.new_win)

    def billing(self):
        self.new_win = Toplevel(self.root)
        self.new_obj = BillClass(self.new_win)

    def customer(self):
        self.new_win = Toplevel(self.root)
        self.new_obj = customerClass(self.new_win)

    def sales(self):
        self.new_win = Toplevel(self.root)
        self.new_obj = salesClass(self.new_win)

    def exit(self):
        exitClass(self.root)

    def logout(self):
        op = messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn Đăng xuất?", parent=self.root)

        if op == True:
            self.root.destroy()
            # Mở lại màn hình đăng nhập.
            subprocess.Popen([sys.executable, "login.py"])


if __name__ == "__main__":
    create_db(verbose=False)
    root = Tk()
    obj = IMS(root)
    root.mainloop()
