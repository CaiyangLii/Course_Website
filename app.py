
import sqlite3
from courses import courses
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session
DB = "registrations.db"

app = Flask(__name__)
app.secret_key = 'a-unique-and-secret-key-123456'


@app.route('/')
def index():

    lecturers = {}
    for course in courses:
        name = course["lecturer"]
        if name not in lecturers:
            lecturers[name] = {
    "bio": course.get("bio", "No bio available.")
        }
            
    return render_template('index.html', courses=courses, lecturers=lecturers)


@app.route('/course/<int:course_id>')
def course_detail(course_id):
    course = next((c for c in courses if c["id"] == course_id), None)
    return render_template('course_detail.html', course=course)

def init_db():
    with sqlite3.connect(DB) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER,
                name TEXT,
                email TEXT,
                timestamp TEXT
            )
            """
        )
@app.route("/register/<int:course_id>", methods=["POST"])
def register(course_id):
    name = request.form["name"].strip()
    email = request.form["email"].strip()
    timestamp = datetime.now().isoformat(sep=" ", timespec="seconds")

    with sqlite3.connect(DB) as connection:
        connection.execute(
            """
            INSERT INTO registrations (course_id, name, email, timestamp)
            VALUES (?, ?, ?, ?)
            """,
            (course_id, name, email, timestamp),
        )

    return render_template("thankyou.html", name=name)

@app.route("/admin/registrations")
def view_registrations():
    if not session.get("admin"):
        return redirect(url_for("login"))

    with sqlite3.connect(DB) as conn:
        cursor = conn.execute(
            """
            SELECT id, course_id, name, email, timestamp
            FROM registrations ORDER BY id DESC
            """
        )
        rows = cursor.fetchall()

    return render_template("registrations.html", data=rows)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "admin":
            session["admin"] = True
            return redirect(url_for("view_registrations"))

        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")


if __name__ == '__main__':
    init_db() 
    app.run(debug=True)
