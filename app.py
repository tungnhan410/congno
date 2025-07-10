
from flask import Flask, render_template, request, redirect, session
import json, os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/images'
app.secret_key = 'secret'

PRODUCTS_FILE = 'data/products.json'
USERS_FILE = 'data/users.json'

def load_data(file, default):
    return json.load(open(file, 'r', encoding='utf-8')) if os.path.exists(file) else default
def save_data(file, data): json.dump(data, open(file, 'w'), indent=2)

products = load_data(PRODUCTS_FILE, [])
users = load_data(USERS_FILE, [])

@app.route('/')
def index():
    query = request.args.get('q', '').lower()
    category = request.args.get('cat', '')
    filtered = [p for p in products if (query in p['name'].lower() and (not category or p['category'] == category))]
    cats = list(set(p['category'] for p in products))
    return render_template('index.html', products=products, filtered=filtered, cats=cats)

@app.route('/add_product', methods=['POST'])
def add_product():
    if session.get('user') != 'admin': return redirect('/')
    file = request.files.get('image')
    filename = secure_filename(file.filename) if file else ''
    if file: file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    p = {
        'name': request.form['name'],
        'image': filename,
        'price': int(request.form['price']),
        'category': request.form['category']
    }
    products.append(p)
    save_data(PRODUCTS_FILE, products)
    return redirect('/')

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    idx = int(request.form['id'])
    session.setdefault('cart', []).append(products[idx])
    session.modified = True
    return redirect('/')

@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total = sum(p['price'] for p in cart)
    return render_template('cart.html', cart=cart, total=total)

@app.route('/checkout')
def checkout():
    session['cart'] = []
    return render_template('checkout.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form['user'], request.form['pass']
        for user in users:
            if user['user'] == u and user['pass'] == p:
                session['user'] = u
                return redirect('/')
        return 'Sai tài khoản'
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u, p = request.form['user'], request.form['pass']
        users.append({'user': u, 'pass': p})
        save_data(USERS_FILE, users)
        return redirect('/login')
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
