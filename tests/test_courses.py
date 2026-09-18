from app.models.user import User
from app.models.course import Course
from app import db


class TestCourseCRUD:
    def test_create_course(self, auth_client, test_user):
        response = auth_client.post(
            "/courses/new",
            data={"name": "Discrete Structures", "code": "CSC-102", "instructor": ""},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert b"Discrete Structures" in response.data

    def test_create_course_requires_name(self, auth_client):
        response = auth_client.post("/courses/new", data={"name": "", "code": ""})
        assert b"required" in response.data.lower()

    def test_edit_course(self, auth_client, test_course):
        response = auth_client.post(
            f"/courses/{test_course}/edit",
            data={"name": "Object Oriented Programming (Updated)", "code": "CSC-241", "instructor": ""},
            follow_redirects=True,
        )
        assert b"Updated" in response.data

    def test_delete_course(self, auth_client, test_course):
        auth_client.post(f"/courses/{test_course}/delete", follow_redirects=True)
        response = auth_client.get("/courses/")
        assert b"Object Oriented Programming" not in response.data

    def test_deleting_course_cascades_to_its_tasks(self, app, auth_client, test_user, test_course):
        from app.models.task import Task
        from datetime import date, timedelta

        user_id, _ = test_user
        with app.app_context():
            task = Task(
                user_id=user_id,
                course_id=test_course,
                title="Some task",
                due_date=date.today() + timedelta(days=3),
            )
            db.session.add(task)
            db.session.commit()

        auth_client.post(f"/courses/{test_course}/delete")

        with app.app_context():
            assert Task.query.filter_by(course_id=test_course).count() == 0


class TestCourseIsolation:
    def test_cannot_edit_another_users_course(self, app, client, test_course):
        with app.app_context():
            other = User(email="other@example.com")
            other.set_password("password123")
            db.session.add(other)
            db.session.commit()

        client.post("/login", data={"email": "other@example.com", "password": "password123"})

        response = client.get(f"/courses/{test_course}/edit")
        assert response.status_code == 404