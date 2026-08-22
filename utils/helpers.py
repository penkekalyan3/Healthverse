import re
import io
from functools import wraps
from flask import session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash

def login_required(f):
    """Decorator to restrict route access to authenticated users only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def hash_password(password):
    """Hashes a password using Werkzeug's default method (scrypt)."""
    return generate_password_hash(password)

def verify_password(password, hashed):
    """Verifies a password against its hash."""
    return check_password_hash(hashed, password)

def validate_registration(fullname, email, password, confirm_password):
    """Validates registration inputs. Returns (is_valid, error_message)."""
    if not fullname or not fullname.strip():
        return False, "Full Name is required."
        
    if not email or not email.strip():
        return False, "Email Address is required."
        
    # Email regex check
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, email):
        return False, "Invalid email address format."
        
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
        
    if password != confirm_password:
        return False, "Passwords do not match."
        
    return True, ""

def validate_login(email, password):
    """Validates login inputs. Returns (is_valid, error_message)."""
    if not email or not email.strip():
        return False, "Email Address is required."
    if not password:
        return False, "Password is required."
    return True, ""

def validate_profile(age, gender, height, weight, goal, activity_level):
    """Validates profile inputs. Returns (is_valid, error_message)."""
    try:
        age_val = int(age)
        if age_val <= 0 or age_val > 120:
            return False, "Please enter a valid age between 1 and 120."
    except ValueError:
        return False, "Age must be a positive integer."
        
    if gender not in ["Female", "Male", "Other"]:
        return False, "Invalid gender selection."
        
    try:
        height_val = float(height)
        if height_val <= 30 or height_val > 300:
            return False, "Please enter a valid height between 30 cm and 300 cm."
    except ValueError:
        return False, "Height must be a valid number."
        
    try:
        weight_val = float(weight)
        if weight_val <= 2 or weight_val > 500:
            return False, "Please enter a valid weight between 2 kg and 500 kg."
    except ValueError:
        return False, "Weight must be a valid number."
        
    valid_goals = ["Weight Loss", "Weight Gain", "Maintain Fitness", "Build Muscle"]
    if goal not in valid_goals:
        return False, "Invalid fitness goal selection."
        
    valid_activities = ["Beginner", "Intermediate", "Advanced"]
    if activity_level not in valid_activities:
        return False, "Invalid activity level selection."
        
    return True, ""

def validate_bmi_inputs(height, weight):
    """Validates BMI height and weight inputs."""
    try:
        h = float(height)
        w = float(weight)
        if h <= 30 or h > 300:
            return False, "Height must be between 30 cm and 300 cm."
        if w <= 2 or w > 500:
            return False, "Weight must be between 2 kg and 500 kg."
        return True, ""
    except ValueError:
        return False, "Height and weight must be numeric values."

def validate_progress_inputs(water, exercise, calories, sleep):
    """Validates progress tracker logs."""
    try:
        wat = float(water)
        exe = int(exercise)
        cal = int(calories)
        slp = float(sleep)
        
        if wat < 0 or wat > 20:
            return False, "Water intake should be between 0 and 20 Liters."
        if exe < 0 or exe > 1440:
            return False, "Exercise duration should be between 0 and 1440 minutes."
        if cal < 0 or cal > 20000:
            return False, "Calories burned should be between 0 and 20,000 kcal."
        if slp < 0 or slp > 24:
            return False, "Sleep hours should be between 0 and 24 hours."
            
        return True, ""
    except ValueError:
        return False, "Inputs must be valid numbers (water and sleep can be decimals, exercise and calories must be integers)."

def generate_pdf_report(user, profile, latest_progress, bmi_history):
    """Generates a downloadable PDF wellness report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter, 
        rightMargin=40, 
        leftMargin=40, 
        topMargin=40, 
        bottomMargin=40
    )
    story = []
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        name='TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#00b894'),
        spaceAfter=15
    )
    
    section_style = ParagraphStyle(
        name='SectionStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#2c3e50'),
        spaceBefore=15,
        spaceAfter=8
    )
    
    body_style = ParagraphStyle(
        name='BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#34495e')
    )

    # Title
    story.append(Paragraph("🌿 HealthVerse Wellness Report", title_style))
    story.append(Paragraph(f"Generated for: <b>{user['fullname']}</b> ({user['email']})", body_style))
    story.append(Spacer(1, 15))
    
    # Section 1: User Profile
    story.append(Paragraph("👤 Profile Summary", section_style))
    if profile:
        profile_data = [
            [Paragraph("<b>Age:</b>", body_style), Paragraph(str(profile['age']), body_style),
             Paragraph("<b>Gender:</b>", body_style), Paragraph(str(profile['gender']), body_style)],
            [Paragraph("<b>Height:</b>", body_style), Paragraph(f"{profile['height']} cm", body_style),
             Paragraph("<b>Weight:</b>", body_style), Paragraph(f"{profile['weight']} kg", body_style)],
            [Paragraph("<b>Goal:</b>", body_style), Paragraph(str(profile['goal']), body_style),
             Paragraph("<b>Activity Level:</b>", body_style), Paragraph(str(profile.get('activity_level', 'N/A')), body_style)]
        ]
    else:
        profile_data = [[Paragraph("No profile details recorded.", body_style)]]
        
    t_profile = Table(profile_data, colWidths=[100, 150, 100, 150])
    t_profile.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_profile)
    story.append(Spacer(1, 15))
    
    # Section 2: Latest Logged Progress
    story.append(Paragraph("📈 Latest Daily Progress", section_style))
    if latest_progress:
        progress_data = [
            [Paragraph("<b>Water Intake:</b>", body_style), Paragraph(f"{latest_progress['water']} L", body_style)],
            [Paragraph("<b>Exercise Minutes:</b>", body_style), Paragraph(f"{latest_progress['exercise']} Min", body_style)],
            [Paragraph("<b>Calories Burned:</b>", body_style), Paragraph(f"{latest_progress['calories']} kcal", body_style)],
            [Paragraph("<b>Sleep Hours:</b>", body_style), Paragraph(f"{latest_progress['sleep']} Hours", body_style)],
            [Paragraph("<b>Logged Date:</b>", body_style), Paragraph(str(latest_progress['date']), body_style)]
        ]
    else:
        progress_data = [[Paragraph("No progress history logged yet.", body_style)]]
        
    t_progress = Table(progress_data, colWidths=[150, 350])
    t_progress.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_progress)
    story.append(Spacer(1, 15))
    
    # Section 3: BMI History
    story.append(Paragraph("❤️ BMI History", section_style))
    if bmi_history:
        bmi_table_data = [
            [Paragraph("<b>Date</b>", body_style), 
             Paragraph("<b>Height</b>", body_style), 
             Paragraph("<b>Weight</b>", body_style), 
             Paragraph("<b>BMI</b>", body_style), 
             Paragraph("<b>Category</b>", body_style)]
        ]
        for item in bmi_history:
            bmi_table_data.append([
                Paragraph(str(item['date'])[:16], body_style),
                Paragraph(f"{item['height']} cm", body_style),
                Paragraph(f"{item['weight']} kg", body_style),
                Paragraph(f"{item['bmi']:.2f}", body_style),
                Paragraph(str(item['category']), body_style)
            ])
            
        t_bmi = Table(bmi_table_data, colWidths=[130, 80, 80, 80, 130])
        t_bmi.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f2f2f2')),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ]))
        story.append(t_bmi)
    else:
        story.append(Paragraph("No BMI history logged yet.", body_style))
        
    doc.build(story)
    buffer.seek(0)
    return buffer
