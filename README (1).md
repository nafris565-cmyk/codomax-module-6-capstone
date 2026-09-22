
# Codomax Module 6 - Python Capstone Project (Advanced)
**Student:** Nafri | **ID:** CDS_INT_202693138
**Project:** Expense Tracker + Mini E-Commerce API with Live Dashboard

## What I Built
Portfolio-ready Python application combining:
1. Expense Tracker (CRUD, summary, category filtering)
2. Inventory System (Products)
3. E-commerce Order System with stock validation
4. Full logging, exception safety, modular structure
5. Live Bootstrap dashboard

## Architecture
- **Backend:** Flask + Flask-CORS
- **DB:** SQLite with 3 tables (expenses, products, orders) + foreign key logic
- **Frontend:** Jinja template + Bootstrap 5 + Vanilla JS
- **Logging:** Python logging module
- **Structure:** app.py (main), templates/index.html, static/, capstone.db (auto init)

## Database Schema
**expenses:** id, title, amount, category, date, notes
**products:** id, name, price, stock, category
**orders:** id, product_id (FK), quantity, total, customer, created_at

## Setup Instructions
```bash
git clone https://github.com/nafris565-cmyk/codomax-module-6-capstone
pip install -r requirements.txt
python app.py  # auto creates DB + seed data
# Open http://localhost:5000
```

## Deployment (For Live Link)
1. Push to GitHub
2. Go to render.com -> New Web Service -> Connect GitHub repo
3. Build Command: pip install -r requirements.txt
4. Start Command: gunicorn app:app
5. Deploy -> Copy Live URL -> Submit to Codomax

## API Endpoints
- GET /api/docs, /api/health
- GET/POST /api/expenses, PUT/DELETE /api/expenses/<id>, GET /api/expenses/summary
- GET/POST /api/products
- GET/POST /api/orders

## Submission Links Format
- GitHub: https://github.com/nafris565-cmyk/codomax-module-6-capstone
- Live: https://your-app.onrender.com
- LinkedIn: https://linkedin.com/posts/...

## Author
Nafri Nafri - Codomax Intern
