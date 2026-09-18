from datetime import date, timedelta
from app.models.task import Task


def get_filtered_tasks(user, course_id=None, status=None, sort="due_date"):
    query = Task.query.filter_by(user_id=user.id)

    if course_id:
        query = query.filter_by(course_id=course_id)

    if status == "pending":
        query = query.filter_by(completed=False)
    elif status == "completed":
        query = query.filter_by(completed=True)

    if sort == "due_date":
        query = query.order_by(Task.due_date.asc())
    elif sort == "priority":
        # High > Medium > Low — simple case ordering, good enough for v1
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        return sorted(query.all(), key=lambda t: priority_order.get(t.priority, 1))

    return query.all()


def get_dashboard_buckets(user):
    """Returns today's tasks, overdue tasks, and the upcoming-7-days tasks."""
    today = date.today()
    week_from_now = today + timedelta(days=7)

    all_pending = Task.query.filter_by(user_id=user.id, completed=False).all()

    overdue = [t for t in all_pending if t.due_date < today]
    due_today = [t for t in all_pending if t.due_date == today]
    upcoming_week = [t for t in all_pending if today < t.due_date <= week_from_now]

    return {
        "overdue": overdue,
        "due_today": due_today,
        "upcoming_week": upcoming_week,
    }
