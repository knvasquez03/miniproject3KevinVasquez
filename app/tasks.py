# INF601 - Advanced Programming in Python

# Kevin Vasquez

# Mini Project 3

from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from .auth import login_required
from .db import get_db

bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@bp.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    tasks = db.execute(
        """
        SELECT task.*, category.name AS category_name
        FROM task
        JOIN category ON task.category_id = category.id
        WHERE task.user_id = ?
        ORDER BY task.id DESC
        """,
        (g.user["id"],)
    ).fetchall()
    return render_template("tasks/dashboard.html", tasks=tasks)

@bp.route("/add", methods=("GET", "POST"))
@login_required
def add_task():
    db = get_db()
    categories = db.execute(
        "SELECT * FROM category WHERE user_id = ? ORDER BY name",
        (g.user["id"],)
    ).fetchall()

    if request.method == "POST":
        title = request.form["title"].strip()
        description = request.form["description"].strip()
        due_date = request.form["due_date"].strip()
        category_id = request.form["category_id"]
        error = None

        if not title:
            error = "Task title is required."
        elif not category_id:
            error = "Category is required."

        if error is None:
            db.execute(
                """
                INSERT INTO task (title, description, due_date, user_id, category_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, description, due_date, g.user["id"], category_id)
            )
            db.commit()
            flash("Task added successfully.")
            return redirect(url_for("tasks.dashboard"))

        flash(error)

    return render_template("tasks/add_task.html", categories=categories)

@bp.route("/categories", methods=("GET", "POST"))
@login_required
def categories():
    db = get_db()

    if request.method == "POST":
        name = request.form["name"].strip()
        if name:
            db.execute(
                "INSERT INTO category (name, user_id) VALUES (?, ?)",
                (name, g.user["id"])
            )
            db.commit()
            flash("Category added successfully.")
            return redirect(url_for("tasks.categories"))
        flash("Category name is required.")

    categories = db.execute(
        "SELECT * FROM category WHERE user_id = ? ORDER BY name",
        (g.user["id"],)
    ).fetchall()

    return render_template("tasks/categories.html", categories=categories)

@bp.route("/completed")
@login_required
def completed():
    db = get_db()
    tasks = db.execute(
        """
        SELECT task.*, category.name AS category_name
        FROM task
        JOIN category ON task.category_id = category.id
        WHERE task.user_id = ? AND task.status = 'Completed'
        ORDER BY task.id DESC
        """,
        (g.user["id"],)
    ).fetchall()
    return render_template("tasks/completed.html", tasks=tasks)

@bp.route("/complete/<int:id>", methods=("POST",))
@login_required
def complete_task(id):
    db = get_db()
    db.execute(
        "UPDATE task SET status = 'Completed' WHERE id = ? AND user_id = ?",
        (id, g.user["id"])
    )
    db.commit()
    flash("Task marked as completed.")
    return redirect(url_for("tasks.dashboard"))

@bp.route("/delete/<int:id>", methods=("POST",))
@login_required
def delete_task(id):
    db = get_db()
    db.execute(
        "DELETE FROM task WHERE id = ? AND user_id = ?",
        (id, g.user["id"])
    )
    db.commit()
    flash("Task deleted.")
    return redirect(url_for("tasks.dashboard"))

@bp.route("/profile")
@login_required
def profile():
    db = get_db()

    total_tasks = db.execute(
        "SELECT COUNT(*) AS count FROM task WHERE user_id = ?",
        (g.user["id"],)
    ).fetchone()["count"]

    completed_tasks = db.execute(
        "SELECT COUNT(*) AS count FROM task WHERE user_id = ? AND status = 'Completed'",
        (g.user["id"],)
    ).fetchone()["count"]

    categories_count = db.execute(
        "SELECT COUNT(*) AS count FROM category WHERE user_id = ?",
        (g.user["id"],)
    ).fetchone()["count"]

    return render_template(
        "tasks/profile.html",
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        categories_count=categories_count
    )