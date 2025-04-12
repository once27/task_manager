# 🧩 Task Manager API (WIP)

A **Task & Project Management System** built using **Django** and **Django REST Framework** with an **API-first approach** — designed for modern teams to collaborate, track, and manage work efficiently.

> ⚠️ This project is in active development and currently focuses on backend API functionality. Frontend will follow soon.

---

## 🚀 Tech Stack

- **Backend**: Django, Django REST Framework
- **Database**: SQLite (development), switchable to MySQL/PostgreSQL
- **Auth**: Token-based authentication with role-based access control
- **DevOps**: Docker & Docker Compose for containerized development
- **Frontend** (Planned): Django templates + JavaScript

---

## 🎯 Features (Planned & In Progress)

- ✅ Secure user authentication (Token-based)
- ✅ Role-based access control (e.g., Admin, Manager, Developer)
- ✅ API endpoints for task and project management
- 🚧 Dashboards for task overview, deadlines, and project status
- 🚧 Task creation, assignment, prioritization
- 🚧 Real-time collaboration: task comments, mentions, notifications
- ✅ Dockerized development environment
- 🛠️ CI/CD (planned via GitHub Actions)

---

## 🐳 Getting Started (With Docker)

```bash
# Clone the repo
git clone https://github.com/once27/task_manager.git
cd task_manager

# Build and run using Docker Compose
docker-compose up --build

The backend will be available at http://localhost:8000/


# For Development Setup Without Docker
# Create and activate a virtual environment
python -m venv env
source env/bin/activate  # or env\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run migrations and start server
python manage.py migrate
python manage.py runserver


✨ Future Plans

Add unit tests and coverage

Setup CI/CD pipelines with GitHub Actions

Implement notifications via WebSockets or polling

Add a rich frontend using Django templates + JavaScript (or React in future)

Deploy on cloud (Render, Railway, or AWS)


🧠 Learning Goals

This project is part of my learning journey to:

Master Django REST Framework and backend API development

Practice clean code and software architecture

Learn containerization and DevOps using Docker

Get hands-on with CI/CD pipelines and production-ready workflows

