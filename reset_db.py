import sqlite3
import os

def reset_database():
    db_path = "interview.db"
    
    if not os.path.exists(db_path):
        print(f"[-] Database file '{db_path}' not found. Nothing to reset.")
        return

    print("[*] Connecting to database...")
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Get list of all tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c.fetchall() if row[0] not in ('sqlite_sequence', 'smtp_settings')]

    print(f"[*] Found {len(tables)} data tables to clear: {', '.join(tables)}")

    for table in tables:
        try:
            # Count records before clearing
            c.execute(f"SELECT COUNT(*) FROM {table}")
            count_before = c.fetchone()[0]
            
            # Delete all records
            c.execute(f"DELETE FROM {table}")
            conn.commit()
            
            print(f"[+] Cleared table '{table}': removed {count_before} records.")
        except Exception as e:
            print(f"[x] Error clearing table '{table}': {e}")

    # Reset the auto-increment sequences in sqlite_sequence
    try:
        c.execute("DELETE FROM sqlite_sequence WHERE name != 'smtp_settings'")
        conn.commit()
        print("[+] Reset auto-increment sequences.")
    except Exception as e:
        print(f"[x] Error resetting sequences: {e}")

    # Vacuum the database to reclaim disk space
    try:
        conn.execute("VACUUM")
        conn.commit()
        print("[+] Successfully vacuumed the database.")
    except Exception as e:
        print(f"[x] Error vacuuming database: {e}")

    conn.close()
    print("[+] Database reset completed! Tables are preserved, but all user and interview data has been erased.")

if __name__ == '__main__':
    reset_database()
