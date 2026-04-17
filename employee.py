"""Màn hình quản lý nhân viên với đầy đủ chức năng CRUD và tìm kiếm."""

from tkinter import *
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
import sqlite3
import re
import hashlib
from ui_theme import COLORS, FONTS, apply_ttk_theme
from ui_scale import AutoScale
from search_suggest import SearchSuggest


def hash_password(password: str) -> str:
    """Băm mật khẩu bằng SHA-256."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def prepare_password_for_storage(password: str) -> str:
    """Tránh băm lặp nếu dữ liệu đang là SHA-256 hex."""
    if re.fullmatch(r"[0-9a-fA-F]{64}", password or ""):
        return (password or "").lower()
    return hash_password(password or "")


class employeeClass:
    """Quản lý dữ liệu nhân viên, tìm kiếm và điều hướng bằng bàn phím."""
    def __init__(self, root):
        self.root = root
        self.root.geometry("1100x600+220+130")
        self.root.title("Hệ thống Quản lý Cửa hàng Tiện lợi | Nhân viên")
        apply_ttk_theme()
        APP_BG = COLORS["bg"]
        CARD_BG = COLORS["surface"]
        CARD_BORDER = COLORS["border"]
        SOFT_BG = COLORS["input_bg"]
        SOFT_TEXT = COLORS["text"]
        TITLE_BG = COLORS["surface"]
        TITLE_FG = COLORS["text"]
        HEADER_BG = COLORS["surface"]
        HEADER_FG = COLORS["text"]
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
        FIELD_Y_OFFSET = 5
        BTN_FONT = FONTS["body_bold"]
        TABLE_HEAD_BG = COLORS["table_head"]
        TABLE_HEAD_FG = COLORS["text"]

        self.root.config(bg=APP_BG)
        self.root.focus_force()

        # Biến trạng thái cho form và tìm kiếm.
        self.var_searchBy = StringVar()
        self.var_searchtxt = StringVar()
        self.var_emp_id = StringVar()
        self.var_gender = StringVar()
        self.var_contact = StringVar()
        self.var_name = StringVar()
        self.var_dob = StringVar()
        self.var_doj = StringVar()
        self.var_email = StringVar()
        self.var_password = StringVar()
        self.var_utype = StringVar()
        self.var_salary = StringVar()

        # Header.
        try:
            self.icon_title = Image.open("Images/images/logo1.png")
            self.icon_title = self.icon_title.resize((50, 50), Image.LANCZOS)
            self.icon_title = ImageTk.PhotoImage(self.icon_title)
            title = Label(self.root, text="  QUẢN LÝ NGƯỜI DÙNG", image=self.icon_title, compound=LEFT,
                          font=FONTS["title_large"], bg=HEADER_BG, fg=HEADER_FG, anchor="w", padx=20).place(x=0, y=0,
                                                                                                             relwidth=1,
                                                                                                             height=70)
        except Exception as e:
            title = Label(self.root, text="  QUẢN LÝ NGƯỜI DÙNG", font=FONTS["title_large"], bg=HEADER_BG,
                          fg=HEADER_FG, anchor="w", padx=20).place(x=0, y=0, relwidth=1, height=70)
            print("Lỗi logo:", e)

        # Thanh tìm kiếm.
        SearchFrame = Frame(self.root, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER)
        SearchFrame.place(x=250, y=70, width=600, height=50)

        self.cmb_search = ttk.Combobox(SearchFrame, textvariable=self.var_searchBy,
                                  values=("Chọn mục...", "Email", "Tên", "SĐT"), state="readonly", justify=CENTER,
                                  font=FONTS["body"])
        self.cmb_search.place(x=30, y=10, width=150, height=30)
        self.cmb_search.current(0)

        self.txt_search = Entry(SearchFrame, textvariable=self.var_searchtxt, font=ENTRY_FONT, bg=ENTRY_BG,
                           highlightthickness=1, highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER, bd=0,
                           justify=CENTER)
        self.txt_search.place(x=190, y=10, width=250, height=30)
        self.txt_search.bind("<Return>", lambda e: self.search())

        btn_search = Button(SearchFrame, text="Tìm kiếm", command=self.search, font=BTN_FONT, bg=BTN_BLUE_BG,
                            fg=BTN_BLUE_FG, activebackground=BTN_BLUE_ACTIVE, activeforeground=BTN_BLUE_FG,
                            bd=1, relief=SOLID, cursor="hand2")
        btn_search.place(x=450, y=10, width=120, height=30)

        # Form nhập liệu.
        FrameContent = Frame(self.root, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER)
        FrameContent.place(x=50, y=130, width=1000, height=280)

        # Hàng 1.
        Label(FrameContent, text="Mã NV:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_FG).place(x=0, y=0)
        self.txt_emp_id = Entry(FrameContent, textvariable=self.var_emp_id, font=ENTRY_FONT, bg=ENTRY_BG,
                                highlightthickness=1, highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER,
                                bd=0)
        self.txt_emp_id.place(x=80, y=0 + FIELD_Y_OFFSET, width=180)

        Label(FrameContent, text="Giới tính:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_FG).place(x=330, y=0)
        self.cmb_gender = ttk.Combobox(FrameContent, textvariable=self.var_gender, values=("Chọn...", "Nam", "Nữ", "Khác"),
                                  state="readonly", justify=CENTER, font=ENTRY_FONT)
        self.cmb_gender.place(x=410, y=0 + FIELD_Y_OFFSET, width=180)
        self.cmb_gender.current(0)

        Label(FrameContent, text="SĐT:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_FG).place(x=660, y=0)
        self.txt_contact = Entry(FrameContent, textvariable=self.var_contact, font=ENTRY_FONT, bg=ENTRY_BG,
                                 highlightthickness=1, highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER,
                                 bd=0)
        self.txt_contact.place(x=750, y=0 + FIELD_Y_OFFSET, width=180)

        # Hàng 2.
        Label(FrameContent, text="Họ Tên:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_FG).place(x=0, y=50)
        self.txt_name = Entry(FrameContent, textvariable=self.var_name, font=ENTRY_FONT, bg=ENTRY_BG,
                              highlightthickness=1, highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER, bd=0)
        self.txt_name.place(x=80, y=50 + FIELD_Y_OFFSET, width=180)

        Label(FrameContent, text="Ngày sinh:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_FG).place(x=330, y=50)
        self.txt_dob = Entry(FrameContent, textvariable=self.var_dob, font=ENTRY_FONT, bg=ENTRY_BG,
                             highlightthickness=1, highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER, bd=0)
        self.txt_dob.place(x=410, y=50 + FIELD_Y_OFFSET, width=180)

        Label(FrameContent, text="Ngày vào:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_FG).place(x=660, y=50)
        self.txt_doj = Entry(FrameContent, textvariable=self.var_doj, font=ENTRY_FONT, bg=ENTRY_BG,
                             highlightthickness=1, highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER, bd=0)
        self.txt_doj.place(x=750, y=50 + FIELD_Y_OFFSET, width=180)

        # Hàng 3.
        Label(FrameContent, text="Email:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_FG).place(x=0, y=100)
        self.txt_email = Entry(FrameContent, textvariable=self.var_email, font=ENTRY_FONT, bg=ENTRY_BG,
                               highlightthickness=1, highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER, bd=0)
        self.txt_email.place(x=80, y=100 + FIELD_Y_OFFSET, width=180)

        Label(FrameContent, text="Mật khẩu:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_FG).place(x=330, y=100)
        self.txt_pass = Entry(FrameContent, textvariable=self.var_password, font=ENTRY_FONT, bg=ENTRY_BG,
                              highlightthickness=1, highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER, bd=0)
        self.txt_pass.place(x=410, y=100 + FIELD_Y_OFFSET, width=180)

        Label(FrameContent, text="Vai trò:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_FG).place(x=660, y=100)
        self.cmb_utype = ttk.Combobox(FrameContent, textvariable=self.var_utype, values=("Chọn...", "Quản lý", "Nhân viên"),
                                 state="readonly", justify=CENTER, font=ENTRY_FONT)
        self.cmb_utype.place(x=750, y=100 + FIELD_Y_OFFSET, width=180)
        self.cmb_utype.current(0)

        # Hàng 4.
        Label(FrameContent, text="Địa chỉ:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_FG).place(x=0, y=150)
        self.txt_address = Text(FrameContent, font=ENTRY_FONT, bg=ENTRY_BG, highlightthickness=1,
                                highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER, bd=0)
        self.txt_address.place(x=80, y=150 + FIELD_Y_OFFSET, width=510, height=60)

        Label(FrameContent, text="Lương:", font=LBL_FONT, bg=CARD_BG, fg=TITLE_FG).place(x=660, y=150)
        self.txt_salary = Entry(FrameContent, textvariable=self.var_salary, font=ENTRY_FONT, bg=ENTRY_BG,
                                highlightthickness=1, highlightbackground=CARD_BORDER, highlightcolor=CARD_BORDER,
                                bd=0)
        self.txt_salary.place(x=750, y=150 + FIELD_Y_OFFSET, width=180)

        # Nút thao tác.
        FrameBtns = Frame(FrameContent, bg=CARD_BG)
        FrameBtns.place(x=80, y=230, width=600, height=40)

        btn_save = Button(FrameBtns, text="Lưu", command=self.add, font=BTN_FONT, bg=BTN_GREEN_BG, fg=BTN_GREEN_FG,
                          activebackground=BTN_GREEN_ACTIVE, activeforeground=BTN_GREEN_FG, bd=1, relief=SOLID,
                          cursor="hand2").pack(side=LEFT, expand=True, fill=X, padx=5)
        btn_update = Button(FrameBtns, text="Cập nhật", command=self.update, font=BTN_FONT, bg=BTN_BLUE_BG,
                            fg=BTN_BLUE_FG, activebackground=BTN_BLUE_ACTIVE, activeforeground=BTN_BLUE_FG,
                            bd=1, relief=SOLID, cursor="hand2").pack(side=LEFT, expand=True, fill=X, padx=5)
        btn_delete = Button(FrameBtns, text="Xóa", command=self.delete, font=BTN_FONT, bg=BTN_RED_BG, fg=BTN_RED_FG,
                            activebackground=BTN_RED_ACTIVE, activeforeground=BTN_RED_FG, bd=1, relief=SOLID,
                            cursor="hand2").pack(side=LEFT, expand=True, fill=X, padx=5)
        btn_clear = Button(FrameBtns, text="Làm mới", command=self.clear, font=BTN_FONT, bg=BTN_YELLOW_BG,
                           fg=BTN_YELLOW_FG, activebackground=BTN_YELLOW_ACTIVE,
                           activeforeground=BTN_YELLOW_FG, bd=1, relief=SOLID, cursor="hand2").pack(side=LEFT, expand=True, fill=X, padx=5)

        # Bảng danh sách nhân viên.
        emp_frame = Frame(self.root, bd=0, bg=CARD_BG, highlightthickness=1, highlightbackground=CARD_BORDER)
        emp_frame.place(x=0, y=420, relwidth=1, height=180)

        scrolly = Scrollbar(emp_frame, orient=VERTICAL)
        scrollx = Scrollbar(emp_frame, orient=HORIZONTAL)

        self.EmployeeTable = ttk.Treeview(emp_frame, columns=("eid", "name", "gender", "email", "contact", "dob", "doj",
                                                              "password", "utype", "address", "salary"),
                                          yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
        scrollx.pack(side=BOTTOM, fill=X)
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.config(command=self.EmployeeTable.xview)
        scrolly.config(command=self.EmployeeTable.yview)

        self.EmployeeTable.heading("eid", text="Mã NV", anchor=CENTER)
        self.EmployeeTable.heading("name", text="Họ Tên", anchor=CENTER)
        self.EmployeeTable.heading("gender", text="Giới tính", anchor=CENTER)
        self.EmployeeTable.heading("email", text="Email", anchor=CENTER)
        self.EmployeeTable.heading("contact", text="SĐT", anchor=CENTER)
        self.EmployeeTable.heading("dob", text="Ngày sinh", anchor=CENTER)
        self.EmployeeTable.heading("doj", text="Ngày vào", anchor=CENTER)
        self.EmployeeTable.heading("password", text="Mật khẩu", anchor=CENTER)
        self.EmployeeTable.heading("utype", text="Vai trò", anchor=CENTER)
        self.EmployeeTable.heading("address", text="Địa chỉ", anchor=CENTER)
        self.EmployeeTable.heading("salary", text="Lương", anchor=CENTER)

        self.EmployeeTable["show"] = "headings"

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=FONTS["table_heading"], background=TABLE_HEAD_BG,
                        foreground=TABLE_HEAD_FG, relief="flat")
        style.configure("Treeview", font=FONTS["table"], background=CARD_BG, fieldbackground=CARD_BG, rowheight=28)
        style.map('Treeview', background=[('selected', COLORS["row_selected"])], foreground=[('selected', TITLE_FG)])
        style.configure("TCombobox", padding=2, foreground=TITLE_FG, fieldbackground=SOFT_BG, background=SOFT_BG)

        self.EmployeeTable.column("eid", width=90, anchor=CENTER)
        self.EmployeeTable.column("name", anchor=CENTER)
        self.EmployeeTable.column("gender", anchor=CENTER)
        self.EmployeeTable.column("email", anchor=CENTER)
        self.EmployeeTable.column("contact", anchor=CENTER)
        self.EmployeeTable.column("dob", anchor=CENTER)
        self.EmployeeTable.column("doj", anchor=CENTER)
        self.EmployeeTable.column("password", anchor=CENTER)
        self.EmployeeTable.column("utype", anchor=CENTER)
        self.EmployeeTable.column("address", anchor=CENTER)
        self.EmployeeTable.column("salary", anchor=CENTER)
        self.EmployeeTable.pack(fill=BOTH, expand=1)
        self.EmployeeTable.bind("<ButtonRelease-1>", self.get_data)

        # Ảnh minh họa.
        try:
            self.im_emp = Image.open("Images/images/im2.png")
            self.im_emp = self.im_emp.resize((100, 100), Image.LANCZOS)
            self.im_emp = ImageTk.PhotoImage(self.im_emp)
            lbl_emp_img = Label(self.root, image=self.im_emp, bg=CARD_BG, bd=0)
            lbl_emp_img.place(x=850, y=310)
        except Exception as e:
            print("Lỗi im2.png:", e)

        # Điều hướng bằng Enter và phím mũi tên theo bố cục form.
        try:
            self.txt_emp_id.bind('<Return>', lambda e: self.txt_name.focus())
            self.txt_emp_id.bind('<Down>', lambda e: self.txt_name.focus())
            self.txt_emp_id.bind('<Right>', lambda e: self.cmb_gender.focus())

            self.cmb_gender.bind('<Return>', lambda e: self.txt_contact.focus())
            self.cmb_gender.bind('<Right>', lambda e: self.txt_contact.focus())
            self.cmb_gender.bind('<Left>', lambda e: self.txt_emp_id.focus())

            self.txt_contact.bind('<Return>', lambda e: self.txt_doj.focus())
            self.txt_contact.bind('<Down>', lambda e: self.txt_doj.focus())
            self.txt_contact.bind('<Left>', lambda e: self.cmb_gender.focus())

            self.txt_name.bind('<Return>', lambda e: self.txt_email.focus())
            self.txt_name.bind('<Up>', lambda e: self.txt_emp_id.focus())
            self.txt_name.bind('<Down>', lambda e: self.txt_email.focus())
            self.txt_name.bind('<Right>', lambda e: self.txt_dob.focus())

            self.txt_dob.bind('<Return>', lambda e: self.txt_pass.focus())
            self.txt_dob.bind('<Up>', lambda e: self.cmb_gender.focus())
            self.txt_dob.bind('<Down>', lambda e: self.txt_pass.focus())
            self.txt_dob.bind('<Left>', lambda e: self.txt_name.focus())
            self.txt_dob.bind('<Right>', lambda e: self.txt_doj.focus())

            self.txt_doj.bind('<Return>', lambda e: self.cmb_utype.focus())
            self.txt_doj.bind('<Up>', lambda e: self.txt_contact.focus())
            self.txt_doj.bind('<Down>', lambda e: self.cmb_utype.focus())
            self.txt_doj.bind('<Left>', lambda e: self.txt_dob.focus())

            self.txt_email.bind('<Return>', lambda e: self.txt_address.focus())
            self.txt_email.bind('<Up>', lambda e: self.txt_name.focus())
            self.txt_email.bind('<Down>', lambda e: self.txt_address.focus())
            self.txt_email.bind('<Right>', lambda e: self.txt_pass.focus())

            self.txt_pass.bind('<Return>', lambda e: self.txt_address.focus())
            self.txt_pass.bind('<Up>', lambda e: self.txt_dob.focus())
            self.txt_pass.bind('<Down>', lambda e: self.txt_address.focus())
            self.txt_pass.bind('<Left>', lambda e: self.txt_email.focus())
            self.txt_pass.bind('<Right>', lambda e: self.cmb_utype.focus())

            self.cmb_utype.bind('<Return>', lambda e: self.txt_salary.focus())
            self.cmb_utype.bind('<Left>', lambda e: self.txt_pass.focus())

            self.txt_address.bind('<Return>', lambda e: self.txt_salary.focus())
            self.txt_address.bind('<Up>', lambda e: self.txt_email.focus())
            self.txt_address.bind('<Right>', lambda e: self.txt_salary.focus())
            self.txt_address.bind('<Down>', lambda e: self.txt_salary.focus())

            self.txt_salary.bind('<Up>', lambda e: self.cmb_utype.focus())
            self.txt_salary.bind('<Left>', lambda e: self.txt_address.focus())
            self.txt_salary.bind('<Return>', lambda e: self.add())

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

        self.scaler = AutoScale(self.root, 1100, 600)

    def _get_search_column(self):
        """Ánh xạ tiêu chí tìm kiếm sang cột trong DB."""
        return {
            "Email": "email",
            "Tên": "name",
            "SĐT": "contact",
        }.get(self.var_searchBy.get())

    def _fetch_search_suggestions(self, term):
        """Lấy gợi ý tìm kiếm nhân viên theo tiền tố."""
        db_column = self._get_search_column()
        if not db_column:
            return []

        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute(
                f"SELECT DISTINCT {db_column} FROM employee "
                f"WHERE {db_column} LIKE ? "
                f"ORDER BY {db_column} LIMIT 8",
                (f"{term}%",)
            )
            return [row[0] for row in cur.fetchall() if row[0]]
        finally:
            con.close()

    def _apply_search_suggestion(self, value):
        """Đổ gợi ý vào ô tìm kiếm và lọc ngay."""
        self.var_searchtxt.set(value)
        self.search()

    def add(self):
        """Thêm nhân viên mới với kiểm tra dữ liệu đầu vào."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if self.var_emp_id.get() == "":
                messagebox.showerror("Lỗi", "Vui lòng nhập Mã Nhân viên", parent=self.root)
            elif self.var_name.get().strip() == "":
                messagebox.showerror("Lỗi", "Vui lòng nhập Họ tên", parent=self.root)
            elif self.var_gender.get() == "Chọn...":
                messagebox.showerror("Lỗi", "Vui lòng chọn Giới tính", parent=self.root)
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", self.var_email.get()):
                messagebox.showerror("Lỗi", "Định dạng Email không hợp lệ!", parent=self.root)
            elif not re.match(r"^\d{10,11}$", self.var_contact.get()):
                messagebox.showerror("Lỗi", "Số điện thoại phải là 10-11 chữ số!", parent=self.root)
            elif self.var_password.get().strip() == "":
                messagebox.showerror("Lỗi", "Vui lòng nhập Mật khẩu", parent=self.root)
            elif self.var_utype.get() == "Chọn...":
                messagebox.showerror("Lỗi", "Vui lòng chọn Vai trò", parent=self.root)
            else:
                cur.execute("Select * from employee WHERE eid = ?", (self.var_emp_id.get(),))
                row = cur.fetchone()
                if row != None:
                    messagebox.showerror("Lỗi", "Mã Nhân viên đã tồn tại", parent=self.root)
                else:
                    stored_password = prepare_password_for_storage(self.var_password.get().strip())
                    cur.execute(
                        "Insert into employee(eid,name,gender,email,contact,dob,doj,password,utype,address,salary) values(?,?,?,?,?,?,?,?,?,?,?)",
                        (
                            self.var_emp_id.get(),
                            self.var_name.get(),
                            self.var_gender.get(),
                            self.var_email.get(),
                            self.var_contact.get(),
                            self.var_dob.get(),
                            self.var_doj.get(),
                            stored_password,
                            self.var_utype.get(),
                            self.txt_address.get('1.0', END),
                            self.var_salary.get(),
                        ))
                    con.commit()
                    messagebox.showinfo("Thành công", "Thêm nhân viên thành công", parent=self.root)
                    self.show()
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def show(self):
        """Tải lại bảng nhân viên."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute("Select eid,name,gender,email,contact,dob,doj,password,utype,address,salary from employee")
            rows = cur.fetchall()
            self.EmployeeTable.delete(*self.EmployeeTable.get_children())
            for row in rows:
                self.EmployeeTable.insert('', END, values=row)
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hiển thị: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def get_data(self, ev):
        """Đổ dữ liệu từ bảng vào form."""
        f = self.EmployeeTable.focus()
        content = (self.EmployeeTable.item(f))
        row = content['values']
        if not row:
            return
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            cur.execute(
                "Select eid,name,gender,email,contact,dob,doj,password,utype,address,salary from employee WHERE eid=?",
                (row[0],)
            )
            db_row = cur.fetchone()
            if not db_row:
                return
            self.var_emp_id.set(db_row[0])
            self.var_name.set(db_row[1])
            self.var_gender.set(db_row[2])
            self.var_email.set(db_row[3])
            self.var_contact.set(db_row[4] if db_row[4] is not None else "")
            self.var_dob.set(db_row[5])
            self.var_doj.set(db_row[6])
            self.var_password.set(db_row[7])
            self.var_utype.set(db_row[8])
            self.txt_address.delete('1.0', END)
            self.txt_address.insert(END, db_row[9] if db_row[9] else "")
            self.var_salary.set(db_row[10])
        finally:
            con.close()

    def update(self):
        """Cập nhật thông tin nhân viên đã chọn."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if self.var_emp_id.get() == "":
                messagebox.showerror("Lỗi", "Cần có Mã Nhân viên để cập nhật", parent=self.root)
            elif self.var_name.get().strip() == "":
                messagebox.showerror("Lỗi", "Vui lòng nhập Họ tên", parent=self.root)
            elif self.var_gender.get() == "Chọn...":
                messagebox.showerror("Lỗi", "Vui lòng chọn Giới tính", parent=self.root)
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", self.var_email.get()):
                messagebox.showerror("Lỗi", "Định dạng Email không hợp lệ!", parent=self.root)
            elif not re.match(r"^\d{10,11}$", self.var_contact.get()):
                messagebox.showerror("Lỗi", "Số điện thoại phải là 10-11 chữ số!", parent=self.root)
            elif self.var_password.get().strip() == "":
                messagebox.showerror("Lỗi", "Vui lòng nhập Mật khẩu", parent=self.root)
            elif self.var_utype.get() == "Chọn...":
                messagebox.showerror("Lỗi", "Vui lòng chọn Vai trò", parent=self.root)
            else:
                cur.execute("Select * from employee WHERE eid = ?", (self.var_emp_id.get(),))
                row = cur.fetchone()
                if row == None:
                    messagebox.showerror("Lỗi", "Mã Nhân viên không tồn tại", parent=self.root)
                else:
                    stored_password = prepare_password_for_storage(self.var_password.get().strip())
                    cur.execute(
                        "update employee set name=?,gender=?,email=?,contact=?,dob=?,doj=?,password=?,utype=?,address=?,salary=? WHERE eid = ?",
                        (
                            self.var_name.get(),
                            self.var_gender.get(),
                            self.var_email.get(),
                            self.var_contact.get(),
                            self.var_dob.get(),
                            self.var_doj.get(),
                            stored_password,
                            self.var_utype.get(),
                            self.txt_address.get('1.0', END),
                            self.var_salary.get(),
                            self.var_emp_id.get(),
                        ))
                    con.commit()
                    messagebox.showinfo("Thành công", "Cập nhật thông tin thành công", parent=self.root)
                    self.show()
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def delete(self):
        """Xoá nhân viên theo mã."""
        con = sqlite3.connect(database=r'ims.db')
        cur = con.cursor()
        try:
            if self.var_emp_id.get() == "":
                messagebox.showerror("Lỗi", "Vui lòng chọn nhân viên cần xóa", parent=self.root)
            else:
                cur.execute("Select * from employee WHERE eid = ?", (self.var_emp_id.get(),))
                row = cur.fetchone()
                if row == None:
                    messagebox.showerror("Lỗi", "Nhân viên không tồn tại", parent=self.root)
                else:
                    op = messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa nhân viên này?", parent=self.root)
                    if op == True:
                        cur.execute("delete from employee where eid=?", (self.var_emp_id.get(),))
                        con.commit()
                        messagebox.showinfo("Đã xóa", "Xóa thành công", parent=self.root)
                        self.clear()
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()

    def clear(self):
        """Làm mới form và trạng thái tìm kiếm."""
        self.var_emp_id.set("")
        self.var_name.set("")
        self.var_gender.set("Chọn...")
        self.var_email.set("")
        self.var_contact.set("")
        self.var_dob.set("")
        self.var_doj.set("")
        self.var_password.set("")
        self.var_utype.set("Chọn...")
        self.txt_address.delete('1.0', END)
        self.var_salary.set("")
        self.var_searchtxt.set("")
        self.var_searchBy.set("Chọn mục...")
        if hasattr(self, "search_suggest"):
            self.search_suggest.hide()
        self.show()

    def search(self):
        """Tìm nhân viên theo Email/Tên/SĐT."""
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
                    "Select eid,name,gender,email,contact,dob,doj,password,utype,address,salary "
                    "from employee WHERE " + db_column + " LIKE ?",
                    (search_value,))
                rows = cur.fetchall()
                if len(rows) != 0:
                    self.EmployeeTable.delete(*self.EmployeeTable.get_children())
                    for row in rows:
                        self.EmployeeTable.insert('', END, values=row)
                else:
                    messagebox.showerror("Lỗi", "Không tìm thấy kết quả", parent=self.root)
        except Exception as ex:
            messagebox.showerror("Lỗi", f"Lỗi hệ thống: {str(ex)}", parent=self.root)
        finally:
            con.close()


if __name__ == "__main__":
    root = Tk()
    obj = employeeClass(root)
    root.mainloop()
