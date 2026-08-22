from flask import render_template, request, session, jsonify
from utils.database import db_get_profile
from utils.ai_helper import get_ai_response

def ai_view():
    """Handles health coach queries and AI responses using user profile context."""
    user_id = session["user_id"]
    
    question = None
    response = None
    
    if request.method == "POST":
        if request.is_json:
            data = request.get_json() or {}
            question = data.get("question")
        else:
            question = request.form.get("question")
            
        if not question:
            if request.is_json:
                return jsonify({"success": False, "message": "No question provided"}), 400
            return render_template("ai.html", question=None, response=None)
            
        # Retrieve user profile context to personalize the AI response
        user_profile = db_get_profile(user_id)
        profile_dict = dict(user_profile) if user_profile else None
        
        # Query Gemini API
        response = get_ai_response(question, profile_dict)
        
        if request.is_json:
            return jsonify({"success": True, "response": response})
        
    return render_template("ai.html", question=question, response=response)

