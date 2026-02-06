import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta, date
import math

class AnalyticsModule(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        
        # Header
        header = ttk.Frame(self)
        header.pack(fill="x", padx=20, pady=10)
        ttk.Label(header, text="Business Intelligence & Analytics", style="Header.TLabel").pack(side="left")
        
        # Controls Frame
        ctrl_frame = ttk.LabelFrame(self, text="Report Configuration", padding=10)
        ctrl_frame.pack(fill="x", padx=20, pady=5)
        
        # Report Type
        ttk.Label(ctrl_frame, text="Report Type:").pack(side="left", padx=5)
        self.report_type = tk.StringVar(value="Sales Trend (Bar)")
        type_combo = ttk.Combobox(ctrl_frame, textvariable=self.report_type, state="readonly", width=25)
        type_combo['values'] = ["Sales Trend (Bar)", "Top Products (Pie)", "Top Customers (Pie)"]
        type_combo.pack(side="left", padx=5)
        type_combo.bind("<<ComboboxSelected>>", self.refresh_report)
        
        # Period
        ttk.Label(ctrl_frame, text=" |  Period:").pack(side="left", padx=10)
        self.period_var = tk.StringVar(value="Monthly")
        periods = ["Daily", "Monthly", "Annual"] # Simplified for Pie logic compat
        for p in periods:
            ttk.Radiobutton(ctrl_frame, text=p, variable=self.period_var, value=p, command=self.refresh_report).pack(side="left", padx=5)
            
        ttk.Button(ctrl_frame, text="Generate", command=self.refresh_report).pack(side="left", padx=20)
        
        # Split View
        content = ttk.PanedWindow(self, orient="horizontal")
        content.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.chart_frame = ttk.Frame(content) 
        self.canvas = tk.Canvas(self.chart_frame, bg="white", height=450)
        self.canvas.pack(fill="both", expand=True)
        content.add(self.chart_frame, weight=3)
        
        self.text_frame = ttk.Frame(content, padding=10)
        content.add(self.text_frame, weight=1)
        
        self.stats_lbl = ttk.Label(self.text_frame, text="Details", font=("Segoe UI", 11), background="white", padding=10, relief="flat")
        self.stats_lbl.pack(fill="both", expand=True)
        
        self.refresh_report()

    def get_date_filter(self, period):
        if period == "Daily": return "WHERE i.date >= date('now', '-30 days')"
        if period == "Monthly": return "WHERE i.date >= date('now', '-12 months')"
        return "WHERE i.date >= date('now', '-5 years')"

    def refresh_report(self, event=None):
        rtype = self.report_type.get()
        period = self.period_var.get()
        filter_clause = self.get_date_filter(period)
        
        if "Bar" in rtype:
            self.show_trend_bar(period, filter_clause)
        elif "Products" in rtype:
            self.show_product_pie(period, filter_clause)
        else:
            self.show_customer_pie(period, filter_clause)

    def show_trend_bar(self, period, filter_clause):
        # ... (Previous Bar Logic adjusted) ...
        grp_fmt = "%Y-%m-%d" if period == "Daily" else ("%Y-%m" if period == "Monthly" else "%Y")
        
        query = f"""
            SELECT strftime('{grp_fmt}', i.date) as p, SUM(i.total_amount), COUNT(*)
            FROM invoices i
            {filter_clause}
            GROUP BY p
            ORDER BY p ASC
        """
        rows = self.db.execute_query(query)
        data = [(r[0], r[1], r[2]) for r in rows]
        
        self.draw_bar_chart(data, f"Sales {period}")
        
        # Summary
        total = sum(d[1] for d in data)
        self.update_summary(f"Trend: {period}", total, sum(d[2] for d in data), data)

    def show_product_pie(self, period, filter_clause):
        # Top 5 Products by Revenue
        query = f"""
            SELECT it.name, SUM(ii.total) as val
            FROM invoice_items ii
            JOIN invoices i ON ii.invoice_id = i.id
            JOIN items it ON ii.item_id = it.id
            {filter_clause}
            GROUP BY it.name
            ORDER BY val DESC
            LIMIT 5
        """
        rows = self.db.execute_query(query)
        self.draw_pie_chart(rows, "Top 5 Products")
        self.update_summary("Top Products", sum(r[1] for r in rows), 0, rows, is_pie=True)

    def show_customer_pie(self, period, filter_clause):
        # Top 5 Customers by Revenue
        query = f"""
            SELECT p.name, SUM(i.total_amount) as val
            FROM invoices i
            JOIN parties p ON i.party_id = p.id
            {filter_clause}
            GROUP BY p.name
            ORDER BY val DESC
            LIMIT 5
        """
        rows = self.db.execute_query(query)
        self.draw_pie_chart(rows, "Top 5 Customers")
        self.update_summary("Top Customers", sum(r[1] for r in rows), 0, rows, is_pie=True)

    def draw_bar_chart(self, data, title):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 600
        h = 400
        if not data:
            self.canvas.create_text(w/2, h/2, text="No Data Available")
            return
            
        max_val = max(d[1] for d in data) * 1.1
        bar_w = max(20, min(50, (w-100)/len(data) - 10))
        x_start = 50
        y_base = h - 50
        
        self.canvas.create_text(w/2, 20, text=title, font=("Segoe UI", 14, "bold"), fill="#555")
        
        for i, (lbl, val, _) in enumerate(data):
            bar_h = (val / max_val) * (h - 100)
            x0 = x_start + i * (bar_w + 10)
            y0 = y_base - bar_h
            
            self.canvas.create_rectangle(x0, y0, x0+bar_w, y_base, fill="#0078D7", outline="")
            self.canvas.create_text(x0+bar_w/2, y0-10, text=f"{int(val/1000)}k", font=("Arial", 8))
            
            # X Label
            dlbl = lbl[5:] if "-" in lbl else lbl 
            self.canvas.create_text(x0+bar_w/2, y_base+15, text=dlbl, font=("Arial", 8))

    def draw_pie_chart(self, data, title):
        self.canvas.delete("all")
        w = self.canvas.winfo_width() or 600
        h = 400
        if not data:
            self.canvas.create_text(w/2, h/2, text="No Data Available")
            return
            
        total = sum(r[1] for r in data)
        if total == 0: return

        cx, cy = w/2 - 100, h/2 # Shift left to make room for legend
        radius = 120
        
        colors = ["#0078D7", "#00B294", "#E81123", "#FFB900", "#7A7574", "#FF8C00"]
        start_angle = 0
        
        self.canvas.create_text(w/2, 20, text=title, font=("Segoe UI", 14, "bold"), fill="#555")
        
        legend_x = cx + radius + 40
        legend_y = cy - radius + 20

        for i, (label, val) in enumerate(data):
            angle = (val / total) * 360
            color = colors[i % len(colors)]
            
            # Slice
            self.canvas.create_arc(cx-radius, cy-radius, cx+radius, cy+radius,
                                   start=start_angle, extent=angle, fill=color, outline="white")
            
            # Legend
            self.canvas.create_rectangle(legend_x, legend_y + i*30, legend_x+20, legend_y + i*30 + 20, fill=color, outline="")
            pct = (val/total)*100
            self.canvas.create_text(legend_x+30, legend_y + i*30 + 10, text=f"{label} ({pct:.1f}%)", anchor="w", font=("Segoe UI", 10))
            
            start_angle += angle

    def update_summary(self, mode, total, count, data, is_pie=False):
        txt = f"REPORT: {mode.upper()}\n"
        txt += "-"*30 + "\n"
        txt += f"TOTAL VALUE: ₹ {total:,.2f}\n"
        if not is_pie:
            txt += f"TOTAL INVOICES: {count}\n"
            avg = total/count if count else 0
            txt += f"AVG TICKET: ₹ {avg:,.2f}\n"
        
        txt += "\nBREAKDOWN:\n"
        txt += "-"*30 + "\n"
        
        loop_data = data if is_pie else data[-5:] # Show last 5 for trend, all 5 for pie
        
        for row in loop_data:
            key = row[0]
            val = row[1]
            txt += f"{key}: ₹ {val:,.2f}\n"
            
        self.stats_lbl.config(text=txt)
