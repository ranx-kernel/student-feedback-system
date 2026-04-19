import matplotlib.pyplot as plt
from db import connect_db

def show_dashboard():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.course_name, AVG(f.rating)
        FROM Feedback f
        JOIN Course c ON f.course_id = c.course_id
        GROUP BY c.course_name
    """)

    data = cursor.fetchall()

    if not data:
        print("No data available!")
        return

    courses = [row[0] for row in data]
    ratings = [row[1] for row in data]

    plt.bar(courses, ratings)
    plt.title("Average Course Ratings")
    plt.xlabel("Courses")
    plt.ylabel("Ratings")
    plt.show()

    conn.close()

show_dashboard()