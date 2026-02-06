import tkinter as tk
from tkinter import ttk
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.db_manager import DBManager

# Placeholder Modules (will implement real ones later)
class PlaceholderFrame(ttk.Frame):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.label = ttk.Label(self, text=title, font=("Segoe UI", 24))
        self.label.pack(expand=True)

class Sidebar(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#2c3e50", width=200)
        self.controller = controller
        self.pack_propagate(False)
        
        # App Title
        lbl_title = tk.Label(self, text="BizSuperApp", bg="#2c3e50", fg="white", font=("Segoe UI", 16, "bold"), pady=20)
        lbl_title.pack(fill="x")

        # Navigation Buttons
        self.add_nav_button("Dashboard", "dashboard")
        self.add_nav_button("Documents", "documents")
        self.add_nav_button("Billing", "billing")
        self.add_nav_button("Inventory", "inventory")
        self.add_nav_button("HR & Payroll", "hr")
        self.add_nav_button("Compliance", "compliance")
        self.add_nav_button("Approvals", "approvals")
        self.add_nav_button("Analytics", "analytics")

    def add_nav_button(self, text, start_page_key):
        btn = tk.Button(self, text=text, bg="#2c3e50", fg="white", font=("Segoe UI", 11), 
                        bd=0, activebackground="#34495e", activeforeground="white",
                        command=lambda: self.controller.show_frame(start_page_key), anchor="w", padx=20)
        btn.pack(fill="x", pady=2)

from core.theme import Theme
import os

class BizApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BizSuperApp (Enterprise Edition)")
        self.geometry("1100x700")
        self.state('zoomed') 
        
        # Apply Theme
        Theme.apply_theme(self)
        self.configure(bg="#FFFFFF")
        
        # Icon
        try:
            icon_path = r"C:\Users\shiva\.gemini\antigravity\brain\5e059aa8-bca2-4c4a-adca-eb07e2bf81fe\app_icon_1767380500039.png"
            if os.path.exists(icon_path):
                 img = tk.PhotoImage(file=icon_path)
                 self.iconphoto(True, img)
        except Exception as e:
            print(f"Icon error: {e}")
            
        # Database
        self.db = DBManager()
        
        # Layout
        self.sidebar = Sidebar(self, self)
        self.sidebar.pack(side="left", fill="y")
        
        self.container = ttk.Frame(self)
        self.container.pack(side="right", fill="both", expand=True)
        
        self.frames = {}
        
        # Initialize Modules
        self.init_modules()
        
        self.show_frame("dashboard")

    def init_modules(self):
        # In a real app, these would be imported classes from modules/
        from modules.billing.view import BillingModule
        
        module_map = {
            # "dashboard": "Dashboard", # Replaced above
            # "documents": "Documents & Workflow", # Replaced above
            # "inventory": "Inventory & Purchase", # Replaced above
            # "hr": "HR & Payroll", # Replaced above
            # "compliance": "One-Click Compliance", # Replaced above
            # "approvals": "Approvals Center", # Replaced above
            # "analytics": "Reports & Analytics" # Replaced above
        }
        
        # Instantiate Billing Module specifically
        from modules.billing.view import BillingModule
        billing_frame = BillingModule(self.container, self.db)
        self.frames["billing"] = billing_frame
        billing_frame.grid(row=0, column=0, sticky="nsew")

        # Instantiate Inventory Module
        from modules.inventory.view import InventoryModule
        inv_frame = InventoryModule(self.container, self.db)
        self.frames["inventory"] = inv_frame
        inv_frame.grid(row=0, column=0, sticky="nsew")

        # Instantiate Dashboard Module
        from modules.dashboard.view import DashboardModule
        dash_frame = DashboardModule(self.container, self.db)
        self.frames["dashboard"] = dash_frame
        dash_frame.grid(row=0, column=0, sticky="nsew")

        # Instantiate HR Module
        from modules.hr.view import HRModule
        hr_frame = HRModule(self.container, self.db)
        self.frames["hr"] = hr_frame
        hr_frame.grid(row=0, column=0, sticky="nsew")
        
        # Instantiate Documents Module
        from modules.documents.view import DocumentsModule
        doc_frame = DocumentsModule(self.container, self.db)
        self.frames["documents"] = doc_frame
        doc_frame.grid(row=0, column=0, sticky="nsew")

        # Instantiate Compliance Module
        from modules.compliance.view import ComplianceModule
        comp_frame = ComplianceModule(self.container, self.db)
        self.frames["compliance"] = comp_frame
        comp_frame.grid(row=0, column=0, sticky="nsew")
        
        # Instantiate Approvals Module
        from modules.approvals.view import ApprovalsModule
        app_frame = ApprovalsModule(self.container, self.db)
        self.frames["approvals"] = app_frame
        app_frame.grid(row=0, column=0, sticky="nsew")

        # Instantiate Analytics Module
        from modules.analytics.view import AnalyticsModule
        ana_frame = AnalyticsModule(self.container, self.db)
        self.frames["analytics"] = ana_frame
        ana_frame.grid(row=0, column=0, sticky="nsew")
        
        for key, title in module_map.items():
            frame = PlaceholderFrame(self.container, title)
            self.frames[key] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

    def show_frame(self, key):
        frame = self.frames[key]
        frame.tkraise()

if __name__ == "__main__":
    app = BizApp()
    app.mainloop()
