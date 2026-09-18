from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.services.task_service import get_dashboard_buckets

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@login_required
def index():
    buckets = get_dashboard_buckets(current_user)
    return render_template("dashboard/index.html", **buckets)


@dashboard_bp.route("/")
def root():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))
