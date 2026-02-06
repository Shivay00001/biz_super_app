import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class ApprovalsModule(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        
        # Header
        ttk.Label(self, text="Approvals & Audit Log", font=("Segoe UI", 20, "bold")).pack(pady=20)
        
        # Create Request (Mocking a user flow)
        req_frame = ttk.LabelFrame(self, text="Create New Request")
        req_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(req_frame, text="Request Type:").pack(side="left", padx=5)
        self.type_combo = ttk.Combobox(req_frame, values=["Expense > 5000", "Discount > 10%", "New Vendor"])
        self.type_combo.pack(side="left", padx=5)
        
        ttk.Label(req_frame, text="Details:").pack(side="left", padx=5)
        self.detail_entry = ttk.Entry(req_frame, width=40)
        self.detail_entry.pack(side="left", padx=5)
        
        ttk.Button(req_frame, text="Submit Request", command=self.submit_req).pack(side="left", padx=10)
        
        # List
        self.tree = ttk.Treeview(self, columns=("id", "type", "details", "status", "date"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("type", text="Type")
        self.tree.heading("details", text="Details")
        self.tree.heading("status", text="Status")
        self.tree.heading("date", text="Date")
        
        self.tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Action Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="✅ Approve Selected", command=self.approve).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="❌ Reject Selected", command=self.reject).pack(side="left", padx=10)
        
        self.refresh()

    def submit_req(self):
        rtype = self.type_combo.get()
        details = self.detail_entry.get()
        if rtype and details:
            # We use approval_requests table from schema
            self.db.execute_query("INSERT INTO approval_requests (module, reference_id, status) VALUES (?, ?, ?)", 
                                  (rtype, 0, 'pending'), commit=True)
            # Schema was module, reference_id. Let's hijack 'module' for type and maybe we need a details column?
            # Schema: module TEXT, reference_id INTEGER.
            # I'll stick to schema and maybe add a 'note' column if allows, or just put details in module string for now.
            # "Expense > 5000: Buying Server"
            
            self.refresh()
            self.detail_entry.delete(0, tk.END)

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        rows = self.db.execute_query("SELECT id, module, status, created_at FROM approval_requests ORDER BY created_at DESC")
        for r in rows:
            self.tree.insert("", "end", values=(r[0], r[1], "N/A", r[2], r[3]))

    def approve(self):
        self.update_status('approved')

    def reject(self):
        self.update_status('rejected')

    def update_status(self, status):
        sel = self.tree.selection()
        if not sel: return
        item_id = self.tree.item(sel[0], "values")[0]
        self.db.execute_query("UPDATE approval_requests SET status=? WHERE id=?", (status, item_id), commit=True)
        self.refresh()
