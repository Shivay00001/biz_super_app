import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.db_manager import DBManager
import time

TEST_DB = "test_auto_gen.db"

def test_generation():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
        print(f"Removed existing {TEST_DB}")

    print("Initializing DB Manager with missing DB file...")
    db = DBManager(db_path=TEST_DB)
    
    if os.path.exists(TEST_DB):
        print("✅ SUCCESS: Database file created automatically.")
    else:
        print("❌ FAILURE: Database file NOT created.")
        return

    # Check Tables
    tables = db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
    table_names = [t[0] for t in tables]
    print(f"Tables found: {table_names}")
    
    expected = ['items', 'parties', 'invoices', 'invoice_items', 'employees']
    missing = [t for t in expected if t not in table_names]
    
    if not missing:
        print("✅ SUCCESS: All core tables created.")
    else:
        print(f"❌ FAILURE: Missing tables: {missing}")

    db.close()
    # Cleanup
    try:
        os.remove(TEST_DB)
    except:
        pass

if __name__ == "__main__":
    test_generation()
