import sqlite3

DB_NAME = "app_data.db"

def get_connection():
    """Establish connection and enable row factory for easy column access."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Access columns by name: row["title"]
    return conn

def get_categories():
    """Fetch all main category groupings for the home screen."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, icon_name FROM categories ORDER BY name ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_emergency_topics():
    """Fetch high-priority life-threatening emergency topics for quick access."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, summary FROM topics WHERE is_emergency = 1;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_topics_by_category(category_id):
    """Fetch all first aid topics under a specific category."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, summary, warning_note, is_emergency FROM topics WHERE category_id = ?;",
        (category_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_topic_with_steps(topic_id):
    """Fetch complete details and ordered procedure steps for a selected guide."""
    conn = get_connection()
    cursor = conn.cursor()

    # Get topic header details
    cursor.execute(
        "SELECT id, title, summary, warning_note FROM topics WHERE id = ?;",
        (topic_id,)
    )
    topic_row = cursor.fetchone()

    if not topic_row:
        conn.close()
        return None

    topic_data = dict(topic_row)

    # Get ordered step-by-step instructions
    cursor.execute(
        "SELECT step_number, headline, details, image_path FROM steps WHERE topic_id = ? ORDER BY step_number ASC;",
        (topic_id,)
    )
    step_rows = cursor.fetchall()
    conn.close()

    topic_data["steps"] = [dict(step) for step in step_rows]
    return topic_data

# Quick test call
if __name__ == "__main__":
    print("Categories in DB:")
    for cat in get_categories():
        print(f" - [{cat['id']}] {cat['name']}")

    print("\nEmergency Topics:")
    for emergency in get_emergency_topics():
        print(f" - {emergency['title']}")

    print("\nTesting Full Guide Retrieval (Adult CPR):")
    cpr_guide = get_topic_with_steps(1)
    if cpr_guide:
        print(f"Title: {cpr_guide['title']}")
        print(f"Warning: {cpr_guide['warning_note']}")
        print("Steps:")
        for step in cpr_guide['steps']:
            print(f"  {step['step_number']}. {step['headline']}")