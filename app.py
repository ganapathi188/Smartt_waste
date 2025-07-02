import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = "admin_secret"
app.config['UPLOAD_FOLDER'] = 'static/uploads'

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        image TEXT,
        description TEXT,
        latitude TEXT,
        longitude TEXT,
        status TEXT,
        created_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )''')
    c.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ('admin', 'admin123'))
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        image = request.files['image']
        description = request.form['description']
        lat = request.form['latitude']
        lon = request.form['longitude']
        filename = image.filename
        image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO reports (image, description, latitude, longitude, status, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                  (filename, description, lat, lon, "Pending", datetime.now()))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template("report.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if 'username' not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM reports ORDER BY created_at DESC")
    reports = c.fetchall()
    conn.close()
    return render_template("admin.html", reports=reports)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['username'] = username
            return redirect(url_for('admin'))
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route("/update_status/<int:report_id>/<string:status>")
def update_status(report_id, status):
    if 'username' not in session:
        return redirect(url_for("login"))
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("UPDATE reports SET status = ? WHERE id = ?", (status, report_id))
    conn.commit()
    conn.close()
    return redirect(url_for('admin'))

if __name__ == "__main__":
    app.run(debug=True)