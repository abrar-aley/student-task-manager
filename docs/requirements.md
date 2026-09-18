# Student Task Manager — Requirements Document (v1)

## 1. Overview
A web-based task management system for university students. Each student has a private account to organize coursework by subject, track deadlines, and receive email reminders before due dates. Built as a portfolio project and intended for real use by the author and university peers.

## 2. Users
- **Primary user**: Individual student
- **Access model**: Multi-user, single-tenant-per-account (each user's data is private; no sharing/collaboration in v1)

## 3. Core Entities
- **User**: account holder
- **Course**: a subject/class the user is enrolled in
- **Task**: a to-do item linked to a Course

## 4. Functional Requirements

### 4.1 Authentication
- FR-1: User can sign up with email/username and password
- FR-2: User can log in and log out
- FR-3: User can reset a forgotten password

### 4.2 Course Management
- FR-4: User can add a Course (name, optional code, optional instructor)
- FR-5: User can edit or delete a Course
- FR-6: Deleting a Course prompts confirmation if Tasks are linked to it

### 4.3 Task Management
- FR-7: User can create a Task with: title, description, linked Course, due date, priority (Low/Medium/High), category (Assignment/Exam/Project/Reading)
- FR-8: User can edit or delete a Task
- FR-9: User can mark a Task complete/incomplete
- FR-10: User can filter tasks by Course, status, or due date
- FR-11: User can sort tasks by nearest deadline

### 4.4 Dashboard
- FR-12: Dashboard shows: tasks due today, overdue tasks, tasks due in the next 7 days

### 4.5 Notifications
- FR-13: System sends an email reminder before a Task's due date (configurable lead time, default 24h)

## 5. Non-Functional Requirements
- NFR-1 (Security): Passwords stored using a secure hash (e.g. bcrypt); one user's data is never visible to another
- NFR-2 (Usability): Adding a task takes under 10 seconds from dashboard
- NFR-3 (Performance): Task list loads in under 1 second for a few hundred tasks
- NFR-4 (Scalability): System supports 50–100 concurrent users without architectural changes
- NFR-5 (Portability): Responsive design — usable on both desktop and mobile browsers
- NFR-6 (Availability): Reliable enough for daily use (no formal uptime SLA required for v1)

## 6. Out of Scope for v1 (Future/Stretch)
- Recurring tasks
- Web push notifications
- Calendar view
- Progress tracking / study streaks
- Export to PDF/CSV
- Collaboration/shared tasks

## 7. Assumptions & Constraints
- Solo developer project — scope is intentionally limited for a realistic v1
- Tech stack to be finalized in the System Design phase
