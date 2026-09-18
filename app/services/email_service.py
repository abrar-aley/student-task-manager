from flask_mail import Message
from app import mail


def send_deadline_reminder(user_email, task_title, due_date):
    msg = Message(
        subject=f"Reminder: {task_title} is due soon",
        recipients=[user_email],
        body=(
            f"Just a heads up — \"{task_title}\" is due on {due_date.strftime('%b %d, %Y')}.\n\n"
            "Log in to your task manager to view details."
        ),
    )
    mail.send(msg)


def send_password_reset_email(user_email, reset_url):
    msg = Message(
        subject="Reset your password",
        recipients=[user_email],
        body=(
            "We received a request to reset your password.\n\n"
            f"Click this link to set a new one: {reset_url}\n\n"
            "This link expires in 30 minutes. If you didn't request this, you can ignore this email."
        ),
    )
    mail.send(msg)