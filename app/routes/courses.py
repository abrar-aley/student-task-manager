from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app import db
from app.models.course import Course

courses_bp = Blueprint("courses", __name__, url_prefix="/courses")


@courses_bp.route("/")
@login_required
def index():
    courses = current_user.courses.order_by(Course.name).all()
    return render_template("courses/index.html", courses=courses)


@courses_bp.route("/new", methods=["GET", "POST"])
@login_required
def new():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Course name is required.", "error")
            return render_template("courses/form.html", course=None)

        course = Course(
            user_id=current_user.id,
            name=name,
            code=request.form.get("code", "").strip() or None,
            instructor=request.form.get("instructor", "").strip() or None,
        )
        db.session.add(course)
        db.session.commit()
        return redirect(url_for("courses.index"))

    return render_template("courses/form.html", course=None)


@courses_bp.route("/<course_id>/edit", methods=["GET", "POST"])
@login_required
def edit(course_id):
    course = Course.query.filter_by(id=course_id, user_id=current_user.id).first_or_404()

    if request.method == "POST":
        course.name = request.form.get("name", "").strip()
        course.code = request.form.get("code", "").strip() or None
        course.instructor = request.form.get("instructor", "").strip() or None
        db.session.commit()
        return redirect(url_for("courses.index"))

    return render_template("courses/form.html", course=course)


@courses_bp.route("/<course_id>/delete", methods=["POST"])
@login_required
def delete(course_id):
    course = Course.query.filter_by(id=course_id, user_id=current_user.id).first_or_404()
    db.session.delete(course)
    db.session.commit()
    return redirect(url_for("courses.index"))
