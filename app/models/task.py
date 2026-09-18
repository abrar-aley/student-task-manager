import uuid
from datetime import date, datetime, timezone
from app import db

PRIORITIES = ["Low", "Medium", "High"]
CATEGORIES = ["Assignment", "Exam", "Project", "Reading"]


class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    course_id = db.Column(db.String(36), db.ForeignKey("courses.id"), nullable=False, index=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date, nullable=False, index=True)
    priority = db.Column(db.String(10), default="Medium")
    category = db.Column(db.String(20), default="Assignment")
    completed = db.Column(db.Boolean, default=False, index=True)
    reminder_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    @property
    def is_overdue(self):
        return (not self.completed) and self.due_date < date.today()

    def __repr__(self):
        return f"<Task {self.title!r}>"
