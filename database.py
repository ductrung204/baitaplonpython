import json
import os
from datetime import datetime
import hashlib

class Database:
    def __init__(self):
        self.data_dir = "data"
        self.create_folders()
        self.load_all_data()
    
    def create_folders(self):
        folders = ['data', 'backups', 'invoices']
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
    
    def load_all_data(self):
        self.cars = self.load_file("cars.json")
        self.customers = self.load_file("customers.json")
        self.employees = self.load_file("employees.json")
        self.invoices = self.load_file("invoices.json")
        
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
        filepath = os.path.join(self.data_dir, filename)
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_file(self, filename, data):
        filepath = os.path.join(self.data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    
    def save_all(self):
        self.save_file("cars.json", self.cars)
        self.save_file("customers.json", self.customers)
        self.save_file("employees.json", self.employees)
        self.save_file("invoices.json", self.invoices)
    
    def login(self, username, password):
        hashed = hashlib.md5(password.encode()).hexdigest()
        for emp in self.employees:
            if emp['username'] == username and emp['password'] == hashed:
                return emp
        return None
    
    # ========== QUẢN LÝ XE ==========
    def get_all_cars(self):
        return self.cars
    
    def get_car_by_id(self, car_id):
        for car in self.cars:
            if car['id'] == car_id:
                return car
        return None
    
    def add_car(self, car_data):
        for car in self.cars:
            if car['id'] == car_data['id']:
                return False, "Mã xe đã tồn tại!"
        self.cars.append(car_data)
        self.save_all()
        return True, "Thêm xe thành công!"
    
    def update_car(self, car_id, new_data):
        for i, car in enumerate(self.cars):
            if car['id'] == car_id:
                self.cars[i].update(new_data)
                self.save_all()
                return True, "Cập nhật thành công!"
        return False, "Không tìm thấy xe!"
    
    def delete_car(self, car_id):
        for i, car in enumerate(self.cars):
            if car['id'] == car_id:
                for inv in self.invoices:
                    for item in inv['items']:
                        if item['car_id'] == car_id:
                            return False, "Xe đã được bán, không thể xóa!"
                self.cars.pop(i)
                self.save_all()
                return True, "Xóa xe thành công!"
        return False, "Không tìm thấy xe!"
    
    def search_cars(self, keyword):
        keyword = keyword.lower()
        return [car for car in self.cars 
                if keyword in car['name'].lower() 
                or keyword in car['brand'].lower() 
                or keyword in car['id'].lower()]
    
    # ========== QUẢN LÝ KHÁCH HÀNG ==========
    def get_all_customers(self):
        return self.customers
    
    def get_customer_by_id(self, cus_id):
        for cus in self.customers:
            if cus['id'] == cus_id:
                return cus
        return None
    
    def add_customer(self, customer_data):
        for cus in self.customers:
            if cus['id'] == customer_data['id']:
                return False, "Mã khách hàng đã tồn tại!"
        self.customers.append(customer_data)
        self.save_all()
        return True, "Thêm khách hàng thành công!"
    
    def update_customer(self, cus_id, new_data):
        for i, cus in enumerate(self.customers):
            if cus['id'] == cus_id:
                self.customers[i].update(new_data)
                self.save_all()
                return True, "Cập nhật thành công!"
        return False, "Không tìm thấy khách hàng!"
    
    def delete_customer(self, cus_id):
        for i, cus in enumerate(self.customers):
            if cus['id'] == cus_id:
                for inv in self.invoices:
                    if inv['customer_id'] == cus_id:
                        return False, "Khách hàng đã mua hàng, không thể xóa!"
                self.customers.pop(i)
                self.save_all()
                return True, "Xóa khách hàng thành công!"
        return False, "Không tìm thấy khách hàng!"
    
    # ========== QUẢN LÝ HÓA ĐƠN ==========
    def get_all_invoices(self):
        return self.invoices
    
    def get_invoice_by_id(self, inv_id):
        for inv in self.invoices:
            if inv['id'] == inv_id:
                return inv
        return None
    
    def create_invoice(self, customer_id, employee_id, items):
        total = sum(item['quantity'] * item['price'] for item in items)
        invoice_id = f"HD{len(self.invoices)+1:04d}"
        
        invoice = {
            "id": invoice_id,
            "customer_id": customer_id,
            "employee_id": employee_id,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "items": items,
            "total": total
        }
        
        self.invoices.append(invoice)
        
        for item in items:
            for car in self.cars:
                if car['id'] == item['car_id']:
                    car['quantity'] -= item['quantity']
        
        for cus in self.customers:
            if cus['id'] == customer_id:
                cus['total_spent'] = cus.get('total_spent', 0) + total
        
        self.save_all()
        self.save_invoice_to_file(invoice)
        return True, invoice
    
    def save_invoice_to_file(self, invoice):
        filename = f"invoices/{invoice['id']}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*50 + "\n")
            f.write("         HÓA ĐƠN BÁN XE\n")
            f.write("="*50 + "\n")
            f.write(f"Số HD: {invoice['id']}\n")
            f.write(f"Ngày: {invoice['date']}\n")
            f.write("-"*50 + "\n")
            for item in invoice['items']:
                car = self.get_car_by_id(item['car_id'])
                car_name = car['name'] if car else item['car_id']
                f.write(f"Xe: {car_name} - SL: {item['quantity']} - ĐG: {item['price']:,.0f}đ\n")
            f.write("-"*50 + "\n")
            f.write(f"TỔNG TIỀN: {invoice['total']:,.0f}đ\n")
            f.write("="*50 + "\n")
    
    # ========== THỐNG KÊ ==========
    def get_statistics(self):
        total_revenue = sum(inv['total'] for inv in self.invoices)
        total_cars_sold = sum(item['quantity'] for inv in self.invoices for item in inv['items'])
        
        car_sales = {}
        for inv in self.invoices:
            for item in inv['items']:
                car_sales[item['car_id']] = car_sales.get(item['car_id'], 0) + item['quantity']
        
        top_cars = sorted(car_sales.items(), key=lambda x: x[1], reverse=True)[:5]
        top_customers = sorted(self.customers, key=lambda x: x.get('total_spent', 0), reverse=True)[:5]
        low_stock = [car for car in self.cars if car['quantity'] < 5]
        
        return {
            'total_revenue': total_revenue,
            'total_cars_sold': total_cars_sold,
            'total_invoices': len(self.invoices),
            'total_customers': len(self.customers),
            'top_cars': top_cars,
            'top_customers': top_customers,
            'low_stock': low_stock
        }