import json
import sqlite3
import urllib.request


class FirstAidDatabase:
    def __init__(self, db_name="first_aid_hybrid.db"):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        """Creates and returns a database connection with Row factory."""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Creates tables and inserts default seed data if empty."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Categories Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    icon TEXT,
                    version INTEGER DEFAULT 1,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Guides Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS guides (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER,
                    title TEXT NOT NULL,
                    symptoms TEXT,
                    steps TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories (id)
                );
            """)

            # Check if categories already exist; if not, insert seed data
            cursor.execute("SELECT COUNT(*) FROM categories")
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO categories (name) VALUES ('Burns & Scalds')")
                burns_id = cursor.lastrowid

                cursor.execute("INSERT INTO categories (name) VALUES ('Wounds & Bleeding')")
                wounds_id = cursor.lastrowid

                cursor.execute("INSERT INTO categories (name) VALUES ('Choking & CPR')")
                cpr_id = cursor.lastrowid

                # Insert Sample Guides
                cursor.execute("""
                    INSERT INTO guides (category_id, title, symptoms, steps)
                    VALUES (?, ?, ?, ?)
                """, (
                    burns_id,
                    "Minor Thermal Burns",
                    "Red skin, pain, mild swelling",
                    "1. Cool the burn under cool running water for 10-20 minutes.\n2. Remove any tight jewelry or rings before swelling starts.\n3. Cover loosely with a clean, non-fluffy bandage or cloth."
                ))

                cursor.execute("""
                    INSERT INTO guides (category_id, title, symptoms, steps)
                    VALUES (?, ?, ?, ?)
                """, (
                    wounds_id,
                    "Severe Bleeding",
                    "Blood spurting or flowing continuously from a wound",
                    "1. Apply direct, firm pressure on the wound using a clean cloth or sterile bandage.\n2. Elevate the injured area above the heart if possible.\n3. Keep applying pressure and seek emergency medical help immediately."
                ))

                cursor.execute("""
                    INSERT INTO guides (category_id, title, symptoms, steps)
                    VALUES (?, ?, ?, ?)
                """, (
                    cpr_id,
                    "Adult CPR",
                    "Unresponsive, not breathing normally",
                    "1. Call for emergency help and get an AED if available.\n2. Place hands in the center of the chest and push hard and fast (100-120 beats/min).\n3. Allow the chest to recoil completely between compressions."
                ))

                conn.commit()
                print("Seed data inserted successfully!")

    def get_emergency_topics(self):
        """Fetch quick-access emergency guides for the home screen."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, symptoms, steps FROM guides LIMIT 3")
            return [dict(row) for row in cursor.fetchall()]

    def get_categories(self):
        """Fetch all categories to show on the main screen."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories ORDER BY name ASC")
            return [dict(row) for row in cursor.fetchall()]

    def get_guides_by_category(self, category_id):
        """Fetch all guide titles under a specific category."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, title, symptoms FROM guides WHERE category_id = ? ORDER BY title ASC",
                (category_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_guide_detail(self, guide_id):
        """Fetch full details (steps, symptoms) for a specific first-aid guide."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM guides WHERE id = ?", (guide_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def search_guides(self, search_term):
        """Search guides offline by title, symptoms, or steps."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = f"%{search_term}%"
            cursor.execute(
                "SELECT id, title, symptoms FROM guides WHERE title LIKE ? OR symptoms LIKE ? OR steps LIKE ?",
                (query, query, query)
            )
            return [dict(row) for row in cursor.fetchall()]

    def check_internet(self, host="https://www.google.com", timeout=3):
        """Checks if the device has an active internet connection."""
        try:
            urllib.request.urlopen(host, timeout=timeout)
            return True
        except Exception:
            return False

    def sync_guides_from_server(self, remote_guides_data):
        """
        Compares local guide versions with remote data from the server
        and updates SQLite if the remote version is newer.
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            updated_count = 0

            for remote_guide in remote_guides_data:
                guide_id = remote_guide.get('id')
                remote_version = remote_guide.get('version', 1)
                title = remote_guide.get('title')
                symptoms = remote_guide.get('symptoms')
                steps = remote_guide.get('steps')
                category_id = remote_guide.get('category_id')

                cursor.execute("SELECT version FROM guides WHERE id = ?", (guide_id,))
                local_row = cursor.fetchone()

                if local_row is None:
                    cursor.execute("""
                        INSERT INTO guides (id, category_id, title, symptoms, steps, version, last_updated)
                        VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (guide_id, category_id, title, symptoms, steps, remote_version))
                    updated_count += 1
                elif remote_version > local_row['version']:
                    cursor.execute("""
                        UPDATE guides
                        SET title = ?, symptoms = ?, steps = ?, version = ?, last_updated = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (title, symptoms, steps, remote_version, guide_id))
                    updated_count += 1

            conn.commit()
            print(f"Sync complete. Updated/Added {updated_count} guides.")
            return updated_count

    def get_topics_by_category(self, category_identifier):
        """Fetch all guides/topics belonging to a specific category by ID or Name."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if isinstance(category_identifier, int):
                cursor.execute("""
                    SELECT id, title, symptoms, steps
                    FROM guides
                    WHERE category_id = ?
                    ORDER BY title ASC
                """, (category_identifier,))
            else:
                cursor.execute("""
                    SELECT guides.id, guides.title, guides.symptoms, guides.steps
                    FROM guides
                    JOIN categories ON guides.category_id = categories.id
                    WHERE categories.name = ?
                    ORDER BY guides.title ASC
                """, (category_identifier,))
                
            return [dict(row) for row in cursor.fetchall()]
    def get_topic_with_steps(self, topic_id):
        """Fetch specific guide details and steps by its ID."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, title, symptoms, steps FROM guides WHERE id = ?", (topic_id,))
            row = cursor.fetchone()
            return dict(row) if row else None