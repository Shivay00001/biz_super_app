import sqlite3
import os

db_path = "C:/Users/shiva/.gemini/antigravity/scratch/biz_super_app/biz_app.db"

def migrate():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Check if column exists
        cursor.execute("PRAGMA table_info(items)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if 'stock_quantity' not in columns:
            print("Adding stock_quantity column...")
            cursor.execute("ALTER TABLE items ADD COLUMN stock_quantity REAL DEFAULT 0")
        
        if 'tax_rate' not in columns:
            print("Adding tax_rate column...")
            cursor.execute("ALTER TABLE items ADD COLUMN tax_rate REAL DEFAULT 18.0")
            
        if 'hsn_code' not in columns:
            print("Adding hsn_code column...")
            cursor.execute("ALTER TABLE items ADD COLUMN hsn_code TEXT")
            
        conn.commit()
        print("Migration successful.")
            
        conn.close()
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
