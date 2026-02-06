import tkinter as tk
from tkinter import ttk

class DashboardModule(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        
        # Header
        ttk.Label(self, text="Business Dashboard", font=("Segoe UI", 24, "bold")).pack(pady=20)
        
        # KPIS Container
        kpi_frame = ttk.Frame(self)
        kpi_frame.pack(fill="x", padx=20, pady=10)
        
        # KPI Cards (LabelFrames)
        self.card_sales = self.create_card(kpi_frame, "Total Sales", "₹ 0.00", 0)
        self.card_invoices = self.create_card(kpi_frame, "Total Invoices", "0", 1)
        self.card_stock = self.create_card(kpi_frame, "Low Stock Items", "0", 2)
        self.card_parties = self.create_card(kpi_frame, "Total Customers", "0", 3)
        
        # Refresh Button
        ttk.Button(self, text="Refresh Data", command=self.refresh_data).pack(pady=20)
        
        self.refresh_data()

    def create_card(self, parent, title, value, col):
        frame = ttk.LabelFrame(parent, text=title)
        frame.grid(row=0, column=col, padx=10, pady=10, sticky="nsew")
        label = ttk.Label(frame, text=value, font=("Segoe UI", 18, "bold"), foreground="#2c3e50")
        label.pack(padx=20, pady=20)
        parent.grid_columnconfigure(col, weight=1)
        return label

    def refresh_data(self):
        # 1. Total Sales (Sum of finalised invoices)
        # Handle NULL result if no invoices
        res = self.db.execute_query("SELECT SUM(total_amount) FROM invoices WHERE status='final'")
        total_sales = res[0][0] if res and res[0][0] else 0.0
        self.card_sales.config(text=f"₹ {total_sales:,.2f}")
        
        # 2. Invoice Count
        res = self.db.execute_query("SELECT COUNT(*) FROM invoices")
        count_inv = res[0][0] if res else 0
        self.card_invoices.config(text=str(count_inv))
        
        # 3. Low Stock (< 10 units)
        # Ensure stock_quantity column exists (we added it in migration)
        try:
            res = self.db.execute_query("SELECT COUNT(*) FROM items WHERE stock_quantity < 10")
            low_stock = res[0][0] if res else 0
            self.card_stock.config(text=str(low_stock), foreground="red" if low_stock > 0 else "green")
        except Exception:
            self.card_stock.config(text="Err") # Fallback if migration failed

        # 4. Total Parties
        res = self.db.execute_query("SELECT COUNT(*) FROM parties")
        count_parties = res[0][0] if res else 0
        self.card_parties.config(text=str(count_parties))
