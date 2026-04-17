"""Màn hình lịch sử hóa đơn và xuất báo cáo doanh thu."""

from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk, messagebox, filedialog
import os
import re
import sqlite3
import csv
from ui_theme import COLORS, FONTS, apply_ttk_theme
from ui_scale import AutoScale
from search_suggest import SearchSuggest


class salesClass:
    """Hiển thị danh sách hóa đơn, xem chi tiết và xuất CSV."""
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x550+220+130")
        self.root.title("Hệ thống Quản lý Cửa hàng Tiện lợi | Lịch sử Bán hàng")
        apply_ttk_theme()
        APP_BG = COLORS["bg"]
        self.root.config(bg=APP_BG)
        self.root.focus_force()
        self.var_searchBy = StringVar()
        self.var_searchtxt = StringVar()

        # Header.
        HEADER_BG = COLORS["surface"]
        HEADER_FG = COLORS["text"]
        try:
            self.icon_title = Image.open("Images/images/logo1.png")
            self.icon_title = self.icon_title.resize((50, 50), Image.LANCZOS)
            self.icon_title = ImageTk.PhotoImage(self.icon_title)
            title = Label(self.root, text="  LỊCH SỬ HÓA ĐƠN", image=self.icon_title, compound=LEFT,
                          font=FONTS["title_large"], bg=HEADER_BG, fg=HEADER_FG, anchor="w", padx=20).place(x=0, y=0,
                                                                                                             relwidth=1,
                                                                                                             height=70)
        except Exception as e:
            title = Label(self.root, text="  LỊCH SỬ HÓA ĐƠN", font=FONTS["title_large"], bg=HEADER_BG, fg=HEADER_FG,
                          anchor="w", padx=20).place(x=0, y=0, relwidth=1, height=70)
            print("Lỗi logo:", e)

        # Khung trái: danh sách hóa đơn.
        SalesFrame = Frame(self.root, bd=3, relief=RIDGE, bg=COLORS["surface"])
        SalesFrame.place(x=50, y=80, width=300, height=400)

        SearchFrame = Frame(SalesFrame, bg=COLORS["surface"])
        SearchFrame.pack(side=TOP, fill=X, padx=6, pady=6)

        self.cmb_search = ttk.Combobox(
            SearchFrame,
            textvariable=self.var_searchBy,
            values=("Chọn mục...", "Mã HĐ", "Khách hàng", "SĐT"),
            state="readonly",
            justify=CENTER,
            font=FONTS["small"],
        )
        self.cmb_search.pack(side=LEFT)
        self.cmb_search.current(0)

        self.txt_search = Entry(SearchFrame, textvariable=self.var_searchtxt, font=FONTS["small"],
                                bg=COLORS["input_bg"])
        self.txt_search.pack(side=LEFT, fill=X, expand=True, padx=(6, 0), ipady=2)
        self.txt_search.bind("<Return>", lambda e: self.search())

        SearchActionFrame = Frame(SalesFrame, bg=COLORS["surface"])
        SearchActionFrame.pack(side=TOP, fill=X, padx=6, pady=(0, 6))
        Button(SearchActionFrame, text="Tìm", command=self.search, font=FONTS["small"],
               bg=COLORS["primary_soft"], fg=COLORS["text"], bd=1, relief=SOLID,
               cursor="hand2").pack(side=LEFT, expand=True, fill=X)
        Button(SearchActionFrame, text="Tất cả", command=self.clear_search, font=FONTS["small"],
               bg=COLORS["warning_soft"], fg=COLORS["text"], bd=1, relief=SOLID,
               cursor="hand2").pack(side=LEFT, expand=True, fill=X, padx=(6, 0))

        header_text = f"{'Mã Hóa Đơn':<22} {'Thực thu':>14}"
        Label(SalesFrame, text=header_text, font=FONTS["mono"], bg=COLORS["primary"],
              fg="white", anchor="w", padx=4).pack(side=TOP, fill=X)

        scrolly = Scrollbar(SalesFrame, orient=VERTICAL)
        self.SalesList = Listbox(SalesFrame, font=FONTS["mono"], bg=COLORS["surface"], fg=COLORS["text"],
                                 selectbackground=COLORS["primary"], selectforeground="white",
                                 yscrollcommand=scrolly.set)
        scrolly.pack(side=RIGHT, fill=Y)
        scrolly.config(command=self.SalesList.yview)
        self.SalesList.pack(fill=BOTH, expand=1)
        self.SalesList.bind("<ButtonRelease-1>", self.get_data)
        self.sales_index = []

        # Nhãn tổng doanh thu.
        self.lbl_tong_doanh_thu = Label(self.root, text="Tổng doanh thu: 0 VNĐ", font=FONTS["section"],
                                        bg=APP_BG, fg=COLORS["success"])
        self.lbl_tong_doanh_thu.place(x=50, y=490)

        btn_export = Button(self.root, text="Xuất CSV", command=self.export_csv, font=FONTS["body_bold"],
                            bg=COLORS["primary_soft"], fg=COLORS["text"], bd=1, relief=SOLID, cursor="hand2")
        btn_export.place(x=260, y=490, width=120, height=30)

        # Khung phải: chi tiết hóa đơn.
        BillFrame = Frame(self.root, bd=3, relief=RIDGE, bg=COLORS["surface"])
        BillFrame.place(x=400, y=80, width=650, height=400)

        Label(BillFrame, text="Nội dung Hóa đơn", font=FONTS["body_bold"], bg=COLORS["primary"],
              fg="white").pack(side=TOP, fill=X)

        scrolly2 = Scrollbar(BillFrame, orient=VERTICAL)
        self.bill_area = Text(BillFrame, font=FONTS["mono"], bg=COLORS["surface_muted"], fg=COLORS["text"],
                              insertbackground="#1F2937", yscrollcommand=scrolly2.set, wrap=NONE)
        self.bill_area.tag_configure("center", justify=CENTER)
        scrolly2.pack(side=RIGHT, fill=Y)
        scrolly2.config(command=self.bill_area.yview)
        self.bill_area.pack(fill=BOTH, expand=1)

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
        """Ánh xạ tiêu chí tìm kiếm sang cột của bảng bill."""
        return {
            "Mã HĐ": "invoice",
            "Khách hàng": "cname",
            "SĐT": "contact",
        }.get(self.var_searchBy.get())

    def _fetch_search_suggestions(self, term):
        """Gợi ý theo tiền tố cho lịch sử hóa đơn."""
        db_column = self._get_search_column()
        if not db_column:
            return []

        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute(
                f"SELECT DISTINCT {db_column} FROM bill "
                f"WHERE {db_column} LIKE ? "
                f"ORDER BY {db_column} LIMIT 8",
                (f"{term}%",)
            )
            rows = [str(row[0]) for row in cur.fetchall() if row[0] not in (None, "")]
        finally:
            con.close()

        if rows or db_column != "invoice":
            return rows

        return [
            file_name[:-4]
            for file_name, _ in self._fetch_file_entries(term)
        ]

    def _apply_search_suggestion(self, value):
        """Áp dụng gợi ý và lọc danh sách hóa đơn."""
        self.var_searchtxt.set(value)
        self.search()

    def _normalize_amount(self, raw_value):
        """Chuẩn hóa số tiền đọc từ DB/file về int."""
        try:
            return int(float(raw_value))
        except Exception:
            return 0

    def _populate_sales_list(self, entries):
        """Đổ dữ liệu danh sách hóa đơn lên Listbox và cập nhật tổng doanh thu."""
        self.SalesList.delete(0, END)
        self.sales_index = []
        total_amount = 0

        for display_name, amount in entries:
            total_amount += amount
            display_text = f"{display_name:<22} {amount:>12,} VNĐ"
            self.SalesList.insert(END, display_text)
            self.sales_index.append(display_name)

        self.lbl_tong_doanh_thu.config(text=f"Tổng doanh thu: {total_amount:,.0f} VNĐ")

    def _fetch_db_entries(self, search_column=None, search_term=None):
        """Lấy danh sách hóa đơn từ DB, có thể kèm điều kiện tìm kiếm."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            query = "SELECT invoice, net_pay, amount FROM bill"
            params = []
            if search_column and search_term:
                query += f" WHERE {search_column} LIKE ?"
                params.append(f"%{search_term}%")
            query += " ORDER BY invoice DESC"

            cur.execute(query, tuple(params))
            rows = cur.fetchall()
            return [
                (f"{row[0]}.txt", self._normalize_amount(row[1] if row[1] not in (None, "", "None") else row[2]))
                for row in rows
            ]
        finally:
            con.close()

    def _fetch_file_entries(self, invoice_term=""):
        """Lấy danh sách hóa đơn từ thư mục file text cũ."""
        if not os.path.exists('bills'):
            os.mkdir('bills')

        try:
            entries = []
            for file_name in sorted(os.listdir('bills'), reverse=True):
                if not file_name.endswith('.txt'):
                    continue
                if invoice_term and invoice_term.lower() not in file_name[:-4].lower():
                    continue
                entries.append((file_name, self.tinh_tien_mot_hoa_don(file_name)))
            return entries
        except Exception:
            return []

    def show(self):
        """Tải danh sách hóa đơn và tính tổng doanh thu."""
        entries = self._fetch_db_entries()
        if not entries:
            entries = self._fetch_file_entries()
        self._populate_sales_list(entries)

    def export_csv(self):
        """Xuất báo cáo doanh thu sang CSV."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute("SELECT invoice, date, cname, contact, amount, discount, net_pay FROM bill ORDER BY invoice DESC")
            rows = cur.fetchall()

            if not rows:
                return messagebox.showinfo("Thông báo", "Không có dữ liệu để xuất", parent=self.root)

            file_path = filedialog.asksaveasfilename(
                title="Lưu báo cáo CSV",
                defaultextension=".csv",
                filetypes=[("CSV", "*.csv")],
                initialfile="bao_cao_doanh_thu.csv"
            )
            if not file_path:
                return

            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["Mã HĐ", "Ngày", "Khách hàng", "SĐT", "Tổng tiền", "Giảm giá", "Thực thu"])
                writer.writerows(rows)

            messagebox.showinfo("Thành công", "Đã xuất báo cáo CSV", parent=self.root)
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi xuất CSV: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def tinh_tien_mot_hoa_don(self, file_name):
        """Đọc file txt và trích xuất tổng tiền."""
        tong_tien = 0
        tu_khoa_tim_kiem = ["tổng cộng", "thanh toán"]

        try:
            with open(f"bills/{file_name}", 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines:
                    line_lower = line.lower()
                    if any(tu_khoa in line_lower for tu_khoa in tu_khoa_tim_kiem):
                        line_cleaned = line.replace(',', '').replace('.', '')
                        numbers = re.findall(r'\d+', line_cleaned)

                        if numbers:
                            tong_tien = int(numbers[-1])
                            break
        except Exception:
            pass

        return tong_tien

    def get_data(self, ev):
        """Đọc file hóa đơn theo lựa chọn trong danh sách."""
        index_ = self.SalesList.curselection()
        if not index_: return

        idx = index_[0]
        if idx >= len(self.sales_index):
            return
        file_name = self.sales_index[idx]
        self.bill_area.delete('1.0', END)

        try:
            with open(f"bills/{file_name}", 'r', encoding='utf-8') as f:
                data = f.read()
                self.bill_area.insert(END, data, "center")
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Không đọc được file: {str(ex)}")

    def clear_search(self):
        """Đặt lại thanh tìm kiếm và tải toàn bộ hóa đơn."""
        self.var_searchBy.set("Chọn mục...")
        self.var_searchtxt.set("")
        if hasattr(self, "search_suggest"):
            self.search_suggest.hide()
        self.show()

    def search(self):
        """Tìm hóa đơn theo mã, khách hàng hoặc SĐT."""
        if hasattr(self, "search_suggest"):
            self.search_suggest.hide()

        if self.var_searchBy.get() == "Chọn mục...":
            return messagebox.showerror("Lỗi", "Vui lòng chọn tiêu chí tìm kiếm", parent=self.root)

        term = self.var_searchtxt.get().strip()
        if term == "":
            return messagebox.showerror("Lỗi", "Vui lòng nhập nội dung tìm kiếm", parent=self.root)

        search_column = self._get_search_column()
        entries = self._fetch_db_entries(search_column, term)
        if not entries and search_column == "invoice":
            entries = self._fetch_file_entries(term)

        if not entries:
            return messagebox.showerror("Lỗi", "Không tìm thấy hóa đơn phù hợp", parent=self.root)

        self._populate_sales_list(entries)


if __name__ == "__main__":
    root = Tk()
    obj = salesClass(root)
    root.mainloop()
