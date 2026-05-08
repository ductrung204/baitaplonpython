import json
import os
from datetime import datetime
import hashlib

# ==================== TẠO THƯ MỤC ====================
def create_folders():
    folders = ['data', 'backups', 'invoices']
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"✅ Đã tạo thư mục: {folder}")

create_folders()

# ==================== QUẢN LÝ DỮ LIỆU ====================
class DataManager:
    def __init__(self):
        self.data_dir = "data"
        self.load_all_data()
    
    def load_all_data(self):
        """Tải tất cả dữ liệu"""
        self.cars = self.load_file("cars.json")
        self.customers = self.load_file("customers.json")
        self.employees = self.load_file("employees.json")
        self.invoices = self.load_file("invoices.json")
        
        # Tạo tài khoản admin mặc định
        if not self.employees:
            default_admin = {
                "id": "ADMIN01",
                "name": "Quản trị viên",
                "username": "admin",
                "password": hashlib.md5("admin123".encode()).hexdigest(),
                "role": "admin"
            }
            self.employees.append(default_admin)
            self.save_file("employees.json", self.employees)
            print("✅ Đã tạo tài khoản admin: admin / admin123")
    
    def load_file(self, filename):
        """Đọc file JSON"""
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_file(self, filename, data):
        """Ghi file JSON"""
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    def save_all(self):
        """Lưu tất cả dữ liệu"""
        self.save_file("cars.json", self.cars)
        self.save_file("customers.json", self.customers)
        self.save_file("employees.json", self.employees)
        self.save_file("invoices.json", self.invoices)

# ==================== HỆ THỐNG ĐĂNG NHẬP ====================
class LoginSystem:
    def __init__(self, data_manager):
        self.dm = data_manager
    
    def login(self):
        print("\n" + "="*50)
        print("       🚗 QUẢN LÝ ĐẠI LÝ XE HƠI 🚗")
        print("="*50)
        print("              ĐĂNG NHẬP HỆ THỐNG")
        print("-"*50)
        
        username = input("  👤 Tên đăng nhập: ").strip()
        password = input("  🔐 Mật khẩu: ").strip()
        
        hashed_password = hashlib.md5(password.encode()).hexdigest()
        
        for emp in self.dm.employees:
            if emp['username'] == username and emp['password'] == hashed_password:
                print(f"\n✅ ĐĂNG NHẬP THÀNH CÔNG!")
                print(f"   Chào mừng: {emp['name']}")
                input("\nNhấn Enter để tiếp tục...")
                return emp
        
        print("\n❌ SAI TÊN ĐĂNG NHẬP HOẶC MẬT KHẨU!")
        return None

