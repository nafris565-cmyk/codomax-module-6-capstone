
import os, sqlite3, logging, json
from datetime import datetime
from flask import Flask, jsonify, request, render_template, g
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATABASE = 'capstone.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with app.app_context():
        db = get_db()
        # Expenses
        db.execute('''CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            notes TEXT
        )''')
        # Products for E-commerce part
        db.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            stock INTEGER DEFAULT 0,
            category TEXT
        )''')
        # Orders
        db.execute('''CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            quantity INTEGER,
            total REAL,
            customer TEXT,
            created_at TEXT
        )''')
        db.commit()
        # Seed data if empty
        cur = db.execute('SELECT COUNT(*) as c FROM products')
        if cur.fetchone()['c'] == 0:
            db.executemany('INSERT INTO products (name,price,stock,category) VALUES (?,?,?,?)', [
                ('Laptop Pro', 85000, 10, 'Electronics'),
                ('Wireless Mouse', 1200, 100, 'Electronics'),
                ('Office Chair', 15000, 20, 'Furniture'),
                ('Python Book', 850, 50, 'Books')
            ])
            db.commit()
            logger.info("Seed data inserted")
        logger.info("DB initialized")

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# ---------- Frontend ----------
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/docs')
def api_docs():
    return jsonify({
        "project": "Codomax Module 6 - Python Capstone",
        "student": "Nafri - CDS_INT_202693138",
        "endpoints": {
            "expenses": "/api/expenses [GET,POST], /api/expenses/<id> [PUT,DELETE], /api/expenses/summary",
            "products": "/api/products [GET,POST], /api/products/<id>",
            "orders": "/api/orders [GET,POST]",
            "health": "/api/health"
        },
        "live_demo": "Deployed on Render"
    })

# ---------- Health ----------
@app.route('/api/health')
def health():
    return jsonify({"status":"ok","timestamp":datetime.utcnow().isoformat(),"project":"Capstone"})

# ---------- Expenses API ----------
@app.route('/api/expenses', methods=['GET','POST'])
def expenses():
    db = get_db()
    if request.method == 'POST':
        data = request.get_json()
        if not data or not all(k in data for k in ('title','amount','category')):
            return jsonify({"error":"title, amount, category required"}), 400
        try:
            db.execute('INSERT INTO expenses (title,amount,category,date,notes) VALUES (?,?,?,?,?)',
                (data['title'], float(data['amount']), data['category'], data.get('date', datetime.now().strftime('%Y-%m-%d')), data.get('notes','')))
            db.commit()
            logger.info(f"Expense added: {data['title']}")
            return jsonify({"message":"Expense added"}), 201
        except Exception as e:
            logger.error(f"Error adding expense: {e}")
            return jsonify({"error":str(e)}), 500
    # GET with filters
    category = request.args.get('category')
    query = 'SELECT * FROM expenses'
    params = []
    if category:
        query += ' WHERE category=?'
        params.append(category)
    query += ' ORDER BY id DESC'
    rows = db.execute(query, params).fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/expenses/<int:exp_id>', methods=['PUT','DELETE'])
def expense_detail(exp_id):
    db = get_db()
    if request.method == 'DELETE':
        db.execute('DELETE FROM expenses WHERE id=?',(exp_id,))
        db.commit()
        return jsonify({"message":"Deleted"})
    data = request.get_json()
    db.execute('UPDATE expenses SET title=?, amount=?, category=?, notes=? WHERE id=?',
        (data.get('title'), data.get('amount'), data.get('category'), data.get('notes',''), exp_id))
    db.commit()
    return jsonify({"message":"Updated"})

@app.route('/api/expenses/summary')
def expense_summary():
    db = get_db()
    rows = db.execute('SELECT category, SUM(amount) as total, COUNT(*) as count FROM expenses GROUP BY category').fetchall()
    total = db.execute('SELECT SUM(amount) as total FROM expenses').fetchone()['total'] or 0
    return jsonify({"by_category":[dict(r) for r in rows], "grand_total": total})

# ---------- Products API ----------
@app.route('/api/products', methods=['GET','POST'])
def products():
    db = get_db()
    if request.method == 'POST':
        data = request.get_json()
        db.execute('INSERT INTO products (name,price,stock,category) VALUES (?,?,?,?)',
            (data['name'], data['price'], data['stock'], data.get('category','General')))
        db.commit()
        return jsonify({"message":"Product added"}), 201
    rows = db.execute('SELECT * FROM products').fetchall()
    return jsonify([dict(r) for r in rows])

@app.route('/api/products/<int:pid>')
def product_one(pid):
    db = get_db()
    row = db.execute('SELECT * FROM products WHERE id=?',(pid,)).fetchone()
    if not row: return jsonify({"error":"Not found"}), 404
    return jsonify(dict(row))

# ---------- Orders API ----------
@app.route('/api/orders', methods=['GET','POST'])
def orders():
    db = get_db()
    if request.method == 'POST':
        data = request.get_json()
        prod = db.execute('SELECT * FROM products WHERE id=?',(data['product_id'],)).fetchone()
        if not prod: return jsonify({"error":"Product not found"}), 404
        if prod['stock'] < int(data['quantity']):
            return jsonify({"error":"Insufficient stock"}), 400
        total = prod['price'] * int(data['quantity'])
        db.execute('INSERT INTO orders (product_id,quantity,total,customer,created_at) VALUES (?,?,?,?,?)',
            (data['product_id'], data['quantity'], total, data.get('customer','Guest'), datetime.now().isoformat()))
        db.execute('UPDATE products SET stock=stock-? WHERE id=?',(data['quantity'], data['product_id']))
        db.commit()
        return jsonify({"message":"Order placed","total":total}), 201
    rows = db.execute('SELECT o.*, p.name as product_name FROM orders o JOIN products p ON o.product_id=p.id ORDER BY o.id DESC').fetchall()
    return jsonify([dict(r) for r in rows])

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
