from flask import Flask, render_template, session
from config import Config
from utils.database import init_db, close_connection
from utils.helpers import login_required

app = Flask(__name__)
app.config.from_object(Config)

# Register database close handler at the end of each request
app.teardown_appcontext(close_connection)

# Auto-initialize SQLite database on startup
with app.app_context():
    init_db()

# Home Page (public)
@app.route("/")
def home():
    return render_template("index.html")

# Import view functions from modular route files
from routes.auth import register_view, login_view, logout_view
from routes.dashboard import dashboard_view, profile_view, reports_view, download_report_view
from routes.bmi import bmi_view
from routes.progress import progress_view
from routes.yoga import yoga_view
from routes.ai import ai_view

# Authentication Routes (public)
@app.route("/register", methods=["GET", "POST"])
def register():
    return register_view()

@app.route("/login", methods=["GET", "POST"])
def login():
    return login_view()

@app.route("/logout")
def logout():
    return logout_view()

# Protected Dashboard & Profile Routes (login required)
@app.route("/dashboard")
@login_required
def dashboard():
    return dashboard_view()

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    return profile_view()

# Protected Health Reports & Download Routes (login required)
@app.route("/reports")
@login_required
def reports():
    return reports_view()

@app.route("/reports/download")
@login_required
def download_report():
    return download_report_view()

# Protected Fitness & Calculator Tools (login required)
@app.route("/bmi", methods=["GET", "POST"])
@login_required
def bmi():
    return bmi_view()

@app.route("/progress", methods=["GET", "POST"])
@login_required
def progress():
    return progress_view()

@app.route("/yoga")
@login_required
def yoga():
    return yoga_view()



@app.route("/api/yoga/log", methods=["POST"])
@login_required
def log_yoga():
    from routes.yoga import log_yoga_session
    return log_yoga_session()


# Protected AI Health Coach Route (login required)
@app.route("/ai", methods=["GET", "POST"])
@login_required
def ai():
    return ai_view()

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)