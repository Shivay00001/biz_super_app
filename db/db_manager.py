import sqlite3
import os

class DBManager:
    def __init__(self, db_path="biz_app.db"):
        self.db_path = db_path
        self.conn = None
        self.initialize_db()

    def get_connection(self):
        if not self.conn:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def initialize_db(self):
        """Creates tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Read schema from file if it exists, otherwise use a hardcoded string or relative path
        # Assuming schema.sql is in the same directory as this file
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        
        if os.path.exists(schema_path):
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
                cursor.executescript(schema_sql)
        else:
            print("Schema file not found!")
            
        conn.commit()
    
    def execute_query(self, query, params=(), commit=False):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        if commit:
            conn.commit()
            return cursor.lastrowid
        return cursor.fetchall()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
