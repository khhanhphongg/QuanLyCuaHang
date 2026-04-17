"""Khởi tạo CSDL SQLite cho hệ thống quản lý bán hàng."""

import sqlite3
import hashlib


def hash_password(password: str) -> str:
    """Băm mật khẩu bằng SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def create_db(verbose=True):
    """Tạo bảng, index và tài khoản admin mặc định nếu chưa có."""
    con = sqlite3.connect(database=r'ims.db')
    cur = con.cursor()
    # Bảng nhân viên.
    cur.execute(
        "CREATE TABLE IF NOT EXISTS employee(eid text PRIMARY KEY, name text, email text, gender text, contact text, dob text, doj text, password text, utype text, address text, salary text)")
    # Bảng nhà cung cấp.
    cur.execute("CREATE TABLE IF NOT EXISTS supplier(invoice text PRIMARY KEY, name text, contact text, desc text)")
    # Bảng danh mục.
    cur.execute("CREATE TABLE IF NOT EXISTS category(cid INTEGER PRIMARY KEY AUTOINCREMENT, name text)")
    # Bảng sản phẩm (mở rộng: barcode, giá nhập, tồn kho tối thiểu, đơn vị, mô tả).
    cur.execute(
        "CREATE TABLE IF NOT EXISTS product(pid INTEGER PRIMARY KEY AUTOINCREMENT, Category text, Supplier text, name text, price text, qty text, status text, barcode text, cost_price real DEFAULT 0, min_qty integer DEFAULT 5, unit text DEFAULT 'Cái', description text DEFAULT '')")
    # Bảng hóa đơn: mã, ngày, khách, tổng tiền, giảm giá, thực thu.
    cur.execute(
        "CREATE TABLE IF NOT EXISTS bill(invoice text PRIMARY KEY, date text, cname text, contact text, amount text, discount text, net_pay text)")
    # Bảng chi tiết hoá đơn (bill items).
    cur.execute(
        "CREATE TABLE IF NOT EXISTS bill_item(id INTEGER PRIMARY KEY AUTOINCREMENT, invoice text, pid integer, name text, price text, qty text, total text, FOREIGN KEY(invoice) REFERENCES bill(invoice))")
    # Bảng khách hàng.
    cur.execute(
        "CREATE TABLE IF NOT EXISTS customer(cid INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, email TEXT, address TEXT, points INTEGER DEFAULT 0, created_at TEXT, updated_at TEXT)")
    # Index phục vụ tìm kiếm nhanh.
    cur.execute("CREATE INDEX IF NOT EXISTS idx_employee_email ON employee(email)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_employee_name ON employee(name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_employee_contact ON employee(contact)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_supplier_name ON supplier(name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_supplier_contact ON supplier(contact)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_category_name ON category(name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_product_name ON product(name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_product_category ON product(Category)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_product_supplier ON product(Supplier)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_product_barcode ON product(barcode)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_customer_name ON customer(name)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_customer_phone ON customer(phone)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_customer_email ON customer(email)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bill_invoice ON bill(invoice)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bill_cname ON bill(cname)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bill_contact ON bill(contact)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bill_date ON bill(date)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_bill_item_invoice ON bill_item(invoice)")
    # Bảng nhật ký hoạt động (Audit Log).
    cur.execute(
        "CREATE TABLE IF NOT EXISTS audit_log(id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, user TEXT, action TEXT, detail TEXT)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp)")

    # Migration: thêm cột mới cho DB cũ đã tồn tại.
    for col_def in [
        ("barcode", "text"),
        ("cost_price", "real DEFAULT 0"),
        ("min_qty", "integer DEFAULT 5"),
        ("unit", "text DEFAULT 'Cái'"),
        ("description", "text DEFAULT ''"),
    ]:
        try:
            cur.execute(f"ALTER TABLE product ADD COLUMN {col_def[0]} {col_def[1]}")
        except Exception:
            pass  # Cột đã tồn tại

    # Tạo tài khoản admin mặc định nếu chưa tồn tại.
    cur.execute("SELECT * FROM employee WHERE eid='NV01'")
    if cur.fetchone() is None:
        admin_pass = hash_password('123456')
        cur.execute(
            "INSERT INTO employee(eid,name,email,gender,contact,dob,doj,password,utype,address,salary) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            ('NV01', 'Admin Hệ Thống', 'admin@gmail.com', 'Nam', '0987654321', '01-01-2000', '01-01-2024', admin_pass,
             'Quản lý', 'Hà Nội', '10000000'))
        con.commit()
        if verbose:
            print("Đã tạo tài khoản Admin: NV01 / 123456")
    else:
        if verbose:
            print("Tài khoản Admin đã tồn tại.")

    con.commit()
    if verbose:
        print("Khởi tạo Cơ sở dữ liệu thành công!")


if __name__ == "__main__":
    create_db()