# ==================== QUẢN LÝ XE ====================
class CarManager:
    def __init__(self, data_manager):
        self.dm = data_manager
    
    def add_car(self):
        print("\n" + "="*50)
        print("        ➕ THÊM XE MỚI")
        print("="*50)
        
        car_id = input("  Mã xe (VD: XE001): ").strip().upper()
        
        # Kiểm tra trùng mã
        for car in self.dm.cars:
            if car['id'] == car_id:
                print("  ❌ Mã xe đã tồn tại!")
                return
        
        car_name = input("  Tên xe: ").strip()
        brand = input("  Hãng xe: ").strip()
        year = int(input("  Năm sản xuất: "))
        import_price = float(input("  Giá nhập (VNĐ): "))
        sell_price = float(input("  Giá bán (VNĐ): "))
        quantity = int(input("  Số lượng: "))
        
        # Kiểm tra giá
        if sell_price <= import_price:
            print("  ⚠️ Giá bán phải lớn hơn giá nhập!")
            confirm = input("  Vẫn muốn thêm? (y/n): ").lower()
            if confirm != 'y':
                return
        
        new_car = {
            "id": car_id,
            "name": car_name,
            "brand": brand,
            "year": year,
            "import_price": import_price,
            "sell_price": sell_price,
            "quantity": quantity
        }
        
        self.dm.cars.append(new_car)
        self.dm.save_all()
        print(f"\n  ✅ Đã thêm xe {car_name} thành công!")
    
    def view_cars(self):
        print("\n" + "="*60)
        print("              📋 DANH SÁCH XE")
        print("="*60)
        
        if not self.dm.cars:
            print("  📭 Chưa có xe nào!")
        else:
            print(f"{'Mã':<8} {'Tên xe':<20} {'Hãng':<12} {'Giá bán':<15} {'Tồn':<6}")
            print("-"*60)
            for car in self.dm.cars:
                print(f"{car['id']:<8} {car['name']:<20} {car['brand']:<12} {car['sell_price']:>12,.0f}đ {car['quantity']:>4}")
        print("="*60)
    
    def search_car(self):
        print("\n" + "="*50)
        print("        🔍 TÌM KIẾM XE")
        print("="*50)
        
        keyword = input("  Nhập tên xe hoặc hãng cần tìm: ").strip().lower()
        
        results = []
        for car in self.dm.cars:
            if keyword in car['name'].lower() or keyword in car['brand'].lower():
                results.append(car)
        
        if not results:
            print("  ❌ Không tìm thấy xe nào!")
        else:
            print(f"\n  📌 Tìm thấy {len(results)} xe:")
            for car in results:
                print(f"     - {car['id']}: {car['name']} - {car['brand']} - {car['sell_price']:,.0f}đ")
        
        input("\nNhấn Enter để tiếp tục...")
    
    def delete_car(self):
        print("\n" + "="*50)
        print("        🗑️ XÓA XE")
        print("="*50)
        
        car_id = input("  Nhập mã xe cần xóa: ").strip().upper()
        
        car_to_delete = None
        for car in self.dm.cars:
            if car['id'] == car_id:
                car_to_delete = car
                break
        
        if not car_to_delete:
            print("  ❌ Không tìm thấy xe!")
            return
        
        print(f"\n  Xe: {car_to_delete['name']} - {car_to_delete['brand']}")
        confirm = input("  Nhập 'YES' để xác nhận xóa: ")
        
        if confirm == "YES":
            self.dm.cars.remove(car_to_delete)
            self.dm.save_all()
            print("  ✅ Đã xóa xe thành công!")
        else:
            print("  Đã hủy thao tác xóa!")

# ==================== QUẢN LÝ KHÁCH HÀNG ====================
class CustomerManager:
    def __init__(self, data_manager):
        self.dm = data_manager
    
    def add_customer(self):
        print("\n" + "="*50)
        print("        👤 THÊM KHÁCH HÀNG")
        print("="*50)
        
        cus_id = input("  Mã KH (VD: KH001): ").strip().upper()
        
        for cus in self.dm.customers:
            if cus['id'] == cus_id:
                print("  ❌ Mã khách hàng đã tồn tại!")
                return
        
        name = input("  Họ tên: ").strip()
        phone = input("  Số điện thoại: ").strip()
        address = input("  Địa chỉ: ").strip()
        email = input("  Email: ").strip()
        
        new_customer = {
            "id": cus_id,
            "name": name,
            "phone": phone,
            "address": address,
            "email": email,
            "total_spent": 0
        }
        
        self.dm.customers.append(new_customer)
        self.dm.save_all()
        print(f"\n  ✅ Đã thêm khách hàng {name} thành công!")
    
    def view_customers(self):
        print("\n" + "="*60)
        print("            👥 DANH SÁCH KHÁCH HÀNG")
        print("="*60)
        
        if not self.dm.customers:
            print("  📭 Chưa có khách hàng nào!")
        else:
            print(f"{'Mã':<8} {'Họ tên':<20} {'SĐT':<12} {'Địa chỉ':<20}")
            print("-"*60)
            for cus in self.dm.customers:
                print(f"{cus['id']:<8} {cus['name']:<20} {cus['phone']:<12} {cus['address']:<20}")
        print("="*60)

