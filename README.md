# TechDesk — IT Asset & Issue Tracking Tool

A Flask + SQLite support-operations application for logging, searching, categorizing, and resolving IT issues.

## Features
- Ticket creation with deterministic category and priority classification.
- Search and filter tickets by issue text, category, and status.
- Status workflow: Open → In Progress → Resolved.
- SQLite persistence with a troubleshooting knowledge-base view.
- Lightweight server-rendered UI suitable for local support teams.

## Run
```bash
python -m venv .venv
.venv\\Scripts\\activate  # Windows
pip install -r requirements.txt
python app.py
```
Open `http://127.0.0.1:5000`.

## Structure
- `app.py` — Flask routes, SQLite schema, classification logic
- `templates/` — dashboard, ticket form, knowledge base
- `static/style.css` — interface styling
