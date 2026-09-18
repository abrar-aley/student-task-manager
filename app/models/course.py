import uuid
from app import db


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    code = db.Column(db.String(30))
    instructor = db.Column(db.String(120))

    tasks = db.relationship("Task", backref="course", cascade="all, delete-orphan", lazy="dynamic")

    def __repr__(self):
        return f"<Course {self.code or self.name}>"
