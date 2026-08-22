import os
from dotenv import load_dotenv

# Load environment variables from a .env file if it exists
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "healthverse-secret-key-123456")
    # Store database file in the database/ subdirectory of the project
    DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), "database", "database.db")
    GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
