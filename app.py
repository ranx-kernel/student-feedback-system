from flask import Flask, render_template, request, redirect, session, send_file
from db import connect_db
from sentiment import analyze_sentiment
import matplotlib.pyplot as plt
import csv

app = Flask(__name__)
app.secret_key = "secret123"

# ---------- INIT DB ----------
def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        course TEXT,
        rating INTEGER,
        comments TEXT,
        sentiment TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- LOGIN ----------
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        user = request.form['username']
        pwd = request.form['password']

        # Dummy credentials (can upgrade later)
        if role == "student" and user == "student" and pwd == "123":
            session['role'] = "student"
            return redirect('/student')

        elif role == "staff" and user == "staff" and pwd == "123":
            session['role'] = "staff"
            return redirect('/staff')

        elif role == "admin" and user == "admin" and pwd == "123":
            session['role'] = "admin"
            return redirect('/admin')

        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")


# ---------- LOGOUT ----------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------- HOME ----------
@app.route('/')
def home():
    return redirect('/login')


# ---------- STUDENT ----------
@app.route('/student')
def student():
    if session.get('role') != "student":
        return redirect('/login')
    return render_template("index.html")


# ---------- SUBMIT FEEDBACK ----------
@app.route('/submit', methods=['POST'])
def submit():
    if session.get('role') != "student":
        return redirect('/login')

    name = request.form['name']
    course = request.form['course']
    rating = int(request.form['rating'])
    comments = request.form['comments']

    sentiment = analyze_sentiment(comments)

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO Feedback (name, course, rating, comments, sentiment) VALUES (?, ?, ?, ?, ?)",
        (name, course, rating, comments, sentiment)
    )

    conn.commit()
    conn.close()

    return render_template("index.html", message=f"Feedback submitted! Sentiment: {sentiment}")


# ---------- STAFF DASHBOARD ----------
@app.route('/staff')
def staff():
    if session.get('role') != "staff":
        return redirect('/login')

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT course, AVG(rating) FROM Feedback GROUP BY course")
    data = cursor.fetchall()

    conn.close()

    courses = [d[0] for d in data]
    ratings = [d[1] for d in data]

    # Chart
    plt.figure(figsize=(5,3))
    plt.bar(courses, ratings)
    plt.title("Course Ratings")
    plt.tight_layout()
    plt.savefig("static/chart.png")
    plt.close()

    return render_template("dashboard.html", data=data)


# ---------- ADMIN PANEL ----------
@app.route('/admin')
def admin():
    if session.get('role') != "admin":
        return redirect('/login')

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Feedback")
    data = cursor.fetchall()

    conn.close()

    return render_template("admin.html", data=data)


# ---------- DELETE ----------
@app.route('/delete/<int:id>')
def delete(id):
    if session.get('role') != "admin":
        return redirect('/login')

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM Feedback WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/admin')


# ---------- EXPORT ----------
@app.route('/export')
def export():
    if session.get('role') != "admin":
        return redirect('/login')

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM Feedback")
    data = cursor.fetchall()

    conn.close()

    with open("report.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["ID","Name","Course","Rating","Comments","Sentiment"])
        writer.writerows(data)

    return send_file("report.csv", as_attachment=True)


# ---------- RUN ----------
if __name__ == '__main__':
    app.run(debug=True)