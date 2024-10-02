from flask import Flask, render_template, request, redirect, url_for, session
from phuoc.models import db, Product
from config import Config





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
