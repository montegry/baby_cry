from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3
from weather import get_weather_data
from solar import get_solar_activity

app = Flask(__name__)
DB_PATH = 'cries.db'

# ----- DB INIT -----
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT,
                date TEXT,
                start_time TEXT,
                end_time TEXT,
                temperature REAL,
                pressure REAL,
                solar_activity REAL
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS intervals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                interval_start TEXT,
                interval_end TEXT,
                FOREIGN KEY(session_id) REFERENCES sessions(id)
            )
        ''')
        conn.commit()

# ----- ROUTES -----
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    city = request.form['city']
    date = request.form['date']
    start_time = request.form['start_time']
    end_time = request.form.get('end_time')  # Может быть пустым

    weather = get_weather_data(city)
    solar = get_solar_activity()

    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT INTO sessions (city, date, start_time, end_time, temperature, pressure, solar_activity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            city, date, start_time, end_time,
            weather['temperature'], weather['pressure'], solar
        ))
        session_id = c.lastrowid

        # Добавляем интервалы
        interval_starts = request.form.getlist('interval_start')
        interval_ends = request.form.getlist('interval_end')
        for istart, iend in zip(interval_starts, interval_ends):
            if istart and iend:
                c.execute('''
                    INSERT INTO intervals (session_id, interval_start, interval_end)
                    VALUES (?, ?, ?)
                ''', (session_id, istart, iend))

        conn.commit()

    return redirect(url_for('edit_session', session_id=session_id))

@app.route("/edit/<int:session_id>", methods=["GET", "POST"])
def edit_session(session_id):
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        if request.method == "POST":
            end_time = request.form['end_time']
            c.execute('UPDATE sessions SET end_time = ? WHERE id = ?', (end_time, session_id))

            interval_starts = request.form.getlist('interval_start')
            interval_ends = request.form.getlist('interval_end')
            for istart, iend in zip(interval_starts, interval_ends):
                if istart and iend:
                    c.execute('''
                        INSERT INTO intervals (session_id, interval_start, interval_end)
                        VALUES (?, ?, ?)
                    ''', (session_id, istart, iend))
            conn.commit()
            return redirect(url_for('stats'))

        c.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
        session = c.fetchone()
        c.execute('SELECT interval_start, interval_end FROM intervals WHERE session_id = ?', (session_id,))
        intervals = c.fetchall()

    return render_template("edit.html", session=session, intervals=intervals)

@app.route("/stats")
def stats():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()
        c.execute('''
            SELECT * FROM sessions
        ''')
        sessions = c.fetchall()

        c.execute('''
            SELECT session_id, interval_start, interval_end FROM intervals
        ''')
        intervals = c.fetchall()

    return render_template("stats.html", sessions=sessions, intervals=intervals)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
