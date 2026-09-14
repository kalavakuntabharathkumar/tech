from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("techdesk.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,
    assignee TEXT,
    description TEXT,
    resolution TEXT
);
CREATE TABLE IF NOT EXISTS knowledge_base (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue TEXT NOT NULL,
    resolution TEXT NOT NULL
);
"""

def get_db():
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()
    db.close()

def classify(title, description=""):
    text = f"{title} {description}".lower()
    categories = {
        "Network": ["wifi", "network", "vpn", "dns", "internet"],
        "Hardware": ["laptop", "keyboard", "mouse", "monitor", "printer"],
        "Access": ["password", "login", "account", "permission", "access"],
        "Software": ["crash", "install", "application", "software", "error"],
    }
    category = next((c for c, words in categories.items() if any(w in text for w in words)), "General")
    priority = "High" if any(w in text for w in ["down", "blocked", "urgent", "outage", "security"]) else "Medium"
    return category, priority

@app.route("/", methods=["GET"])
def dashboard():
    db = get_db()
    q = request.args.get("q", "").strip()
    category = request.args.get("category", "")
    status = request.args.get("status", "")
    sql = "SELECT * FROM tickets WHERE 1=1"
    params = []
    if q:
        sql += " AND (title LIKE ? OR description LIKE ? OR assignee LIKE ?)"
        params += [f"%{q}%"] * 3
    if category:
        sql += " AND category = ?"; params.append(category)
    if status:
        sql += " AND status = ?"; params.append(status)
    tickets = db.execute(sql + " ORDER BY id DESC", params).fetchall()
    stats = {
        "total": db.execute("SELECT COUNT(*) FROM tickets").fetchone()[0],
        "open": db.execute("SELECT COUNT(*) FROM tickets WHERE status='Open'").fetchone()[0],
        "high": db.execute("SELECT COUNT(*) FROM tickets WHERE priority='High' AND status!='Resolved'").fetchone()[0],
        "kb": db.execute("SELECT COUNT(*) FROM knowledge_base").fetchone()[0],
    }
    db.close()
    return render_template("dashboard.html", tickets=tickets, stats=stats, q=q, category=category, status=status)

@app.route("/tickets/new", methods=["GET", "POST"])
def new_ticket():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form.get("description", "")
        category, priority = classify(title, description)
        db = get_db()
        db.execute("INSERT INTO tickets(title,category,priority,status,assignee,description) VALUES(?,?,?,?,?,?)", (title, category, priority, "Open", request.form.get("assignee", ""), description))
        db.commit(); db.close()
        return redirect(url_for("dashboard"))
    return render_template("ticket_form.html")

@app.route("/tickets/<int:ticket_id>/status", methods=["POST"])
def update_status(ticket_id):
    db = get_db()
    db.execute("UPDATE tickets SET status=? WHERE id=?", (request.form["status"], ticket_id))
    db.commit(); db.close()
    return redirect(request.referrer or url_for("dashboard"))

@app.route("/knowledge")
def knowledge():
    db = get_db(); entries = db.execute("SELECT * FROM knowledge_base ORDER BY issue").fetchall(); db.close()
    return render_template("knowledge.html", entries=entries)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
