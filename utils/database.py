import sqlite3
import os
from flask import g
from config import Config

def get_db_connection():
    """Returns a thread-safe connection to the SQLite database attached to Flask application context g."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(Config.DATABASE)
        db.row_factory = sqlite3.Row
    return db

def close_connection(exception=None):
    """Closes database connection at end of request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database using schema.sql if tables do not exist."""
    db_path = Config.DATABASE
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "database", "schema.sql")
    
    with open(schema_path, "r") as f:
        conn.executescript(f.read())
        
    # Check if avg_bpm and max_bpm columns exist in yoga_sessions table, add them if missing
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(yoga_sessions)")
        columns = [col[1] for col in cursor.fetchall()]
        if "avg_bpm" not in columns:
            cursor.execute("ALTER TABLE yoga_sessions ADD COLUMN avg_bpm INTEGER")
        if "max_bpm" not in columns:
            cursor.execute("ALTER TABLE yoga_sessions ADD COLUMN max_bpm INTEGER")
    except Exception as e:
        print(f"Error migrating yoga_sessions table: {e}")
        
    conn.commit()
    conn.close()
    print("HealthVerse Database Initialized Successfully!")

def db_create_user(fullname, email, password_hash):
    """Saves a new user to the users table. Returns True on success, False if email already exists."""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO users (fullname, email, password) VALUES (?, ?, ?)",
            (fullname, email, password_hash)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def db_get_user_by_email(email):
    """Retrieves user by email."""
    conn = get_db_connection()
    return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

def db_get_user_by_id(user_id):
    """Retrieves user by id."""
    conn = get_db_connection()
    return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()

def db_get_profile(user_id):
    """Retrieves user profile details."""
    conn = get_db_connection()
    return conn.execute("SELECT * FROM profile WHERE user_id = ?", (user_id,)).fetchone()

def db_save_profile(user_id, age, gender, height, weight, goal, activity_level):
    """Saves or updates profile details for a user."""
    conn = get_db_connection()
    existing = db_get_profile(user_id)
    if existing:
        conn.execute(
            "UPDATE profile SET age = ?, gender = ?, height = ?, weight = ?, goal = ?, activity_level = ? WHERE user_id = ?",
            (age, gender, height, weight, goal, activity_level, user_id)
        )
    else:
        conn.execute(
            "INSERT INTO profile (user_id, age, gender, height, weight, goal, activity_level) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, age, gender, height, weight, goal, activity_level)
        )
    conn.commit()

def db_save_bmi(user_id, height, weight, bmi_value, category):
    """Logs BMI calculation details in history."""
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO bmi (user_id, height, weight, bmi, category) VALUES (?, ?, ?, ?, ?)",
        (user_id, height, weight, bmi_value, category)
    )
    conn.commit()

def db_get_bmi_history(user_id):
    """Gets list of all logged BMI values for a user."""
    conn = get_db_connection()
    return conn.execute("SELECT * FROM bmi WHERE user_id = ? ORDER BY date DESC, id DESC", (user_id,)).fetchall()

def db_get_latest_bmi(user_id):
    """Gets the latest BMI log."""
    conn = get_db_connection()
    return conn.execute("SELECT * FROM bmi WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT 1", (user_id,)).fetchone()

def db_save_progress(user_id, water, calories, exercise, sleep):
    """Logs daily progress inputs."""
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO progress (user_id, water, calories, exercise, sleep) VALUES (?, ?, ?, ?, ?)",
        (user_id, water, calories, exercise, sleep)
    )
    conn.commit()

def db_get_latest_progress(user_id):
    """Gets the latest progress logs."""
    conn = get_db_connection()
    return conn.execute("SELECT * FROM progress WHERE user_id = ? ORDER BY date DESC, id DESC LIMIT 1", (user_id,)).fetchone()

def db_update_fullname(user_id, fullname):
    """Updates the user's full name in the users table."""
    conn = get_db_connection()
    conn.execute("UPDATE users SET fullname = ? WHERE id = ?", (fullname, user_id))
    conn.commit()

def db_save_yoga_session(user_id, session_date, start_time, end_time, duration, calories, completed_poses, status, avg_bpm=None, max_bpm=None):
    """Saves a completed or incomplete yoga session in SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO yoga_sessions (user_id, session_date, start_time, end_time, duration, calories, completed_poses, status, avg_bpm, max_bpm)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (user_id, session_date, start_time, end_time, duration, calories, completed_poses, status, avg_bpm, max_bpm)
    )
    conn.commit()
    return cursor.lastrowid

def db_get_yoga_sessions(user_id):
    """Retrieves all yoga session logs for a user."""
    conn = get_db_connection()
    return conn.execute("SELECT * FROM yoga_sessions WHERE user_id = ? ORDER BY session_date DESC, id DESC", (user_id,)).fetchall()

def db_get_user_badges(user_id):
    """Retrieves all badges earned by the user."""
    conn = get_db_connection()
    return conn.execute("SELECT * FROM user_badges WHERE user_id = ? ORDER BY awarded_date DESC", (user_id,)).fetchall()

def db_award_badge_if_new(user_id, badge_name):
    """Awards a badge if it has not already been awarded. Returns True if awarded, False if already exists."""
    conn = get_db_connection()
    try:
        conn.execute(
            "INSERT INTO user_badges (user_id, badge_name) VALUES (?, ?)",
            (user_id, badge_name)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def db_get_streak_days(user_id):
    """Computes the user's consecutive active days of completed sessions up to today."""
    conn = get_db_connection()
    rows = conn.execute(
        "SELECT DISTINCT session_date FROM yoga_sessions WHERE user_id = ? AND status = 'Completed' ORDER BY session_date DESC",
        (user_id,)
    ).fetchall()
    
    if not rows:
        return 0
        
    from datetime import datetime, timedelta
    
    # Extract unique dates
    dates = []
    for r in rows:
        try:
            date_str = r['session_date'].split()[0]
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
            if d not in dates:
                dates.append(d)
        except Exception:
            continue
            
    if not dates:
        return 0
        
    # Check if latest date is today or yesterday to continue streak
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    if dates[0] != today and dates[0] != yesterday:
        return 0
        
    streak = 1
    current_date = dates[0]
    
    for next_date in dates[1:]:
        if current_date - next_date == timedelta(days=1):
            streak += 1
            current_date = next_date
        elif current_date - next_date == timedelta(days=0):
            continue
        else:
            break
            
    return streak

