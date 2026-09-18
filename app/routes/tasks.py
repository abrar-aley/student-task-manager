from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.task import Task, PRIORITIES, CATEGORIES
from app.models.course import Course
from app.services.task_service import get_filtered_tasks

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("/")
@login_required
def index():
    course_id = request.args.get("course_id") or None
    status = request.args.get("status") or None
    sort = request.args.get("sort", "due_date")

    tasks = get_filtered_tasks(current_user, course_id=course_id, status=status, sort=sort)
    courses = current_user.courses.order_by(Course.name).all()

    return render_template(
        "tasks/index.html",
        tasks=tasks,
        courses=courses,
        selected_course=course_id,
        selected_status=status,
        selected_sort=sort,
    )


@tasks_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    courses = current_user.courses.order_by(Course.name).all()

    if not courses:
        flash("Add a course first before creating a task.", "error")
        return redirect(url_for("courses.new"))

    if request.method == "POST":
        task = _build_task_from_form(request.form, current_user.id)
        if task is None:
            return render_template("tasks/form.html", task=None, courses=courses,
                                    priorities=PRIORITIES, categories=CATEGORIES)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for("tasks.index"))

    return render_template("tasks/form.html", task=None, courses=courses,
                            priorities=PRIORITIES, categories=CATEGORIES)


@tasks_bp.route("/<task_id>/edit", methods=["GET", "POST"])
@login_required
def edit(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    courses = current_user.courses.order_by(Course.name).all()

    if request.method == "POST":
        updated = _build_task_from_form(request.form, current_user.id, existing=task)
        if updated is not None:
            db.session.commit()
            return redirect(url_for("tasks.index"))

    return render_template("tasks/form.html", task=task, courses=courses,
                            priorities=PRIORITIES, categories=CATEGORIES)


@tasks_bp.route("/<task_id>/toggle", methods=["POST"])
@login_required
def toggle(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    task.completed = not task.completed
    db.session.commit()
    return redirect(request.referrer or url_for("tasks.index"))


@tasks_bp.route("/<task_id>/delete", methods=["POST"])
@login_required
def delete(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("tasks.index"))


def _build_task_from_form(form, user_id, existing=None):
    title = form.get("title", "").strip()
    due_date_str = form.get("due_date", "")
    course_id = form.get("course_id")

    if not title or not due_date_str or not course_id:
        flash("Title, course, and due date are required.", "error")
        return None

    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Invalid due date.", "error")
        return None

    task = existing or Task(user_id=user_id)
    task.title = title
    task.description = form.get("description", "").strip()
    task.course_id = course_id
    task.due_date = due_date
    task.priority = form.get("priority", "Medium")
    task.category = form.get("category", "Assignment")

    return task
