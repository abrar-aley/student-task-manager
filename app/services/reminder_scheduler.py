from datetime import date, timedelta
from app import db
from app.models.task import Task
from app.models.user import User
from app.services.email_service import send_deadline_reminder

REMINDER_LEAD_DAYS = 1


def check_and_send_reminders(app):
    """Finds tasks due tomorrow that haven't been reminded about yet, and emails their owners.
    Runs inside an app context because it's called from a background scheduler, not a request."""
    with app.app_context():
        target_date = date.today() + timedelta(days=REMINDER_LEAD_DAYS)

        due_tasks = Task.query.filter_by(
            due_date=target_date,
            completed=False,
            reminder_sent=False,
        ).all()

        for task in due_tasks:
            user = User.query.get(task.user_id)
            if not user:
                continue
            try:
                send_deadline_reminder(user.email, task.title, task.due_date)
                task.reminder_sent = True
            except Exception as e:
                app.logger.error(f"Failed to send reminder for task {task.id}: {e}")

        db.session.commit()