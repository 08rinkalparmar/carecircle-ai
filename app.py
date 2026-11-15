
import os
import sqlite3
from functools import wraps
from datetime import datetime

from flask import (
    Flask, render_template, request,
    redirect, url_for, session, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get(
    "SECRET_KEY", "carecircle-demo-secret-key"
)

os.makedirs(app.instance_path, exist_ok=True)
DATABASE = os.path.join(app.instance_path, "carecircle.db")


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                relative_name TEXT,
                relative_email TEXT,
                relative_phone TEXT,
                caretaker_name TEXT,
                caretaker_email TEXT,
                caretaker_phone TEXT,
                doctor_name TEXT,
                doctor_email TEXT,
                doctor_phone TEXT
            )
        """)

        db.execute("""
            CREATE TABLE IF NOT EXISTS health_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                heart_rate INTEGER NOT NULL,
                systolic INTEGER NOT NULL,
                diastolic INTEGER NOT NULL,
                steps INTEGER NOT NULL,
                recorded_at TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return wrapper


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        with get_db() as db:
            user = db.execute(
                "SELECT * FROM users WHERE email = ?",
                (email,)
            ).fetchone()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))

        return render_template(
            "login_page.html",
            error="Invalid email or password."
        )

    return render_template("login_page.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        patient_name = request.form.get("patient_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        relative_name = request.form.get("relative_name", "").strip()
        relative_email = request.form.get("relative_email", "").strip()
        relative_phone = request.form.get("relative_phone", "").strip()

        caretaker_name = request.form.get("caretaker_name", "").strip()
        caretaker_email = request.form.get("caretaker_email", "").strip()
        caretaker_phone = request.form.get("caretaker_phone", "").strip()

        doctor_name = request.form.get("doctor_name", "").strip()
        doctor_email = request.form.get("doctor_email", "").strip()
        doctor_phone = request.form.get("doctor_phone", "").strip()

        if not patient_name or not email or not password:
            return render_template(
                "register_page.html",
                error="Please fill in your name, email and password."
            )

        if len(password) < 8:
            return render_template(
                "register_page.html",
                error="Password must contain at least 8 characters."
            )

        hashed_password = generate_password_hash(password)

        try:
            with get_db() as db:
                db.execute("""
                    INSERT INTO users (
                        patient_name, email, password,
                        relative_name, relative_email, relative_phone,
                        caretaker_name, caretaker_email, caretaker_phone,
                        doctor_name, doctor_email, doctor_phone
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    patient_name, email, hashed_password,
                    relative_name, relative_email, relative_phone,
                    caretaker_name, caretaker_email, caretaker_phone,
                    doctor_name, doctor_email, doctor_phone
                ))

            return redirect(url_for("login"))

        except sqlite3.IntegrityError:
            return render_template(
                "register_page.html",
                error="This email is already registered."
            )

    return render_template("register_page.html")


@app.route("/dashboard")
@login_required
def dashboard():
    with get_db() as db:
        user = db.execute(
            "SELECT * FROM users WHERE id = ?",
            (session["user_id"],)
        ).fetchone()

        latest_reading = db.execute("""
            SELECT * FROM health_readings
            WHERE user_id = ?
            ORDER BY id DESC LIMIT 1
        """, (session["user_id"],)).fetchone()

    if user is None:
        session.clear()
        return redirect(url_for("login"))

    return render_template(
        "dashboard.html",
        user_name=user["patient_name"],
        user=user,
        latest_reading=latest_reading
    )


# Save health readings for the logged-in user
@app.route("/save-health", methods=["POST"])
@login_required
def save_health():
    data = request.get_json(silent=True) or {}

    try:
        heart_rate = int(data.get("heart_rate"))
        systolic = int(data.get("systolic"))
        diastolic = int(data.get("diastolic"))
        steps = int(data.get("steps"))

        if min(heart_rate, systolic, diastolic) <= 0 or steps < 0:
            return jsonify({
                "success": False,
                "message": "Please enter valid positive readings and non-negative steps."
            }), 400

    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Please enter all four readings as numbers."
        }), 400

    recorded_at = datetime.now().isoformat(timespec="seconds")

    with get_db() as db:
        db.execute("""
            INSERT INTO health_readings (
                user_id, heart_rate, systolic,
                diastolic, steps, recorded_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            session["user_id"],
            heart_rate,
            systolic,
            diastolic,
            steps,
            recorded_at
        ))

    return jsonify({
        "success": True,
        "message": "Your health readings have been saved."
    })


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


init_db()


if __name__ == "__main__":
    app.run(debug=True)
