from flask import render_template, request, session
from utils.database import db_get_profile
from utils.ai_helper import get_ai_response

def ai_view():
    """Handles health coach queries and AI responses using user profile context."""
    user_id = session["user_id"]
    
    question = None
    response = None
    
    if request.method == "POST":
        question = request.form.get("question")
        
        # Retrieve user profile context to personalize the AI response
        user_profile = db_get_profile(user_id)
        
        # Convert sqlite3.Row to dict
        profile_dict = dict(user_profile) if user_profile else None
        
        # Query Gemini API
        response = get_ai_response(question, profile_dict)
        
    return render_template("ai.html", question=question, response=response)
