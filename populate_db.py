import sqlite3

def populate_database():
    conn = sqlite3.connect("app_data.db")
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Clear existing data so you can re-run this script anytime without duplicates
    cursor.execute("DELETE FROM steps;")
    cursor.execute("DELETE FROM topics;")
    cursor.execute("DELETE FROM categories;")

    # 1. Insert Main Categories
    categories = [
        (1, "Cardiac & Respiration", "heart_pulse"),
        (2, "Trauma & Wounds", "bandage"),
        (3, "Environmental & Burns", "flame")
    ]
    cursor.executemany(
        "INSERT INTO categories (id, name, icon_name) VALUES (?, ?, ?);", 
        categories
    )

    # 2. Insert First Aid Topics
    topics = [
        (
            1, 1, "Adult CPR", 
            "Cardiopulmonary Resuscitation for unresponsive adults who are not breathing normally.", 
            "DO NOT delay CPR to check for pulse if the person is unresponsive and not breathing normally.", 
            1  # Emergency high-priority
        ),
        (
            2, 1, "Choking (Adult/Child)", 
            "First aid for a conscious person unable to speak, cough, or breathe due to airway obstruction.", 
            "DO NOT perform abdominal thrusts on infants under 1 year old.", 
            1
        ),
        (
            3, 2, "Severe Bleeding", 
            "Emergency procedures to control rapid blood loss from major cuts or wounds.", 
            "DO NOT remove embedded objects from wounds; stabilize them in place.", 
            1
        ),
        (
            4, 3, "Thermal Burns", 
            "First-aid care for heat, steam, or fire burns.", 
            "NEVER apply ice, butter, grease, or adhesive bandages directly to a burn.", 
            0
        )
    ]
    cursor.executemany("""
        INSERT INTO topics (id, category_id, title, summary, warning_note, is_emergency) 
        VALUES (?, ?, ?, ?, ?, ?);
    """, topics)

    # 3. Insert Ordered Steps
    steps = [
        # Adult CPR Steps (topic_id = 1)
        (1, 1, "Check Safety & Responsiveness", "Ensure the area is safe. Tap the shoulder and loudly ask, 'Are you okay?'", "images/cpr_check.png"),
        (1, 2, "Call Emergency Services", "Assign a bystander to call local emergency services and get an AED if available.", None),
        (1, 3, "Give Chest Compressions", "Place hands in center of chest. Push hard and fast (100–120 bpm) at least 2 inches deep.", "images/cpr_compressions.png"),
        (1, 4, "Provide Rescue Breaths", "Give 2 rescue breaths after every 30 compressions if trained, or continue continuous chest compressions.", None),

        # Choking Steps (topic_id = 2)
        (2, 1, "Encourage Coughing", "If the person can talk or cough forcefully, encourage them to keep coughing.", None),
        (2, 2, "Give 5 Back Blows", "Lean the person forward and strike firmly between shoulder blades with the heel of your hand.", None),
        (2, 3, "Give 5 Abdominal Thrusts", "Stand behind them, place a fist above their navel, and pull inward and upward sharply.", None),

        # Severe Bleeding Steps (topic_id = 3)
        (3, 1, "Apply Direct Pressure", "Press a clean cloth or bandage directly onto the wound with firm force.", None),
        (3, 2, "Elevate the Injured Area", "Raise the wound above heart level if possible while continuing firm pressure.", None),
        (3, 3, "Apply Pressure Bandage", "Wrap bandage tightly over the dressing. If blood soaks through, add another pad on top without removing the first.", None),

        # Thermal Burn Steps (topic_id = 4)
        (4, 1, "Cool the Burn", "Hold the burn under cool running water for at least 10 to 20 minutes.", None),
        (4, 2, "Cover Loosely", "Cover with clean, non-stick sterile plastic wrap or cloth without putting pressure on the burn.", None),
        (4, 3, "Manage Pain", "Keep the person calm, elevate the burned area if on an arm or leg, and seek medical aid.", None)
    ]
    cursor.executemany("""
        INSERT INTO steps (topic_id, step_number, headline, details, image_path) 
        VALUES (?, ?, ?, ?, ?);
    """, steps)

    conn.commit()

    # Verification counts
    cursor.execute("SELECT COUNT(*) FROM categories;")
    cat_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM topics;")
    top_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM steps;")
    step_count = cursor.fetchone()[0]

    conn.close()
    print(f"SUCCESS: Inserted {cat_count} categories, {top_count} topics, and {step_count} steps into app_data.db!")

if __name__ == "__main__":
    populate_database()