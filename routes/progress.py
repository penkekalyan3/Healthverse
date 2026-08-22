from flask import render_template, request, flash, session
from utils.database import db_get_profile, db_get_latest_progress, db_save_progress, db_get_latest_bmi
from utils.helpers import validate_progress_inputs

def progress_view():
    """Handles logging daily progress and displaying latest statistics."""
    user_id = session["user_id"]
    
    if request.method == "POST":
        water = request.form.get("water")
        exercise = request.form.get("exercise")
        calories = request.form.get("calories")
        sleep = request.form.get("sleep")
        
        is_valid, err = validate_progress_inputs(water, exercise, calories, sleep)
        if not is_valid:
            flash(err, "error")
        else:
            db_save_progress(
                user_id, 
                float(water), 
                int(calories), 
                int(exercise), 
                float(sleep)
            )
            flash("Today's progress logged successfully!", "success")
            
    # Fetch data to display
    user_profile = db_get_profile(user_id)
    latest_progress = db_get_latest_progress(user_id)
    latest_bmi = db_get_latest_bmi(user_id)
    
    return render_template(
        "progress.html",
        profile=user_profile,
        progress=latest_progress,
        latest_bmi=latest_bmi
    )
