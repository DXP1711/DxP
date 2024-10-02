from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Product
from config import Config
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import User


app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

# Route trang chủ
@app.route('/')
def index():
    products = Product.query.all()
    return render_template('index.html', products=products)

# Route chi tiết sản phẩm
@app.route('/product/<int:id>')
def product(id):
    product = Product.query.get(id)
    return render_template('product.html', product=product)

# Route thêm sản phẩm vào giỏ hàng
@app.route('/add_to_cart/<int:id>')
def add_to_cart(id):
    product = Product.query.get(id)
    if 'cart' not in session:
        session['cart'] = []
    session['cart'].append(product.id)
    return redirect(url_for('cart'))

# Route giỏ hàng
@app.route('/cart')
def cart():
    cart_items = Product.query.filter(Product.id.in_(session.get('cart', []))).all()
    return render_template('cart.html', cart_items=cart_items)

if __name__ == '__main__':
    app.run(debug=True)

# Cấu hình Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route đăng ký
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

# Route đăng nhập
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

# Route đăng xuất
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        # Lưu thông tin đơn hàng
        order_items = session.get('cart', [])
        new_order = Order(user_id=current_user.id, items=str(order_items))
        db.session.add(new_order)
        db.session.commit()
        session['cart'] = []  # Xóa giỏ hàng sau khi thanh toán
        return redirect(url_for('order_complete'))
    return render_template('checkout.html')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    items = db.Column(db.String, nullable=False)
