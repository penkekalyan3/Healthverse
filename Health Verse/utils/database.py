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
