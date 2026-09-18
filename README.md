# Student Task Manager

A student task management web app — organize tasks by course, track deadlines, and get email reminders. Built with Flask, SQLAlchemy, and PostgreSQL, styled with a glassmorphic, mobile-first theme.

## Setup (Windows / VS Code)

1. **Open the project folder from the top level** — always `cd student-task-manager` before running any command, so you don't hit the nested-folder issue.

2. **Create a virtual environment:**
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL:**
   - Install PostgreSQL if you haven't already, and create a database:
     ```
     createdb student_task_manager_dev
     ```

5. **Configure environment variables:**
   - Copy `.env.example` to `.env`
   - Fill in `SECRET_KEY` (any random string), your `DATABASE_URL`, and mail credentials (a Gmail "app password", not your normal password, if using Gmail)

6. **Initialize the database:**
   ```
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

7. **Run the app:**
   ```
   python run.py
   ```
   Visit `http://localhost:5000` — you'll land on the login page, since no account exists yet. Sign up to create one.

## Project Structure

See `docs/design.md` for the full architecture, ER diagram, and route list.

## What's implemented so far (v1 core)
- Signup / login / logout
- Course CRUD
- Task CRUD with course linkage, priority, category, due date
- Dashboard (today / overdue / this week)
- Task filtering by course and status, sorting by due date or priority
- Responsive glass theme: sidebar nav on desktop, bottom nav + FAB on mobile

## Not yet implemented
- Email reminder sending (the `email_service.py` function exists but isn't wired to a scheduler yet — you'll want something like `APScheduler` or a cron job to check for upcoming due dates and call it)
- Password reset flow
