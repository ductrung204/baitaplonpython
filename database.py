import mysql.connector
from datetime import datetime
import hashlib
import time

class Database:
    def __init__(self):
        self.connect()
    
    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="car_dealership",
                connect_timeout=10,
                autocommit=False
            )
            self.cursor = self.conn.cursor(dictionary=True)
            print("✅ Đã kết nối MySQL thành công!")
        except mysql.connector.Error as e:
            print(f"❌ Lỗi kết nối MySQL: {e}")
            print("👉 Hãy kiểm tra XAMPP đã Start MySQL chưa!")
            raise e
    
    def reconnect(self):
        try:
            self.conn.ping(reconnect=True, attempts=3, delay=1)
        except:
            self.connect()
    
    def close(self):
        try:
            self.cursor.close()
            self.conn.close()
        except:
            pass
    
    def execute_query(self, query, params=None):
        try:
            self.reconnect()
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor
        except mysql.connector.Error as e:
            print(f"Lỗi query: {e}")
            raise e
    
    # ========== ĐĂNG NHẬP ==========
    def login(self, username, password):
        hashed = hashlib.md5(password.encode()).hexdigest()
        self.execute_query(
            "SELECT * FROM employees WHERE username = %s AND password = %s",
            (username, hashed)
        )
        return self.cursor.fetchone()
    
    # ========== QUẢN LÝ XE ==========
    def get_all_cars(self):
        self.execute_query("SELECT * FROM cars ORDER BY id")
        return self.cursor.fetchall()
    
    def get_car_by_id(self, car_id):
        self.execute_query("SELECT * FROM cars WHERE id = %s", (car_id,))
        return self.cursor.fetchone()
    
    def add_car(self, car_data):
        try:
            self.reconnect()
            self.cursor.execute(
                """INSERT INTO cars (id, name, brand, year, import_price, sell_price, quantity)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (car_data['id'], car_data['name'], car_data['brand'],
                 car_data['year'], car_data['import_price'],
                 car_data['sell_price'], car_data['quantity'])
            )
            self.conn.commit()
            return True, "Thêm xe thành công!"
        except mysql.connector.IntegrityError:
            return False, "Mã xe đã tồn tại!"
        except Exception as e:
            return False, f"Lỗi: {e}"
    
    def delete_car(self, car_id):
        try:
            self.reconnect()
            self.cursor.execute("DELETE FROM cars WHERE id = %s", (car_id,))
            self.conn.commit()
            return True, "Xóa xe thành công!"
        except Exception as e:
            return False, f"Lỗi: {e}"
    
    def search_cars(self, keyword):
        keyword = f"%{keyword}%"
        self.execute_query(
            "SELECT * FROM cars WHERE name LIKE %s OR brand LIKE %s OR id LIKE %s",
            (keyword, keyword, keyword)
        )
        return self.cursor.fetchall()
    
    # ========== QUẢN LÝ KHÁCH HÀNG ==========
    def get_all_customers(self):
        self.execute_query("SELECT * FROM customers ORDER BY id")
        return self.cursor.fetchall()
    
    def get_customer_by_id(self, cus_id):
        self.execute_query("SELECT * FROM customers WHERE id = %s", (cus_id,))
        return self.cursor.fetchone()
    
    def add_customer(self, customer_data):
        try:
            self.reconnect()
            self.cursor.execute(
                """INSERT INTO customers (id, name, phone, address, email, total_spent)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (customer_data['id'], customer_data['name'], customer_data['phone'],
                 customer_data['address'], customer_data['email'], 0)
            )
            self.conn.commit()
            return True, "Thêm khách hàng thành công!"
        except mysql.connector.IntegrityError:
            return False, "Mã khách hàng đã tồn tại!"
        except Exception as e:
            return False, f"Lỗi: {e}"
    
    def delete_customer(self, cus_id):
        try:
            self.reconnect()
            self.cursor.execute("DELETE FROM customers WHERE id = %s", (cus_id,))
            self.conn.commit()
            return True, "Xóa khách hàng thành công!"
        except Exception as e:
            return False, f"Lỗi: {e}"
    
    # ========== QUẢN LÝ HÓA ĐƠN ==========
    def get_all_invoices(self):
        self.execute_query("SELECT * FROM invoices ORDER BY datetime DESC")
        return self.cursor.fetchall()
    
    def create_invoice(self, customer_id, employee_id, items):
        try:
            self.reconnect()
            self.execute_query("SELECT COUNT(*) as count FROM invoices")
            count = self.cursor.fetchone()['count']
            invoice_id = f"HD{count+1:04d}"
            
            total = sum(item['quantity'] * item['price'] for item in items)
            
            self.cursor.execute(
                """INSERT INTO invoices (id, customer_id, employee_id, datetime, total)
                   VALUES (%s, %s, %s, NOW(), %s)""",
                (invoice_id, customer_id, employee_id, total)
            )
            
            for item in items:
                self.cursor.execute(
                    """INSERT INTO invoice_details (invoice_id, car_id, quantity, price)
                       VALUES (%s, %s, %s, %s)""",
                    (invoice_id, item['car_id'], item['quantity'], item['price'])
                )
                self.cursor.execute(
                    "UPDATE cars SET quantity = quantity - %s WHERE id = %s",
                    (item['quantity'], item['car_id'])
                )
            
            self.cursor.execute(
                "UPDATE customers SET total_spent = total_spent + %s WHERE id = %s",
                (total, customer_id)
            )
            
            self.conn.commit()
            return True, {"id": invoice_id, "total": total}
        except Exception as e:
            self.conn.rollback()
            return False, f"Lỗi: {e}"
    
    # ========== QUẢN LÝ ĐẶT CỌC ==========
    def get_all_deposits(self):
        self.execute_query("""
            SELECT d.*, c.name as customer_name, c.phone as customer_phone,
                   car.name as car_name, car.sell_price as car_price
            FROM deposits d
            JOIN customers c ON d.customer_id = c.id
            JOIN cars car ON d.car_id = car.id
            ORDER BY d.deposit_date DESC
        """)
        return self.cursor.fetchall()
    
    def get_deposit_by_id(self, deposit_id):
        self.execute_query("SELECT * FROM deposits WHERE id = %s", (deposit_id,))
        return self.cursor.fetchone()
    
    def create_deposit(self, customer_id, car_id, deposit_amount, note=""):
        try:
            self.reconnect()
            
            car = self.get_car_by_id(car_id)
            if not car:
                return False, "Không tìm thấy xe!"
            
            remaining_amount = car['sell_price'] - deposit_amount
            
            if deposit_amount <= 0:
                return False, "Số tiền cọc phải lớn hơn 0!"
            
            if deposit_amount > car['sell_price']:
                return False, "Số tiền cọc không được lớn hơn giá xe!"
            
            self.execute_query("SELECT COUNT(*) as count FROM deposits")
            count = self.cursor.fetchone()['count']
            deposit_id = f"DC{count+1:04d}"
            
            self.cursor.execute("""
                INSERT INTO deposits (id, customer_id, car_id, deposit_amount, 
                                      remaining_amount, status, deposit_date, note)
                VALUES (%s, %s, %s, %s, %s, 'pending', NOW(), %s)
            """, (deposit_id, customer_id, car_id, deposit_amount, remaining_amount, note))
            
            self.cursor.execute(
                "UPDATE cars SET quantity = quantity - 1 WHERE id = %s AND quantity > 0",
                (car_id,)
            )
            
            self.conn.commit()
            return True, deposit_id
            
        except Exception as e:
            self.conn.rollback()
            return False, f"Lỗi: {e}"
    
    def complete_deposit(self, deposit_id, employee_id):
        try:
            self.reconnect()
            
            self.execute_query("SELECT * FROM deposits WHERE id = %s", (deposit_id,))
            deposit = self.cursor.fetchone()
            
            if not deposit:
                return False, "Không tìm thấy đơn đặt cọc!"
            
            if deposit['status'] != 'pending':
                return False, "Đơn đặt cọc đã được xử lý!"
            
            items = [{
                'car_id': deposit['car_id'],
                'quantity': 1,
                'price': deposit['deposit_amount'] + deposit['remaining_amount']
            }]
            
            success, result = self.create_invoice(deposit['customer_id'], employee_id, items)
            
            if success:
                self.cursor.execute("""
                    UPDATE deposits SET status = 'completed', expected_delivery_date = CURDATE()
                    WHERE id = %s
                """, (deposit_id,))
                self.conn.commit()
                return True, f"Đã tạo hóa đơn {result['id']} thành công!"
            
            return False, "Lỗi khi tạo hóa đơn!"
            
        except Exception as e:
            self.conn.rollback()
            return False, f"Lỗi: {e}"
    
    def cancel_deposit(self, deposit_id):
        try:
            self.reconnect()
            
            self.execute_query("SELECT * FROM deposits WHERE id = %s", (deposit_id,))
            deposit = self.cursor.fetchone()
            
            if not deposit:
                return False, "Không tìm thấy đơn đặt cọc!"
            
            if deposit['status'] != 'pending':
                return False, "Đơn đặt cọc đã được xử lý, không thể hủy!"
            
            self.cursor.execute(
                "UPDATE cars SET quantity = quantity + 1 WHERE id = %s",
                (deposit['car_id'],)
            )
            
            self.cursor.execute("""
                UPDATE deposits SET status = 'cancelled' WHERE id = %s
            """, (deposit_id,))
            
            self.conn.commit()
            return True, "Đã hủy đơn đặt cọc và hoàn lại xe vào kho!"
            
        except Exception as e:
            self.conn.rollback()
            return False, f"Lỗi: {e}"
    
    # ========== THỐNG KÊ ==========
    def get_statistics(self):
        self.execute_query("SELECT COALESCE(SUM(total), 0) as total FROM invoices")
        total_revenue = self.cursor.fetchone()['total']
        
        self.execute_query("SELECT COALESCE(SUM(quantity), 0) as total FROM invoice_details")
        total_cars_sold = self.cursor.fetchone()['total']
        
        self.execute_query("SELECT COUNT(*) as count FROM invoices")
        total_invoices = self.cursor.fetchone()['count']
        
        self.execute_query("SELECT COUNT(*) as count FROM customers")
        total_customers = self.cursor.fetchone()['count']
        
        self.execute_query("""
            SELECT car_id, SUM(quantity) as total_sold
            FROM invoice_details
            GROUP BY car_id
            ORDER BY total_sold DESC
            LIMIT 5
        """)
        top_cars = [(row['car_id'], row['total_sold']) for row in self.cursor.fetchall()]
        
        self.execute_query("""
            SELECT id, name, total_spent
            FROM customers
            ORDER BY total_spent DESC
            LIMIT 5
        """)
        top_customers = self.cursor.fetchall()
        
        self.execute_query("SELECT * FROM cars WHERE quantity < 5")
        low_stock = self.cursor.fetchall()
        
        all_cars = self.get_all_cars()
        
        return {
            'total_revenue': total_revenue,
            'total_cars_sold': total_cars_sold,
            'total_invoices': total_invoices,
            'total_customers': total_customers,
            'top_cars': top_cars,
            'top_customers': top_customers,
            'low_stock': low_stock,
            'all_cars': all_cars
        }