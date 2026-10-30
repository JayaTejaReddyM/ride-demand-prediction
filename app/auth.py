from functools import wraps
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash, abort)
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)

# Demo user database (passwords are stored hashed, not as plain text)
USERS = {
    "admin":   {"password": generate_password_hash("admin123"),   "role": "admin"},
    "planner": {"password": generate_password_hash("planner123"), "role": "planner"},
    "driver":  {"password": generate_password_hash("driver123"),  "role": "driver"},
}

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return wrapper

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if "user" not in session:
                return redirect(url_for("auth.login"))
            if session.get("role") not in roles:
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return wrapper
    return decorator

@auth_bp.route("/")
def index():
    return redirect(url_for("auth.dashboard"))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]
        user = USERS.get(username)
        if user and check_password_hash(user["password"], password):
            session["user"] = username
            session["role"] = user["role"]
            return redirect(url_for("auth.dashboard"))
        flash("Invalid username or password")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

@auth_bp.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html",
                           user=session["user"], role=session["role"])

@auth_bp.route("/admin")
@role_required("admin")
def admin_page():
    return "<h2>Admin only page</h2><a href='/dashboard'>Back</a>"