from datetime import date, timedelta
from unittest.mock import patch
from app import db
from app.models.task import Task
from app.services.reminder_scheduler import check_and_send_reminders


class TestReminderScheduler:
    def test_sends_reminder_for_task_due_tomorrow(self, app, test_user, test_course):
        user_id, email = test_user
        with app.app_context():
            task = Task(user_id=user_id, course_id=test_course, title="Due tomorrow",
                        due_date=date.today() + timedelta(days=1))
            db.session.add(task)
            db.session.commit()

        with patch("app.services.reminder_scheduler.send_deadline_reminder") as mock_send:
            check_and_send_reminders(app)
            assert mock_send.call_count == 1
            assert mock_send.call_args[0][0] == email
            assert mock_send.call_args[0][1] == "Due tomorrow"

    def test_does_not_remind_tasks_further_out(self, app, test_user, test_course):
        user_id, _ = test_user
        with app.app_context():
            task = Task(user_id=user_id, course_id=test_course, title="Due in 5 days",
                        due_date=date.today() + timedelta(days=5))
            db.session.add(task)
            db.session.commit()

        with patch("app.services.reminder_scheduler.send_deadline_reminder") as mock_send:
            check_and_send_reminders(app)
            assert mock_send.call_count == 0

    def test_does_not_remind_completed_tasks(self, app, test_user, test_course):
        user_id, _ = test_user
        with app.app_context():
            task = Task(user_id=user_id, course_id=test_course, title="Done already",
                        due_date=date.today() + timedelta(days=1), completed=True)
            db.session.add(task)
            db.session.commit()

        with patch("app.services.reminder_scheduler.send_deadline_reminder") as mock_send:
            check_and_send_reminders(app)
            assert mock_send.call_count == 0

    def test_does_not_send_duplicate_reminder_on_second_run(self, app, test_user, test_course):
        user_id, _ = test_user
        with app.app_context():
            task = Task(user_id=user_id, course_id=test_course, title="Remind once",
                        due_date=date.today() + timedelta(days=1))
            db.session.add(task)
            db.session.commit()

        with patch("app.services.reminder_scheduler.send_deadline_reminder"):
            check_and_send_reminders(app)

        with patch("app.services.reminder_scheduler.send_deadline_reminder") as mock_send_again:
            check_and_send_reminders(app)
            assert mock_send_again.call_count == 0

    def test_marks_reminder_sent_after_sending(self, app, test_user, test_course):
        user_id, _ = test_user
        with app.app_context():
            task = Task(user_id=user_id, course_id=test_course, title="Check the flag",
                        due_date=date.today() + timedelta(days=1))
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        with patch("app.services.reminder_scheduler.send_deadline_reminder"):
            check_and_send_reminders(app)

        with app.app_context():
            assert Task.query.get(task_id).reminder_sent is True