# ==================== QUẢN LÝ HÓA ĐƠN ====================
class InvoiceManager:
    def __init__(self, data_manager, car_manager, customer_manager):
        self.dm = data_manager
        self.car_manager = car_manager
        self.customer_manager = customer_manager
    
    def create_invoice(self):
        print("\n" + "="*50)
        print("        🧾 TẠO HÓA ĐƠN MỚI")
        print("="*50)
        
        # Hiển thị danh sách khách hàng
        self.customer_manager.view_customers()
        cus_id = input("\n  Nhập mã khách hàng: ").strip().upper()
        
        customer = None
        for c in self.dm.customers:
            if c['id'] == cus_id:
                customer = c
                break
        
        if not customer:
            print("  ❌ Không tìm thấy khách hàng!")
            return
        
        # Hiển thị danh sách xe
        self.car_manager.view_cars()
        car_id = input("\n  Nhập mã xe muốn mua: ").strip().upper()
        
        car = None
        for c in self.dm.cars:
            if c['id'] == car_id:
                car = c
                break
        
        if not car:
            print("  ❌ Không tìm thấy xe!")
            return
        
        if car['quantity'] <= 0:
            print("  ❌ Xe đã hết hàng!")
            return
        
        quantity = int(input(f"  Số lượng (tồn: {car['quantity']}): "))
        
        if quantity > car['quantity']:
            print("  ❌ Số lượng không đủ!")
            return
        
        # Tính tổng tiền
        total = quantity * car['sell_price']
        
        # Tạo hóa đơn
        invoice_id = f"HD{len(self.dm.invoices)+1:04d}"
        
        invoice = {
            "id": invoice_id,
            "customer_id": cus_id,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": [{"car_id": car_id, "quantity": quantity, "price": car['sell_price']}],
            "total": total
        }
        
        self.dm.invoices.append(invoice)
        
        # Cập nhật tồn kho
        car['quantity'] -= quantity
        
        # Cập nhật tổng chi tiêu của khách
        customer['total_spent'] += total
        
        self.dm.save_all()
        
        print(f"\n  ✅ TẠO HÓA ĐƠN THÀNH CÔNG!")
        print(f"  📄 Mã HD: {invoice_id}")
        print(f"  💰 Tổng tiền: {total:,.0f}đ")
        
        # Lưu hóa đơn ra file
        self.save_invoice_to_file(invoice, customer, car)
    
    def save_invoice_to_file(self, invoice, customer, car):
        filename = f"invoices/{invoice['id']}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*50 + "\n")
            f.write("         HÓA ĐƠN BÁN XE\n")
            f.write("="*50 + "\n")
            f.write(f"Số HD: {invoice['id']}\n")
            f.write(f"Ngày: {invoice['date']}\n")
            f.write(f"Khách hàng: {customer['name']}\n")
            f.write("-"*50 + "\n")
            f.write(f"Xe: {car['name']} - {car['brand']}\n")
            f.write(f"Số lượng: {invoice['items'][0]['quantity']}\n")
            f.write(f"Đơn giá: {car['sell_price']:,.0f}đ\n")
            f.write("-"*50 + "\n")
            f.write(f"TỔNG TIỀN: {invoice['total']:,.0f}đ\n")
            f.write("="*50 + "\n")
            f.write("Cảm ơn quý khách! Hẹn gặp lại!\n")
        
        print(f"  📁 Hóa đơn đã lưu tại: {filename}")
    
    def view_invoices(self):
        print("\n" + "="*70)
        print("              📜 DANH SÁCH HÓA ĐƠN")
        print("="*70)
        
        if not self.dm.invoices:
            print("  📭 Chưa có hóa đơn nào!")
        else:
            print(f"{'Mã HD':<8} {'Ngày':<20} {'Khách hàng':<20} {'Tổng tiền':<15}")
            print("-"*70)
            for inv in self.dm.invoices:
                customer = None
                for c in self.dm.customers:
                    if c['id'] == inv['customer_id']:
                        customer = c
                        break
                customer_name = customer['name'] if customer else "N/A"
                print(f"{inv['id']:<8} {inv['date']:<20} {customer_name:<20} {inv['total']:>12,.0f}đ")
        print("="*70)

