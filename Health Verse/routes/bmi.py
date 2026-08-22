from flask import render_template, request, flash, session
from utils.database import db_get_profile, db_save_bmi
from utils.helpers import validate_bmi_inputs

def bmi_view():
    """Handles BMI calculation, category assignment, and database logging."""
    user_id = session["user_id"]
    
    height = None
    weight = None
    bmi_value = None
    category = None
    
    # Try to pre-populate from profile for GET requests
    user_profile = db_get_profile(user_id)
    if user_profile:
        height = user_profile["height"]
        weight = user_profile["weight"]
        
    if request.method == "POST":
        height_str = request.form.get("height")
        weight_str = request.form.get("weight")
        
        is_valid, err = validate_bmi_inputs(height_str, weight_str)
        if not is_valid:
            flash(err, "error")
        else:
            height = float(height_str)
            weight = float(weight_str)
            
            # Calculate BMI
            height_m = height / 100.0
            bmi_value = weight / (height_m ** 2)
            
            # Determine Category
            if bmi_value < 18.5:
                category = "Underweight"
            elif bmi_value < 25.0:
                category = "Normal"
            elif bmi_value < 30.0:
                category = "Overweight"
            else:
                category = "Obese"
                
            # Log inside database
            db_save_bmi(user_id, height, weight, bmi_value, category)
            flash("BMI calculated and saved successfully!", "success")
            
    return render_template(
        "bmi.html",
        height=height,
        weight=weight,
        bmi_value=bmi_value,
        category=category
    )
