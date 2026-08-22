from flask import render_template, request, redirect, url_for, flash, session, send_file
from utils.database import (
    db_get_user_by_id, 
    db_get_profile, 
    db_save_profile, 
    db_update_fullname,
    db_get_latest_progress,
    db_get_latest_bmi,
    db_get_bmi_history
)
from utils.helpers import login_required, validate_profile, generate_pdf_report

def dashboard_view():
    """Displays the user's dashboard."""
    fullname = session.get("fullname", "User")
    return render_template("dashboard.html", fullname=fullname)

def profile_view():
    """Handles viewing and updating user profile information."""
    user_id = session["user_id"]
    
    if request.method == "POST":
        fullname = request.form.get("fullname")
        age = request.form.get("age")
        gender = request.form.get("gender")
        height = request.form.get("height")
        weight = request.form.get("weight")
        goal = request.form.get("goal")
        activity_level = request.form.get("activity_level")
        
        # Validate profile inputs
        is_valid, err = validate_profile(age, gender, height, weight, goal, activity_level)
        if not is_valid:
            flash(err, "error")
        else:
            # Update user's name
            db_update_fullname(user_id, fullname)
            session["fullname"] = fullname # update session display name
            
            # Save/update profile table
            db_save_profile(
                user_id, 
                int(age), 
                gender, 
                float(height), 
                float(weight), 
                goal, 
                activity_level
            )
            flash("Profile updated successfully!", "success")
            
    # Fetch latest data to render
    user = db_get_user_by_id(user_id)
    user_profile = db_get_profile(user_id)
    
    return render_template("profile.html", user=user, profile=user_profile)

def reports_view():
    """Fetches user health statistics and displays reports dashboard."""
    user_id = session["user_id"]
    
    user = db_get_user_by_id(user_id)
    user_profile = db_get_profile(user_id)
    latest_progress = db_get_latest_progress(user_id)
    latest_bmi = db_get_latest_bmi(user_id)
    bmi_history = db_get_bmi_history(user_id)
    
    return render_template(
        "reports.html",
        profile=user_profile,
        latest_progress=latest_progress,
        latest_bmi=latest_bmi,
        bmi_history=bmi_history
    )

def download_report_view():
    """Generates and downloads the PDF health report."""
    user_id = session["user_id"]
    
    user = db_get_user_by_id(user_id)
    user_profile = db_get_profile(user_id)
    latest_progress = db_get_latest_progress(user_id)
    bmi_history = db_get_bmi_history(user_id)
    
    # Generate PDF buffer
    pdf_buffer = generate_pdf_report(user, user_profile, latest_progress, bmi_history)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"HealthVerse_Report_{user['fullname'].replace(' ', '_')}.pdf",
        mimetype="application/pdf"
    )
