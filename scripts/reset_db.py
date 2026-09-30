"""
SignBridge Database Reset Utility.

Deletes the existing database and recreates it with fresh seed data.
Use this when the schema changes or seed data is updated.

Usage:
    python scripts/reset_db.py
"""

import os
import sys

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Add backend to path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "backend"))

def reset_database():
    print("\n" + "=" * 50)
    print("  SignBridge Database Reset")
    print("=" * 50)

    # 1. Delete existing DB files
    db_paths = [
        os.path.join(PROJECT_ROOT, "signbridge.db"),
        os.path.join(PROJECT_ROOT, "backend", "signbridge.db"),
    ]

    for db_path in db_paths:
        if os.path.exists(db_path):
            try:
                os.remove(db_path)
                print(f"  [OK] Deleted: {db_path}")
            except PermissionError:
                print(f"  [FAIL] Cannot delete (in use): {db_path}")
                print("    Please stop the backend server first!")
                return False
        else:
            print(f"  [SKIP] Not found: {db_path}")

    # 2. Recreate database and seed
    print("\n  Recreating database...")

    # Change working directory to backend for proper relative paths
    os.chdir(os.path.join(PROJECT_ROOT, "backend"))

    from app.db.session import engine, Base, SessionLocal
    from app.db.seed_data import seed_database

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("  [OK] Tables created")

    # Seed data
    db = SessionLocal()
    try:
        seed_database(db)
        print("  [OK] Database seeded successfully")
    except Exception as e:
        print(f"  [FAIL] Seeding error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

    print("\n" + "=" * 50)
    print("  Database reset complete!")
    print("  You can now start the backend server.")
    print("=" * 50 + "\n")
    return True


if __name__ == "__main__":
    reset_database()
