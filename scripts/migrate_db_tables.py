import sqlite3

DB_PATH = 'db.sqlite3'

def migrate_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. Update Content Types
        print("Updating django_content_type...")
        cursor.execute("UPDATE django_content_type SET app_label='ordenes_trabajo' WHERE app_label='ordenes'")
        
        # 2. Update Migrations
        print("Updating django_migrations...")
        cursor.execute("UPDATE django_migrations SET app='ordenes_trabajo' WHERE app='ordenes'")

        # 3. Rename Tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'ordenes_%'")
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            new_name = table.replace('ordenes_', 'ordenes_trabajo_', 1)
            print(f"Renaming {table} -> {new_name}")
            cursor.execute(f"ALTER TABLE {table} RENAME TO {new_name}")

        conn.commit()
        print("Migration successful.")

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_db()