# ==================== CHƯƠNG TRÌNH CHÍNH ====================
class MainApp:
    def __init__(self):
        self.dm = DataManager()
        self.login_sys = LoginSystem(self.dm)
        self.current_user = None
    
    def run(self):
        # Đăng nhập
        while self.current_user is None:
            self.current_user = self.login_sys.login()
            if self.current_user is None:
                retry = input("Thử lại? (y/n): ").lower()
                if retry != 'y':
                    print("👋 Tạm biệt!")
                    return
        
        # Khởi tạo các manager
        self.car_manager = CarManager(self.dm)
        self.customer_manager = CustomerManager(self.dm)
        self.invoice_manager = InvoiceManager(self.dm, self.car_manager, self.customer_manager)
        
        # Menu chính
        while True:
            self.show_menu()
            choice = input("  ▶️ Chọn chức năng: ")
            
            if choice == '0':
                print("\n👋 Cảm ơn bạn đã sử dụng phần mềm!")
                break
            elif choice == '1':
                self.car_menu()
            elif choice == '2':
                self.customer_menu()
            elif choice == '3':
                self.invoice_manager.create_invoice()
            elif choice == '4':
                self.car_manager.view_cars()
                input("\nNhấn Enter để tiếp tục...")
            elif choice == '5':
                self.invoice_manager.view_invoices()
                input("\nNhấn Enter để tiếp tục...")
            elif choice == '6':
                self.car_manager.search_car()
            else:
                print("\n❌ Chức năng không hợp lệ!")
    
    def show_menu(self):
        print("\n" + "="*50)
        print(f"  🏢 QUẢN LÝ ĐẠI LÝ XE HƠI")
        print(f"  👤 Nhân viên: {self.current_user['name']}")
        print("="*50)
        print("  1. 🚗 Quản lý xe")
        print("  2. 👥 Quản lý khách hàng")
        print("  3. 🧾 Bán hàng (tạo hóa đơn)")
        print("  4. 📋 Xem danh sách xe")
        print("  5. 📜 Xem danh sách hóa đơn")
        print("  6. 🔍 Tìm kiếm xe")
        print("  0. 🚪 Thoát")
        print("-"*50)
    
    def car_menu(self):
        while True:
            print("\n--- 🚗 QUẢN LÝ XE ---")
            print("1. Thêm xe mới")
            print("2. Xóa xe")
            print("3. Xem danh sách xe")
            print("0. Quay lại")
            
            choice = input("Chọn: ")
            if choice == '1':
                self.car_manager.add_car()
            elif choice == '2':
                self.car_manager.delete_car()
            elif choice == '3':
                self.car_manager.view_cars()
            elif choice == '0':
                break
            input("\nNhấn Enter để tiếp tục...")
    
    def customer_menu(self):
        while True:
            print("\n--- 👥 QUẢN LÝ KHÁCH HÀNG ---")
            print("1. Thêm khách hàng mới")
            print("2. Xem danh sách khách hàng")
            print("0. Quay lại")
            
            choice = input("Chọn: ")
            if choice == '1':
                self.customer_manager.add_customer()
            elif choice == '2':
                self.customer_manager.view_customers()
            elif choice == '0':
                break
            input("\nNhấn Enter để tiếp tục...")

# ==================== CHẠY CHƯƠNG TRÌNH ====================
if __name__ == "__main__":
    app = MainApp()
    app.run()