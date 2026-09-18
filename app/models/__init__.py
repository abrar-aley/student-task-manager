from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
import os

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
mail = Mail()


def create_app(config_class="app.config.DevConfig"):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    login_manager.login_view = "auth.login"

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.courses import courses_bp
    from app.routes.tasks import tasks_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(tasks_bp)

    _start_scheduler(app)

    return app


def _start_scheduler(app):
    """Starts the background job that emails deadline reminders.
    Guarded so Flask's debug-mode auto-reloader (which runs two processes)
    doesn't start two competing schedulers."""
    if app.config.get("TESTING"):
        return
    if app.debug and os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        return

    from apscheduler.schedulers.background import BackgroundScheduler
    from app.services.reminder_scheduler import check_and_send_reminders

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        func=lambda: check_and_send_reminders(app),
        trigger="interval",
        hours=1,
        id="deadline_reminders",
        replace_existing=True,
    )
    scheduler.start()