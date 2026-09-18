import uuid
from datetime import datetime, timezone
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from app import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    courses = db.relationship("Course", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    tasks = db.relationship("Task", backref="user", cascade="all, delete-orphan", lazy="dynamic")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def get_reset_token(self):
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        return serializer.dumps(self.id, salt="password-reset")

    @staticmethod
    def verify_reset_token(token, max_age_seconds=1800):
        serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
        try:
            user_id = serializer.loads(token, salt="password-reset", max_age=max_age_seconds)
        except (BadSignature, SignatureExpired):
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"<User {self.email}>"