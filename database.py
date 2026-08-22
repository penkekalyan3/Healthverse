import sqlite3
import os

def initialize_database():
    """Initializes the database manually from the schema file."""
    db_dir = "database"
    db_file = os.path.join(db_dir, "database.db")
    schema_file = os.path.join(db_dir, "schema.sql")
    
    # Ensure the database directory exists
    os.makedirs(db_dir, exist_ok=True)
    
    print(f"Connecting to database at: {db_file}...")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    if not os.path.exists(schema_file):
        print(f"❌ Error: Schema file not found at {schema_file}")
        return
        
    print(f"Executing schema from: {schema_file}...")
    with open(schema_file, "r") as f:
        cursor.executescript(f.read())
        
    conn.commit()
    conn.close()
    print("✅ HealthVerse Database Created Successfully!")

if __name__ == "__main__":
    initialize_database()