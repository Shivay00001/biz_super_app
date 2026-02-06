import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import shutil
import os
import shutil
from datetime import datetime

class DocumentsModule(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        # Storage Path
        self.storage_dir = os.path.join(os.getcwd(), "my_documents_store")
        os.makedirs(self.storage_dir, exist_ok=True)
        
        # Header
        header = ttk.Frame(self)
        header.pack(fill="x", padx=20, pady=10)
        ttk.Label(header, text="Document Repository", font=("Segoe UI", 20, "bold")).pack(side="left")
        ttk.Button(header, text="+ Upload File", command=self.upload_file).pack(side="right")
        
        # Filter Bar
        filter_frame = ttk.Frame(self)
        filter_frame.pack(fill="x", padx=20, pady=5)
        ttk.Label(filter_frame, text="Search:").pack(side="left")
        self.search_entry = ttk.Entry(filter_frame)
        self.search_entry.pack(side="left", padx=5)
        ttk.Button(filter_frame, text="Go", command=self.refresh).pack(side="left")
        
        # List
        self.tree = ttk.Treeview(self, columns=("id", "name", "type", "date"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Filename")
        self.tree.heading("type", text="Type")
        self.tree.heading("date", text="Upload Date")
        self.tree.column("id", width=50)
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.tree.bind("<Double-1>", self.open_file) # Open on double click
        
        self.refresh()

    def upload_file(self):
        filepath = filedialog.askopenfilename()
        if not filepath: return
        
        filename = os.path.basename(filepath)
        doc_type = os.path.splitext(filename)[1].upper()
        
        # Copy file
        dest_path = os.path.join(self.storage_dir, f"{int(datetime.now().timestamp())}_{filename}")
        try:
            shutil.copy(filepath, dest_path)
            
            # Save to DB
            self.db.execute_query("""
                INSERT INTO documents (filename, filepath, doc_type) VALUES (?, ?, ?)
            """, (filename, dest_path, doc_type), commit=True)
            
            self.refresh()
            messagebox.showinfo("Success", "File Uploaded Securely")
            
        except Exception as e:
            messagebox.showerror("Error", f"Upload Failed: {e}")

    def open_file(self, event):
        item = self.tree.selection()
        if not item: return
        doc_id = self.tree.item(item[0], "values")[0]
        
        # Fetch path
        res = self.db.execute_query("SELECT filepath FROM documents WHERE id=?", (doc_id,))
        if res:
            path = res[0][0]
            if os.path.exists(path):
                os.startfile(path) # Windows only
            else:
                messagebox.showerror("Error", "File not found on disk!")

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        search = self.search_entry.get()
        query = "SELECT id, filename, doc_type, upload_date FROM documents"
        params = ()
        if search:
            query += " WHERE filename LIKE ?"
            params = (f"%{search}%",)
            
        query += " ORDER BY upload_date DESC"
            
        try:
            rows = self.db.execute_query(query, params)
            for row in rows:
                self.tree.insert("", "end", values=tuple(row))
        except:
            pass # Table might missing if schema not init (it is in schema.sql though)
