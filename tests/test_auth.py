from app.models.user import User
from unittest.mock import patch


class TestSignup:
    def test_signup_creates_user_and_logs_in(self, client):
        response = client.post(
            "/signup",
            data={"email": "new@example.com", "password": "password123"},
            follow_redirects=True,
        )
        assert response.status_code == 200
        assert response.request.path == "/dashboard"

    def test_signup_rejects_duplicate_email(self, client, test_user):
        _, email = test_user
        response = client.post(
            "/signup",
            data={"email": email, "password": "anotherpassword"},
            follow_redirects=True,
        )
        assert b"already registered" in response.data

    def test_signup_rejects_missing_fields(self, client):
        response = client.post("/signup", data={"email": "", "password": ""})
        assert response.status_code == 200
        assert b"required" in response.data.lower()


class TestLogin:
    def test_login_with_correct_credentials_succeeds(self, client, test_user):
        _, email = test_user
        response = client.post(
            "/login",
            data={"email": email, "password": "password123"},
            follow_redirects=True,
        )
        assert response.request.path == "/dashboard"

    def test_login_with_wrong_password_fails(self, client, test_user):
        _, email = test_user
        response = client.post(
            "/login",
            data={"email": email, "password": "wrongpassword"},
        )
        assert b"Wrong email or password" in response.data

    def test_login_with_unknown_email_fails(self, client):
        response = client.post(
            "/login",
            data={"email": "nobody@example.com", "password": "whatever"},
        )
        assert b"Wrong email or password" in response.data

    def test_dashboard_requires_login(self, client):
        response = client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 302
        assert "/login" in response.headers["Location"]


class TestLogout:
    def test_logout_ends_session(self, auth_client):
        auth_client.post("/logout")
        response = auth_client.get("/dashboard", follow_redirects=False)
        assert response.status_code == 302


class TestPasswordReset:
    def test_reset_request_sends_email_for_existing_user(self, client, test_user, app):
        _, email = test_user
        with patch("app.routes.auth.send_password_reset_email") as mock_send:
            client.post("/reset-password", data={"email": email})
            assert mock_send.call_count == 1

    def test_reset_request_does_not_reveal_unknown_email(self, client):
        """Same message shown whether or not the email exists — prevents email enumeration."""
        with patch("app.routes.auth.send_password_reset_email") as mock_send:
            response = client.post(
                "/reset-password", data={"email": "unknown@example.com"}, follow_redirects=True
            )
            assert mock_send.call_count == 0
            assert b"reset link has been sent" in response.data

    def test_valid_token_allows_password_change(self, client, test_user, app):
        user_id, email = test_user
        with app.app_context():
            user = User.query.get(user_id)
            token = user.get_reset_token()

        client.post(f"/reset-password/{token}", data={"password": "newpassword456"})

        with app.app_context():
            refreshed = User.query.get(user_id)
            assert refreshed.check_password("newpassword456")
            assert not refreshed.check_password("password123")

    def test_invalid_token_is_rejected(self, client):
        response = client.get("/reset-password/not-a-real-token", follow_redirects=True)
        assert b"invalid or has expired" in response.data

    def test_reset_password_too_short_is_rejected(self, client, test_user, app):
        user_id, _ = test_user
        with app.app_context():
            token = User.query.get(user_id).get_reset_token()

        response = client.post(f"/reset-password/{token}", data={"password": "short"})
        assert b"at least 8 characters" in response.data