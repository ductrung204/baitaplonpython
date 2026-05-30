import mysql.connector

print("🔌 Đang kết nối MySQL...")

# Kết nối MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)

cursor = conn.cursor()

# Xóa database cũ nếu có
cursor.execute("DROP DATABASE IF EXISTS car_dealership")
cursor.execute("CREATE DATABASE car_dealership")
cursor.execute("USE car_dealership")

print("✅ Đã tạo database car_dealership")

# ========== TẠO CÁC BẢNG ==========

# 1. Bảng XE
cursor.execute("""
CREATE TABLE cars (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    brand VARCHAR(50) NOT NULL,
    year INT NOT NULL,
    import_price BIGINT NOT NULL,
    sell_price BIGINT NOT NULL,
    quantity INT NOT NULL DEFAULT 0
)
""")

# 2. Bảng KHÁCH HÀNG
cursor.execute("""
CREATE TABLE customers (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    address VARCHAR(200),
    email VARCHAR(100),
    total_spent BIGINT DEFAULT 0
)
""")

# 3. Bảng NHÂN VIÊN
cursor.execute("""
CREATE TABLE employees (
    id VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(32) NOT NULL,
    role VARCHAR(20) DEFAULT 'staff'
)
""")

# 4. Bảng HÓA ĐƠN
cursor.execute("""
CREATE TABLE invoices (
    id VARCHAR(10) PRIMARY KEY,
    customer_id VARCHAR(10),
    employee_id VARCHAR(10),
    datetime DATETIME NOT NULL,
    total BIGINT NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (employee_id) REFERENCES employees(id)
)
""")

# 5. Bảng CHI TIẾT HÓA ĐƠN
cursor.execute("""
CREATE TABLE invoice_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    invoice_id VARCHAR(10),
    car_id VARCHAR(10),
    quantity INT NOT NULL,
    price BIGINT NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(id),
    FOREIGN KEY (car_id) REFERENCES cars(id)
)
""")

# 6. Bảng ĐẶT CỌC (THÊM MỚI)
cursor.execute("""
CREATE TABLE deposits (
    id VARCHAR(10) PRIMARY KEY,
    customer_id VARCHAR(10),
    car_id VARCHAR(10),
    deposit_amount BIGINT NOT NULL,
    remaining_amount BIGINT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    deposit_date DATETIME NOT NULL,
    expected_delivery_date DATE,
    note TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (car_id) REFERENCES cars(id)
)
""")

print("✅ Đã tạo các bảng (cars, customers, employees, invoices, invoice_details, deposits)")

# ========== THÊM DỮ LIỆU MẪU ==========

# Thêm tài khoản admin
cursor.execute("DELETE FROM employees WHERE id='ADMIN01'")
cursor.execute("""
INSERT INTO employees (id, name, username, password, role)
VALUES ('ADMIN01', 'Quản trị viên', 'admin', MD5('admin123'), 'admin')
""")

# Xóa dữ liệu cũ
cursor.execute("DELETE FROM cars")
cursor.execute("DELETE FROM customers")

# Thêm dữ liệu mẫu - XE
cars_data = [
    ('TOY001', 'Toyota Camry 2.5Q', 'Toyota', 2024, 950000000, 1150000000, 10),
    ('HON001', 'Honda Civic RS', 'Honda', 2024, 720000000, 880000000, 15),
    ('MAZ001', 'Mazda 3 Premium', 'Mazda', 2024, 620000000, 750000000, 12),
    ('KIA001', 'KIA K3 GT', 'KIA', 2024, 530000000, 650000000, 10),
    ('HYU001', 'Hyundai Elantra', 'Hyundai', 2024, 590000000, 720000000, 12),
    ('LAM001', 'Lamborghini Huracán EVO', 'Lamborghini', 2024, 18000000000, 22000000000, 3),
    ('FER001', 'Ferrari SF90 Stradale', 'Ferrari', 2024, 25000000000, 30000000000, 2),
    ('POR001', 'Porsche 911 Turbo S', 'Porsche', 2024, 12000000000, 15000000000, 5)
]

for car in cars_data:
    cursor.execute("""
        INSERT INTO cars (id, name, brand, year, import_price, sell_price, quantity)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, car)

# Thêm dữ liệu mẫu - KHÁCH HÀNG
customers_data = [
    ('VIP001', 'Nguyễn Văn An', '0901111222', 'Hà Nội', 'an@luxury.com', 0),
    ('VIP002', 'Trần Thị Bảo', '0902222333', 'TP.HCM', 'bao@luxury.com', 0),
    ('VIP003', 'Lê Hoàng Cường', '0903333444', 'Đà Nẵng', 'cuong@luxury.com', 0),
    ('VIP004', 'Phạm Minh Đức', '0904444555', 'Hải Phòng', 'duc@luxury.com', 0),
    ('VIP005', 'Ngô Thị Hoa', '0905555666', 'Nha Trang', 'hoa@luxury.com', 0)
]

for cus in customers_data:
    cursor.execute("""
        INSERT INTO customers (id, name, phone, address, email, total_spent)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, cus)

conn.commit()
print("✅ Đã thêm dữ liệu mẫu (xe, khách hàng, admin)")

# ========== KIỂM TRA ==========
cursor.execute("SELECT COUNT(*) FROM cars")
car_count = cursor.fetchone()[0]
print(f"\n📋 Số xe trong database: {car_count}")

cursor.execute("SELECT COUNT(*) FROM customers")
cus_count = cursor.fetchone()[0]
print(f"👥 Số khách hàng: {cus_count}")

cursor.execute("SELECT COUNT(*) FROM employees")
emp_count = cursor.fetchone()[0]
print(f"👤 Số nhân viên: {emp_count}")

cursor.execute("SELECT COUNT(*) FROM deposits")
dep_count = cursor.fetchone()[0]
print(f"💰 Số đơn đặt cọc: {dep_count}")

print("\n🚗 Danh sách xe:")
cursor.execute("SELECT id, name, sell_price FROM cars")
for row in cursor.fetchall():
    print(f"   {row[0]} - {row[1]} - {row[2]:,}đ")

cursor.close()
conn.close()

print("\n✅ ĐÃ TẠO DATABASE THÀNH CÔNG!")
print("🔐 Tài khoản đăng nhập: admin / admin123")
print("🌐 Địa chỉ web: http://localhost:5000")
print("\n📌 Tính năng mới: ĐẶT CỌC XE - Nhận xe sau")