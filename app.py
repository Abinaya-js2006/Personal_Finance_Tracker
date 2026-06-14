import sqlite3
from flask import Flask, render_template, request, redirect, session
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = "finance_tracker_secret"
def create_table():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            category TEXT,
            amount REAL
        )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    ''')

    conn.commit()
    conn.close()

create_table()

def generate_chart():

    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    cursor.execute("""
        SELECT category, SUM(amount)
        FROM transactions
        WHERE type='Expense'
        GROUP BY category
    """)

    data = cursor.fetchall()
    conn.close()

    if len(data) > 0:

        categories = [row[0] for row in data]
        amounts = [row[1] for row in data]

        plt.figure(figsize=(6,6))

@app.route('/')
def home():
    if 'user' not in session:
       return redirect('/login')
    generate_chart()
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transactions")
    data = cursor.fetchall()

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='Income'")
    total_income = cursor.fetchone()[0] or 0

    cursor.execute("SELECT SUM(amount) FROM transactions WHERE type='Expense'")
    total_expense = cursor.fetchone()[0] or 0

    balance = total_income - total_expense

    conn.close()

    return render_template(
        'index.html',
        transactions=data,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance
    )

@app.route('/add', methods=['POST'])
def add():

    transaction_type = request.form['type']
    category = request.form['category']
    amount = request.form['amount']

    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO transactions(type, category, amount) VALUES (?, ?, ?)",
        (transaction_type, category, amount)
    )

    conn.commit()
    conn.close()

    return redirect('/')



@app.route('/delete/<int:id>')
def delete(id):

    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM transactions WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/')

@app.route('/transactions')
def transactions():

    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM transactions")
    data = cursor.fetchall()

    conn.close()

    return render_template(
        'transactions.html',
        transactions=data
    )
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users(username,password) VALUES (?,?)",
            (username,password)
        )

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')
@app.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username,password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session['user'] = username

            return redirect('/')

    return render_template('login.html')
@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)