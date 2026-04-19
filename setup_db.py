from db import connect_db

conn = connect_db()
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS Student (
    student_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Course (
    course_id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT,
    faculty_name TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Feedback (
    feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    course_id INTEGER,
    rating INTEGER,
    comments TEXT
)
""")

conn.commit()
conn.close()

print("Database and tables created successfully!")