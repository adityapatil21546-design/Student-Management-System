
from flask import Flask, request, redirect, render_template_string
import sqlite3

app = Flask(__name__)

def get_db():
    con = sqlite3.connect("students.db")
    con.row_factory = sqlite3.Row
    return con

def setup():
    con = get_db()
    con.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            roll TEXT NOT NULL,
            course TEXT NOT NULL
        )
    """)
    con.commit()
    con.close()

PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>StudentHub | Dashboard</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: 'Segoe UI', Arial, sans-serif;
    background: #f3f5fb;
    color: #202943;
}
.sidebar {
    position: fixed;
    width: 235px;
    height: 100vh;
    background: linear-gradient(160deg,#172554,#312e81);
    padding: 30px 20px;
    color: white;
}
.brand {
    font-size: 25px;
    font-weight: bold;
    margin-bottom: 50px;
}
.brand span { color: #a5b4fc; }
.menu {
    padding: 14px;
    background: #ffffff20;
    border-radius: 9px;
    margin-bottom: 12px;
}
.menu a { color: white; text-decoration: none; }
.sidebar p {
    color: #c7d2fe;
    font-size: 13px;
    margin-top: 50px;
}
.main {
    margin-left: 235px;
    padding: 35px;
}
.topbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    gap: 15px;
}
.topbar h1 { margin: 0; font-size: 28px; }
.topbar p { color: #7b849c; margin-top: 7px; }
.profile {
    background: white;
    padding: 12px 18px;
    border-radius: 12px;
    font-weight: bold;
}
.stats {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: 20px;
    margin-bottom: 25px;
}
.stat {
    background: white;
    padding: 24px;
    border-radius: 15px;
    box-shadow: 0 4px 15px #2029430b;
}
.stat small { color: #818ba2; }
.stat h2 { font-size: 30px; margin: 12px 0 0; }
.icon { font-size: 25px; }
.content {
    display: grid;
    grid-template-columns: 320px 1fr;
    gap: 22px;
}
.card {
    background: white;
    padding: 25px;
    border-radius: 15px;
    box-shadow: 0 4px 15px #2029430b;
}
.card h3 { margin-top: 0; }
label {
    display: block;
    margin: 16px 0 7px;
    font-size: 13px;
    font-weight: 600;
}
input {
    width: 100%;
    padding: 12px;
    border: 1px solid #dce1ed;
    border-radius: 8px;
    outline: none;
}
input:focus { border-color: #6366f1; }
.add-btn {
    width: 100%;
    margin-top: 22px;
    padding: 13px;
    background: linear-gradient(90deg,#4f46e5,#7c3aed);
    color: white;
    border: 0;
    border-radius: 8px;
    font-weight: bold;
    cursor: pointer;
}
.search {
    margin: 12px 0 20px;
    max-width: 260px;
}
.table-wrap { overflow-x: auto; }
table {
    width: 100%;
    border-collapse: collapse;
    min-width: 480px;
}
th {
    text-align: left;
    padding: 14px 10px;
    background: #f6f7fc;
    color: #68738b;
    font-size: 12px;
}
td {
    padding: 15px 10px;
    border-bottom: 1px solid #edf0f6;
    font-size: 13px;
}
.pill {
    background: #eef2ff;
    color: #4f46e5;
    padding: 6px 10px;
    border-radius: 20px;
}
.delete {
    background: #fee2e2;
    color: #dc2626;
    border: 0;
    padding: 7px 10px;
    border-radius: 6px;
    cursor: pointer;
}
.empty {
    text-align: center;
    padding: 35px;
    color: #8992a5;
}
.footer {
    text-align: center;
    margin-top: 30px;
    color: #8992a5;
    font-size: 12px;
}
@media(max-width:950px) {
    .content { grid-template-columns: 1fr; }
}
@media(max-width:650px) {
    .sidebar { position: static; width: 100%; height: auto; }
    .brand { margin-bottom: 15px; }
    .sidebar p { display: none; }
    .main { margin-left: 0; padding: 18px; }
    .stats { grid-template-columns: 1fr; }
    .topbar { align-items: flex-start; }
}
</style>
</head>
<body>

<aside class="sidebar">
    <div class="brand">Student<span>Hub.</span></div>
    <div class="menu">▦ &nbsp; <a href="/">Dashboard</a></div>
    <div class="menu">♙ &nbsp; <a href="#students">Students</a></div>
    <div class="menu">＋ &nbsp; <a href="#add">Add Student</a></div>
    <p>STUDENT MANAGEMENT SYSTEM<br>Version 1.0</p>
</aside>

<main class="main">
    <header class="topbar">
        <div>
            <h1>Dashboard</h1>
            <p>Welcome! Manage your student records here.</p>
        </div>
        <div class="profile">👤 Admin</div>
    </header>

    <section class="stats">
        <div class="stat">
            <div class="icon">👨‍🎓</div>
            <small>Total Students</small>
            <h2>{{ total }}</h2>
        </div>
        <div class="stat">
            <div class="icon">📚</div>
            <small>Courses Registered</small>
            <h2>{{ courses }}</h2>
        </div>
        <div class="stat">
            <div class="icon">💻</div>
            <small>System Status</small>
            <h2 style="color:#16a34a;font-size:23px">Active</h2>
        </div>
    </section>

    <section class="content">
        <div class="card" id="add">
            <h3>＋ Add New Student</h3>
            <p style="color:#8992a5;font-size:13px">
                Enter student information below.
            </p>
            <form action="/add" method="POST">
                <label>Student Name</label>
                <input name="name" placeholder="Enter full name" required maxlength="80">

                <label>Roll Number</label>
                <input name="roll" placeholder="Enter roll number" required maxlength="30">

                <label>Course</label>
                <input name="course" placeholder="Enter course name" required maxlength="60">

                <button class="add-btn">+ Register Student</button>
            </form>
        </div>

        <div class="card" id="students">
            <h3>Student Records</h3>
            <input class="search" id="search" placeholder="🔍 Search students..." onkeyup="searchStudents()">

            <div class="table-wrap">
            <table id="studentTable">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>NAME</th>
                        <th>ROLL NO.</th>
                        <th>COURSE</th>
                        <th>ACTION</th>
                    </tr>
                </thead>
                <tbody>
                {% for s in students %}
                    <tr>
                        <td>#{{ s.id }}</td>
                        <td><b>{{ s.name }}</b></td>
                        <td>{{ s.roll }}</td>
                        <td><span class="pill">{{ s.course }}</span></td>
                        <td>
                            <form action="/delete/{{ s.id }}" method="POST"
                            onsubmit="return confirm('Delete this student?')">
                                <button class="delete">Delete</button>
                            </form>
                        </td>
                    </tr>
                {% else %}
                    <tr><td colspan="5" class="empty">
                    No students registered yet.
                    </td></tr>
                {% endfor %}
                </tbody>
            </table>
            </div>
        </div>
    </section>

    <div class="footer">
        StudentHub | Python Flask + SQLite | College Mini Project
    </div>
</main>

<script>
function searchStudents() {
    let input = document.getElementById("search").value.toLowerCase();
    let rows = document.querySelectorAll("#studentTable tbody tr");

    rows.forEach(row => {
        row.style.display = row.innerText.toLowerCase().includes(input)
            ? "" : "none";
    });
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    con = get_db()
    students = con.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    total = len(students)
    courses = con.execute(
        "SELECT COUNT(DISTINCT course) FROM students"
    ).fetchone()[0]
    con.close()

    return render_template_string(
        PAGE, students=students, total=total, courses=courses
    )

@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"].strip()
    roll = request.form["roll"].strip()
    course = request.form["course"].strip()

    if name and roll and course:
        con = get_db()
        con.execute(
            "INSERT INTO students(name,roll,course) VALUES(?,?,?)",
            (name, roll, course)
        )
        con.commit()
        con.close()

    return redirect("/")

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    con = get_db()
    con.execute("DELETE FROM students WHERE id=?", (id,))
    con.commit()
    con.close()
    return redirect("/")

if __name__ == "__main__":
    setup()
    app.run(debug=True)


