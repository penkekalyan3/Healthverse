from flask import render_template, request, redirect, url_for, flash, session
from utils.database import db_create_user, db_get_user_by_email
from utils.helpers import hash_password, verify_password, validate_registration, validate_login

def register_view():
    """Handles new user registration view."""
    if "user_id" in session:
        return redirect(url_for('dashboard'))
        
    if request.method == "POST":
        fullname = request.form.get("fullname")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        
        # Validation
        is_valid, err = validate_registration(fullname, email, password, confirm_password)
        if not is_valid:
            flash(err, "error")
            return render_template("register.html")
            
        hashed = hash_password(password)
        success = db_create_user(fullname, email, hashed)
        if success:
            flash("Registration successful! Please login below.", "success")
            return redirect(url_for('login'))
        else:
            flash("An account with this email already exists.", "error")
            return render_template("register.html")
            
    return render_template("register.html")

def login_view():
    """Handles user login view."""
    if "user_id" in session:
        return redirect(url_for('dashboard'))
        
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        is_valid, err = validate_login(email, password)
        if not is_valid:
            flash(err, "error")
            return render_template("login.html")
            
        user = db_get_user_by_email(email)
        if user and verify_password(password, user["password"]):
            session["user_id"] = user["id"]
            session["fullname"] = user["fullname"]
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email address or password.", "error")
            return render_template("login.html")
            
    return render_template("login.html")

def logout_view():
    """Clears user session and redirects to login."""
    session.clear()
    flash("You have been successfully logged out.", "success")
    return redirect(url_for('login'))
