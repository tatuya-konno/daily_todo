from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)

DB = "todo.db"


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            todo_type TEXT NOT NULL,
            weekdays TEXT,
            target_date TEXT,
            done INTEGER DEFAULT 0,
            done_date TEXT
        )
    """)

    conn.commit()
    conn.close()


@app.route("/")
def index():
    init_db()

    today = date.today()
    today_str = str(today)
    weekday = str(today.weekday())

    conn = get_db()

    todos = conn.execute("""
        SELECT * FROM todos
        WHERE
            (
                todo_type = 'weekday'
                AND weekdays LIKE ?
            )
            OR
            (
                todo_type = 'today'
                AND target_date = ?
            )
            OR
            (
                todo_type = 'always'
                AND (done = 0 OR done_date = ?)
            )
        ORDER BY id
    """, (f"%{weekday}%", today_str, today_str)).fetchall()

    conn.close()

    return render_template(
        "index.html",
        todos=todos,
        today=today_str
    )


@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    todo_type = request.form["todo_type"]

    weekdays = ""
    target_date = None

    if todo_type == "weekday":
        selected_days = request.form.getlist("weekdays")
        weekdays = ",".join(selected_days)

    elif todo_type == "today":
        target_date = str(date.today())

    conn = get_db()

    conn.execute("""
        INSERT INTO todos
        (name, todo_type, weekdays, target_date)
        VALUES (?, ?, ?, ?)
    """, (
        name,
        todo_type,
        weekdays,
        target_date
    ))

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/toggle/<int:todo_id>")
def toggle(todo_id):
    conn = get_db()

    todo = conn.execute(
        "SELECT * FROM todos WHERE id = ?",
        (todo_id,)
    ).fetchone()

    if todo:
        today = str(date.today())

        if todo["todo_type"] == "always":
            conn.execute("""
                UPDATE todos
                SET done = 1, done_date = ?
                WHERE id = ?
            """, (today, todo_id))

        else:
            conn.execute("""
                UPDATE todos
                SET done = 1, done_date = ?
                WHERE id = ?
            """, (today, todo_id))

        conn.commit()

    conn.close()

    return redirect("/")


@app.route("/delete/<int:todo_id>")
def delete(todo_id):
    conn = get_db()

    conn.execute(
        "DELETE FROM todos WHERE id = ?",
        (todo_id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)