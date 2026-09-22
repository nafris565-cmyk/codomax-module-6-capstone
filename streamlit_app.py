
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os

DB = "capstone.db"

def get_conn():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.execute("""CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        amount REAL NOT NULL,
        category TEXT NOT NULL,
        date TEXT NOT NULL,
        notes TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        stock INTEGER DEFAULT 0,
        category TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        quantity INTEGER,
        total REAL,
        customer TEXT,
        created_at TEXT
    )""")
    cur = conn.execute("SELECT COUNT(*) as c FROM products").fetchone()
    if cur['c'] == 0:
        conn.executemany("INSERT INTO products (name,price,stock,category) VALUES (?,?,?,?)", [
            ('Laptop Pro', 85000, 10, 'Electronics'),
            ('Wireless Mouse', 1200, 100, 'Electronics'),
            ('Office Chair', 15000, 20, 'Furniture'),
            ('Python Book', 850, 50, 'Books')
        ])
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="Codomax Capstone - Nafri", page_icon="💼", layout="wide")
st.title("💼 Codomax Module 6 - Python Capstone Project")
st.caption("Student: Nafri | ID: CDS_INT_202693138 | Expense Tracker + Mini E-Commerce | Live Deployment")

tab1, tab2, tab3 = st.tabs(["💰 Expenses", "🛒 Products", "📦 Orders"])

with tab1:
    col1, col2 = st.columns([1,2])
    with col1:
        st.subheader("Add Expense")
        with st.form("exp_form"):
            title = st.text_input("Title")
            amount = st.number_input("Amount (₹)", min_value=1.0)
            category = st.selectbox("Category", ["Food","Travel","Shopping","Office","Other"])
            notes = st.text_area("Notes")
            submitted = st.form_submit_button("Add Expense")
            if submitted:
                conn = get_conn()
                conn.execute("INSERT INTO expenses (title,amount,category,date,notes) VALUES (?,?,?,?,?)",
                    (title, amount, category, datetime.now().strftime("%Y-%m-%d"), notes))
                conn.commit()
                conn.close()
                st.success("Added!")
                st.rerun()
    with col2:
        conn = get_conn()
        df = pd.read_sql_query("SELECT * FROM expenses ORDER BY id DESC", conn)
        conn.close()
        if not df.empty:
            st.metric("Total Spent", f"₹{df['amount'].sum():,.0f}")
            st.metric("Transactions", len(df))
            st.dataframe(df, use_container_width=True)
            summary = df.groupby("category")["amount"].sum()
            st.bar_chart(summary)
        else:
            st.info("No expenses yet - Add one!")

with tab2:
    conn = get_conn()
    pdf = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    st.dataframe(pdf, use_container_width=True)
    st.subheader("Add Product")
    with st.form("prod_form"):
        pname = st.text_input("Product Name")
        pprice = st.number_input("Price", min_value=1.0)
        pstock = st.number_input("Stock", min_value=1)
        pcat = st.text_input("Category", "General")
        psub = st.form_submit_button("Add Product")
        if psub:
            conn = get_conn()
            conn.execute("INSERT INTO products (name,price,stock,category) VALUES (?,?,?,?)",(pname,pprice,pstock,pcat))
            conn.commit()
            conn.close()
            st.success("Product Added!")
            st.rerun()

with tab3:
    conn = get_conn()
    odf = pd.read_sql_query("SELECT o.*, p.name as product_name FROM orders o JOIN products p ON o.product_id=p.id ORDER BY o.id DESC", conn)
    prods = pd.read_sql_query("SELECT id, name, stock, price FROM products", conn)
    conn.close()
    
    st.subheader("Place Order")
    with st.form("order_form"):
        pid = st.selectbox("Product", prods["id"].tolist(), format_func=lambda x: f"#{x} - {prods[prods['id']==x]['name'].values[0]} (Stock:{prods[prods['id']==x]['stock'].values[0]})")
        qty = st.number_input("Quantity", min_value=1, value=1)
        cust = st.text_input("Customer Name", "Guest")
        osub = st.form_submit_button("Place Order")
        if osub:
            conn = get_conn()
            prod = conn.execute("SELECT * FROM products WHERE id=?",(pid,)).fetchone()
            if prod["stock"] < qty:
                st.error("Insufficient stock!")
            else:
                total = prod["price"] * qty
                conn.execute("INSERT INTO orders (product_id,quantity,total,customer,created_at) VALUES (?,?,?,?,?)",(pid,qty,total,cust,datetime.now().isoformat()))
                conn.execute("UPDATE products SET stock=stock-? WHERE id=?",(qty,pid))
                conn.commit()
                st.success(f"Order Placed! Total: ₹{total}")
            conn.close()
            st.rerun()
    
    if not odf.empty:
        st.dataframe(odf, use_container_width=True)
    else:
        st.info("No orders yet")

st.divider()
st.markdown("**Tech Stack:** Python | Streamlit | SQLite | Pandas | Deployment: Streamlit Cloud (Free) | GitHub: github.com/nafris565-cmyk/codomax-module-6-capstone | **Live Demo Ready for Codomax**")
