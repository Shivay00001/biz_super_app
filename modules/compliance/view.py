import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

class ComplianceModule(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.chk_vars = {}
        
        # Header
        ttk.Label(self, text="Compliance & GST Calendar", font=("Segoe UI", 20, "bold")).pack(pady=20)
        
        # Event Tracker Frame
        frame = ttk.LabelFrame(self, text="Upcoming Deadlines")
        frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Ensure Table Exists
        self.init_db()
        
        # List of Standard Indian SME Compliances
        self.month_year = date.today().strftime("%B %Y")
        ttk.Label(frame, text=f"Deadlines for {self.month_year}", font=("Segoe UI", 12, "italic")).pack(pady=5)
        
        # Scrollable canvas for tasks? Or just a simple frame loop
        self.task_container = ttk.Frame(frame)
        self.task_container.pack(fill="both", expand=True, padx=10)
        
        self.refresh_tasks()
        
        # Add Custom Task
        add_frame = ttk.Frame(self)
        add_frame.pack(fill="x", padx=20, pady=10)
        self.task_entry = ttk.Entry(add_frame)
        self.task_entry.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(add_frame, text="Add Custom Reminder", command=self.add_custom).pack(side="left")

    def init_db(self):
        self.db.execute_query("""
            CREATE TABLE IF NOT EXISTS compliance_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                due_date DATE,
                status TEXT DEFAULT 'pending'
            )
        """, commit=True)
        
        # Seed Data if Empty
        count = self.db.execute_query("SELECT COUNT(*) FROM compliance_events")[0][0]
        if count == 0:
            seed_data = [
                ("GSTR-1 Filling", "2026-01-11"),
                ("GSTR-3B Filling", "2026-01-20"),
                ("TDS Payment", "2026-01-07"),
                ("ESI/PF Deposit", "2026-01-15")
            ]
            for name, date_str in seed_data:
                self.db.execute_query("INSERT INTO compliance_events (name, due_date) VALUES (?, ?)", (name, date_str), commit=True)

    def refresh_tasks(self):
        for widget in self.task_container.winfo_children():
            widget.destroy()
            
        rows = self.db.execute_query("SELECT id, name, due_date, status FROM compliance_events ORDER BY due_date")
        
        for r in rows:
            obj_id, name, due, status = r
            
            row_frame = ttk.Frame(self.task_container)
            row_frame.pack(fill="x", pady=2)
            
            # Checkbox
            var = tk.IntVar(value=1 if status == 'done' else 0)
            self.chk_vars[obj_id] = var
            chk = ttk.Checkbutton(row_frame, variable=var, command=lambda i=obj_id, v=var: self.toggle_task(i, v))
            chk.pack(side="left")
            
            # Label
            fg = "gray" if status == 'done' else "black"
            lbl = ttk.Label(row_frame, text=f"{name} (Due: {due})", foreground=fg)
            lbl.pack(side="left", padx=10)
            
            if status == 'pending':
                ttk.Label(row_frame, text="⚠️ Pending", foreground="red").pack(side="left")
            else:
                ttk.Label(row_frame, text="✅ Done", foreground="green").pack(side="left")

    def toggle_task(self, obj_id, var_obj):
        new_status = 'done' if var_obj.get() == 1 else 'pending'
        self.db.execute_query("UPDATE compliance_events SET status=? WHERE id=?", (new_status, obj_id), commit=True)
        self.refresh_tasks()

    def add_custom(self):
        txt = self.task_entry.get()
        if txt:
            self.db.execute_query("INSERT INTO compliance_events (name, due_date) VALUES (?, ?)", (txt, date.today().isoformat()), commit=True)
            self.task_entry.delete(0, tk.END)
            self.refresh_tasks()
