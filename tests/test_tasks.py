from datetime import date, timedelta
from app import db
from app.models.task import Task


class TestTaskCRUD:
    def test_create_task(self, auth_client, test_course):
        due = (date.today() + timedelta(days=5)).isoformat()
        response = auth_client.post(
            "/tasks/new",
            data={
                "title": "Submit lab report",
                "description": "",
                "course_id": test_course,
                "due_date": due,
                "priority": "High",
                "category": "Assignment",
            },
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Submit lab report" in response.data

    def test_create_task_requires_title_course_and_date(self, auth_client, test_course):
        response = auth_client.post(
            "/tasks/new",
            data={"title": "", "course_id": test_course, "due_date": ""},
        )
        assert b"required" in response.data.lower()

    def test_new_task_redirects_to_add_course_if_none_exist(self, auth_client):
        response = auth_client.get("/tasks/new", follow_redirects=True)
        assert b"course" in response.data.lower()

    def test_toggle_task_completion(self, app, auth_client, test_user, test_course):
        user_id, _ = test_user
        with app.app_context():
            task = Task(user_id=user_id, course_id=test_course, title="Toggle me",
                        due_date=date.today() + timedelta(days=1))
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        auth_client.post(f"/tasks/{task_id}/toggle")
        with app.app_context():
            assert Task.query.get(task_id).completed is True

        auth_client.post(f"/tasks/{task_id}/toggle")
        with app.app_context():
            assert Task.query.get(task_id).completed is False

    def test_delete_task(self, app, auth_client, test_user, test_course):
        user_id, _ = test_user
        with app.app_context():
            task = Task(user_id=user_id, course_id=test_course, title="Delete me",
                        due_date=date.today())
            db.session.add(task)
            db.session.commit()
            task_id = task.id

        auth_client.post(f"/tasks/{task_id}/delete")
        with app.app_context():
            assert Task.query.get(task_id) is None


class TestTaskFiltering:
    def _make_task(self, app, user_id, course_id, title, completed=False, days_offset=1):
        with app.app_context():
            task = Task(
                user_id=user_id, course_id=course_id, title=title,
                due_date=date.today() + timedelta(days=days_offset), completed=completed,
            )
            db.session.add(task)
            db.session.commit()

    def test_filter_by_status_pending(self, app, auth_client, test_user, test_course):
        user_id, _ = test_user
        self._make_task(app, user_id, test_course, "Pending one", completed=False)
        self._make_task(app, user_id, test_course, "Done one", completed=True)

        response = auth_client.get("/tasks/?status=pending")
        assert b"Pending one" in response.data
        assert b"Done one" not in response.data

    def test_filter_by_status_completed(self, app, auth_client, test_user, test_course):
        user_id, _ = test_user
        self._make_task(app, user_id, test_course, "Pending two", completed=False)
        self._make_task(app, user_id, test_course, "Done two", completed=True)

        response = auth_client.get("/tasks/?status=completed")
        assert b"Done two" in response.data
        assert b"Pending two" not in response.data


class TestDashboardBuckets:
    def test_overdue_due_today_and_upcoming_are_bucketed_correctly(self, app, auth_client, test_user, test_course):
        user_id, _ = test_user
        with app.app_context():
            overdue = Task(user_id=user_id, course_id=test_course, title="Overdue task",
                            due_date=date.today() - timedelta(days=2))
            today = Task(user_id=user_id, course_id=test_course, title="Today task",
                         due_date=date.today())
            upcoming = Task(user_id=user_id, course_id=test_course, title="Upcoming task",
                             due_date=date.today() + timedelta(days=3))
            far_future = Task(user_id=user_id, course_id=test_course, title="Far future task",
                               due_date=date.today() + timedelta(days=30))
            db.session.add_all([overdue, today, upcoming, far_future])
            db.session.commit()

        response = auth_client.get("/dashboard")
        body = response.data.decode()
        assert "Overdue task" in body
        assert "Today task" in body
        assert "Upcoming task" in body
        assert "Far future task" not in body

    def test_completed_tasks_excluded_from_dashboard(self, app, auth_client, test_user, test_course):
        user_id, _ = test_user
        with app.app_context():
            done = Task(user_id=user_id, course_id=test_course, title="Already done",
                        due_date=date.today(), completed=True)
            db.session.add(done)
            db.session.commit()

        response = auth_client.get("/dashboard")
        assert b"Already done" not in response.data


class TestTaskIsolation:
    def test_cannot_toggle_another_users_task(self, app, client, test_user, test_course):
        from app.models.user import User

        user_id, _ = test_user
        with app.app_context():
            task = Task(user_id=user_id, course_id=test_course, title="Not yours",
                        due_date=date.today())
            db.session.add(task)
            db.session.commit()
            task_id = task.id

            other = User(email="intruder@example.com")
            other.set_password("password123")
            db.session.add(other)
            db.session.commit()

        client.post("/login", data={"email": "intruder@example.com", "password": "password123"})
        response = client.post(f"/tasks/{task_id}/toggle")
        assert response.status_code == 404