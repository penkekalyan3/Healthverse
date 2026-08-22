from flask import render_template, request, jsonify, session
from utils.database import (
    db_save_progress,
    db_save_yoga_session,
    db_get_yoga_sessions,
    db_award_badge_if_new,
    db_get_streak_days,
    db_get_user_badges
)

def yoga_view():
    """Renders the Yoga routine planner."""
    return render_template("yoga.html")

def log_yoga_session():
    """Logs the yoga workout to progress history and yoga_sessions, and awards badges (SQLite)."""
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"success": False, "message": "Unauthorized"}), 401
    
    data = request.get_json() or {}
    duration_seconds = data.get("duration", 0)
    calories = data.get("calories", 0)
    completed_poses = data.get("completed_poses", 0)
    start_time = data.get("start_time", "")
    end_time = data.get("end_time", "")
    status = data.get("status", "Completed")
    avg_bpm = data.get("avg_bpm")
    max_bpm = data.get("max_bpm")
    
    if avg_bpm is not None:
        try:
            avg_bpm = int(avg_bpm)
        except (ValueError, TypeError):
            avg_bpm = None
    if max_bpm is not None:
        try:
            max_bpm = int(max_bpm)
        except (ValueError, TypeError):
            max_bpm = None
    
    from datetime import datetime
    session_date = data.get("session_date", datetime.now().strftime("%Y-%m-%d"))
    
    if not start_time:
        start_time = datetime.now().strftime("%I:%M %p")
    if not end_time:
        end_time = datetime.now().strftime("%I:%M %p")
        
    # Convert seconds to minutes (round to nearest integer, minimum 1 if session completed)
    exercise_minutes = max(1, round(duration_seconds / 60.0)) if duration_seconds > 0 else 0
    
    try:
        # 1. Log to overall progress
        db_save_progress(user_id, 0.0, int(calories), int(exercise_minutes), 0.0)
        
        # 2. Log to yoga sessions table
        db_save_yoga_session(
            user_id, 
            session_date, 
            start_time, 
            end_time, 
            int(duration_seconds), 
            int(calories), 
            int(completed_poses), 
            status,
            avg_bpm=avg_bpm,
            max_bpm=max_bpm
        )
        
        # 3. Award badges automatically
        new_badges = []
        
        if status == "Completed":
            # Count total completed sessions
            all_sessions = db_get_yoga_sessions(user_id)
            completed_sessions = [s for s in all_sessions if s['status'] == "Completed"]
            
            # Badge 1: First Session
            if len(completed_sessions) >= 1:
                if db_award_badge_if_new(user_id, "First Session"):
                    new_badges.append("First Session")
            
            # Badge 2: Yoga Master (10 Completed Sessions)
            if len(completed_sessions) >= 10:
                if db_award_badge_if_new(user_id, "Yoga Master"):
                    new_badges.append("Yoga Master")
            
            # Badge 3: Streaks
            streak_days = db_get_streak_days(user_id)
            if streak_days >= 7:
                if db_award_badge_if_new(user_id, "7 Day Streak"):
                    new_badges.append("7 Day Streak")
            if streak_days >= 30:
                if db_award_badge_if_new(user_id, "30 Day Streak"):
                    new_badges.append("30 Day Streak")
                    
        # Get all user badges to return
        all_user_badges = [dict(b) for b in db_get_user_badges(user_id)]
        
        return jsonify({
            "success": True, 
            "message": "Workout logged successfully!",
            "new_badges": new_badges,
            "all_badges": all_user_badges
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "message": str(e)}), 500





