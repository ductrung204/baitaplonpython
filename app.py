from flask import Flask, render_template, request, redirect, url_for, session, flash
from database import Database

app = Flask(__name__)
app.secret_key = "quanlyxehoi_secret_key_2025"
db = Database()

# ==================== TRANG ĐĂNG NHẬP ====================
@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    user = db.login(username, password)
    if user:
        session['user'] = user
        flash(f'Chào mừng {user["name"]}!', 'success')
        return redirect(url_for('index'))
    
    flash('Sai tên đăng nhập hoặc mật khẩu!', 'error')
    return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Đã đăng xuất!', 'info')
    return redirect(url_for('login_page'))

# ==================== TRANG CHỦ ====================
@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    stats = db.get_statistics()
    all_cars = db.get_all_cars()
    return render_template('index.html', user=session['user'], stats=stats, all_cars=all_cars)

# ==================== QUẢN LÝ XE ====================
@app.route('/cars')
def cars():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    search = request.args.get('search', '')
    if search:
        cars_list = db.search_cars(search)
    else:
        cars_list = db.get_all_cars()
    
    return render_template('cars.html', cars=cars_list, user=session['user'], search=search)

@app.route('/add_car', methods=['POST'])
def add_car():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    try:
        car_data = {
            'id': request.form['id'].strip().upper(),
            'name': request.form['name'].strip(),
            'brand': request.form['brand'].strip(),
            'year': int(request.form['year']),
            'import_price': float(request.form['import_price']),
            'sell_price': float(request.form['sell_price']),
            'quantity': int(request.form['quantity'])
        }
        success, msg = db.add_car(car_data)
        flash(msg, 'success' if success else 'error')
    except ValueError:
        flash('Vui lòng nhập đúng định dạng số!', 'error')
    
    return redirect(url_for('cars'))

@app.route('/delete_car/<car_id>')
def delete_car(car_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    success, msg = db.delete_car(car_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('cars'))

# ==================== QUẢN LÝ KHÁCH HÀNG ====================
@app.route('/customers')
def customers():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    customers_list = db.get_all_customers()
    return render_template('customers.html', customers=customers_list, user=session['user'])

@app.route('/add_customer', methods=['POST'])
def add_customer():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    customer_data = {
        'id': request.form['id'].strip().upper(),
        'name': request.form['name'].strip(),
        'phone': request.form['phone'].strip(),
        'address': request.form['address'].strip(),
        'email': request.form.get('email', '').strip(),
        'total_spent': 0
    }
    
    success, msg = db.add_customer(customer_data)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('customers'))

@app.route('/delete_customer/<cus_id>')
def delete_customer(cus_id):
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    success, msg = db.delete_customer(cus_id)
    flash(msg, 'success' if success else 'error')
    return redirect(url_for('customers'))

# ==================== BÁN HÀNG ====================
@app.route('/sell')
def sell():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    cars_list = db.get_all_cars()
    customers_list = db.get_all_customers()
    return render_template('sell.html', cars=cars_list, customers=customers_list, user=session['user'])

@app.route('/create_invoice', methods=['POST'])
def create_invoice():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    customer_id = request.form['customer_id']
    car_id = request.form['car_id']
    quantity = int(request.form['quantity'])
    
    car = db.get_car_by_id(car_id)
    if not car:
        flash('Không tìm thấy xe!', 'error')
        return redirect(url_for('sell'))
    
    if quantity > car['quantity']:
        flash(f'Không đủ số lượng! Xe {car["name"]} chỉ còn {car["quantity"]} chiếc.', 'error')
        return redirect(url_for('sell'))
    
    items = [{'car_id': car_id, 'quantity': quantity, 'price': car['sell_price']}]
    success, result = db.create_invoice(customer_id, session['user']['id'], items)
    
    if success:
        flash(f'✅ Tạo hóa đơn thành công! Mã HD: {result["id"]} - Tổng tiền: {result["total"]:,.0f}đ', 'success')
    else:
        flash('❌ Tạo hóa đơn thất bại!', 'error')
    
    return redirect(url_for('sell'))

# ==================== HÓA ĐƠN ====================
@app.route('/invoices')
def invoices():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    invoices_list = db.get_all_invoices()
    return render_template('invoices.html', invoices=invoices_list, user=session['user'])

# ==================== THỐNG KÊ ====================
@app.route('/statistics')
def statistics():
    if 'user' not in session:
        return redirect(url_for('login_page'))
    
    stats = db.get_statistics()
    return render_template('statistics.html', stats=stats, user=session['user'])

if __name__ == '__main__':
    app.run(debug=True)