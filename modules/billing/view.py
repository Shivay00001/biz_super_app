import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
import os

class BillingModule(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        
        # Header
        header = ttk.Frame(self)
        header.pack(fill="x", padx=20, pady=10)
        ttk.Label(header, text="Billing & Professional Invoices", font=("Segoe UI", 20, "bold")).pack(side="left")
        
        # Tab Control
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.invoice_list_frame = InvoiceListFrame(self.notebook, self.db)
        self.notebook.add(self.invoice_list_frame, text="All Invoices")
        
        self.create_invoice_frame = CreateInvoiceFrame(self.notebook, self.db, self.on_invoice_saved)
        self.notebook.add(self.create_invoice_frame, text="New Invoice")

        self.party_frame = PartyMasterFrame(self.notebook, self.db)
        self.notebook.add(self.party_frame, text="Parties (Customers)")

    def on_invoice_saved(self):
        messagebox.showinfo("Success", "Invoice Saved Successfully!")
        self.invoice_list_frame.refresh_data()
        self.notebook.select(self.invoice_list_frame)

class InvoiceListFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        
        # Action Bar
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="🖨️ Print / Download PDF", command=self.print_pdf).pack(side="left", padx=20)
        ttk.Button(btn_frame, text="📊 Export CSV", command=self.export_csv).pack(side="left", padx=20)
        ttk.Button(btn_frame, text="🔄 Refresh", command=self.refresh_data).pack(side="left", padx=20)

        # Treeview
        columns = ("id", "number", "party", "date", "amount", "status")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("number", text="Invoice #")
        self.tree.heading("party", text="Party")
        self.tree.heading("date", text="Date")
        self.tree.heading("amount", text="Amount")
        self.tree.heading("status", text="Status")
        
        self.tree.column("id", width=50)
        self.tree.column("number", width=120)
        self.tree.column("party", width=200)
        
        self.tree.pack(fill="both", expand=True)
        
        self.refresh_data()

    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        query = """
            SELECT i.id, i.invoice_number, p.name as party_name, i.date, i.total_amount, i.status 
            FROM invoices i
            LEFT JOIN parties p ON i.party_id = p.id
            ORDER BY i.created_at DESC
        """
        rows = self.db.execute_query(query)
        for row in rows:
            self.tree.insert("", "end", values=(row[0], row[1], row[2], row[3], f"₹ {row[4]:.2f}", row[5]))

    def print_pdf(self):
        sel = self.tree.selection()
        if not sel: return
        
        inv_id, inv_num, party_name, inv_date, amt, status = self.tree.item(sel[0], "values")
        
        # Fetch Full Details
        items_rows = self.db.execute_query("""
            SELECT i.name, ii.quantity, ii.rate, ii.total
            FROM invoice_items ii
            JOIN items i ON ii.item_id = i.id
            WHERE ii.invoice_id = ?
        """, (inv_id,))
        
        items = [{'name': r[0], 'qty': r[1], 'rate': r[2], 'total': r[3]} for r in items_rows]
        
        # Party Phone
        party_res = self.db.execute_query("SELECT phone FROM parties WHERE name=?", (party_name,))
        party_phone = party_res[0][0] if party_res else "N/A"
        
        # Generate
        from common.pdf_generator import PDFGenerator
        pdf = PDFGenerator()
        path = pdf.generate_invoice(
            {'number': inv_num, 'party_name': party_name, 'party_phone': party_phone, 'date': inv_date, 'total_amount': float(amt.replace("₹ ",""))},
            items
        )
        
        if messagebox.askyesno("PDF Created", f"Invoice Saved at:\n{path}\n\nOpen now?"):
            os.startfile(path)

    def export_csv(self):
        try:
            filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
            if not filename: return
            
            import csv
            query = """
                SELECT i.invoice_number, p.name, i.date, i.total_amount, i.status 
                FROM invoices i
                LEFT JOIN parties p ON i.party_id = p.id
                ORDER BY i.date DESC
            """
            rows = self.db.execute_query(query)
            
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Invoice Number", "Party Name", "Date", "Total Amount", "Status"])
                writer.writerows(rows)
                
            messagebox.showinfo("Success", f"Data Exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

class CreateInvoiceFrame(ttk.Frame):
    def __init__(self, parent, db, on_save_callback):
        super().__init__(parent)
        self.db = db
        self.on_save_callback = on_save_callback
        self.items = [] 
        
        # Form Container
        form_frame = ttk.Frame(self)
        form_frame.pack(fill="x", padx=20, pady=20)
        
        # Top Row
        ttk.Label(form_frame, text="Party:").grid(row=0, column=0, padx=5, sticky="w")
        self.party_var = tk.StringVar()
        self.party_combo = ttk.Combobox(form_frame, textvariable=self.party_var)
        self.party_combo.grid(row=0, column=1, padx=5, sticky="w")
        
        ttk.Label(form_frame, text="Inv #:").grid(row=0, column=2, padx=5, sticky="w")
        self.inv_num_entry = ttk.Entry(form_frame, width=15)
        self.inv_num_entry.grid(row=0, column=3, padx=5)
        self.inv_num_entry.insert(0, f"INV-{date.today().strftime('%Y%m%d')}-001")

        ttk.Label(form_frame, text="Date:").grid(row=0, column=4, padx=5, sticky="w")
        self.date_entry = ttk.Entry(form_frame, width=12)
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.grid(row=0, column=5, padx=5)
        
        ttk.Button(form_frame, text="Refresh DB", command=self.load_master_data).grid(row=0, column=6, padx=10)

        # Add Item Section
        item_frame = ttk.LabelFrame(self, text="Add Items")
        item_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(item_frame, text="Select Item").grid(row=0, column=0)
        self.item_var = tk.StringVar()
        self.item_combo = ttk.Combobox(item_frame, textvariable=self.item_var, width=30)
        self.item_combo.grid(row=1, column=0, padx=5, pady=5)
        self.item_combo.bind("<<ComboboxSelected>>", self.on_item_select)
        
        ttk.Label(item_frame, text="Qty").grid(row=0, column=1)
        self.qty_entry = ttk.Entry(item_frame, width=10)
        self.qty_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(item_frame, text="Rate (Tax Incl)").grid(row=0, column=2)
        self.rate_entry = ttk.Entry(item_frame, width=10)
        self.rate_entry.grid(row=1, column=2, padx=5, pady=5)
        
        ttk.Button(item_frame, text="Add Line", command=self.add_line_item).grid(row=1, column=3, padx=5)

        # Items Grid
        self.tree = ttk.Treeview(self, columns=("item_id", "item_name", "qty", "rate", "tax", "total"), show="headings", height=8)
        self.tree.heading("item_id", text="ID")
        self.tree.heading("item_name", text="Item")
        self.tree.heading("qty", text="Qty")
        self.tree.heading("rate", text="Rate")
        self.tree.heading("tax", text="Tax %")
        self.tree.heading("total", text="Total")
        self.tree.column("item_id", width=0, stretch=False)
        self.tree.pack(fill="x", padx=20, pady=10)
        
        # Footer
        footer = ttk.Frame(self)
        footer.pack(fill="x", padx=20, pady=20)
        self.total_label = ttk.Label(footer, text="Total: ₹ 0.00", font=("Segoe UI", 14, "bold"))
        self.total_label.pack(side="right", padx=20)
        ttk.Button(footer, text="Save Invoice", command=self.save_invoice).pack(side="right")

        self.load_master_data()

    def load_master_data(self):
        parties = self.db.execute_query("SELECT id, name FROM parties")
        self.party_map = {p[1]: p[0] for p in parties}
        self.party_combo['values'] = list(self.party_map.keys())
        
        try:
             items = self.db.execute_query("SELECT id, name, price, stock_quantity, tax_rate FROM items")
        except:
             items = self.db.execute_query("SELECT id, name, price, stock_quantity FROM items")
             items = [list(i) + [18.0] for i in items] 

        self.product_map = {i[1]: {'id': i[0], 'price': i[2], 'stock': i[3], 'tax': i[4]} for i in items}
        self.item_combo['values'] = list(self.product_map.keys())

    def on_item_select(self, event):
        name = self.item_var.get()
        if name in self.product_map:
            rate = self.product_map[name]['price']
            self.rate_entry.delete(0, tk.END)
            self.rate_entry.insert(0, str(rate))
            self.qty_entry.delete(0, tk.END)
            self.qty_entry.insert(0, "1")

    def add_line_item(self):
        name = self.item_var.get()
        qty = self.qty_entry.get()
        rate = self.rate_entry.get()
        
        if not name or not qty: return
        
        info = self.product_map.get(name)
        if not info:
             messagebox.showerror("Error", "Invalid Item")
             return

        try:
            qty = float(qty)
            rate = float(rate)
            total = qty * rate
            
            if qty > info['stock']:
                if not messagebox.askyesno("Stock Warning", f"Avail Stock: {info['stock']}. Proceed?"):
                    return
            
            self.items.append({
                "id": info['id'], "name": name, "qty": qty, 
                "rate": rate, "tax": info['tax'], "total": total
            })
            self.tree.insert("", "end", values=(info['id'], name, qty, rate, f"{info['tax']}%", total))
            self.update_total()
            
            self.item_var.set('')
            self.qty_entry.delete(0, tk.END)
            self.rate_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Invalid numbers")

    def update_total(self):
        total = sum(i['total'] for i in self.items)
        self.total_label.config(text=f"Total: ₹ {total:.2f}")

    def save_invoice(self):
        party_name = self.party_var.get()
        if not party_name or not self.items:
            messagebox.showerror("Error", "Select Party and Add Items")
            return
            
        party_id = self.party_map.get(party_name)
        if not party_id:
             messagebox.showerror("Error", "Invalid Party. Add in Party Master first.")
             return
        
        conn = self.db.get_connection()
        try:
            total_amt = sum(i['total'] for i in self.items)
            
            # create invoice
            cur = conn.execute("INSERT INTO invoices (invoice_number, party_id, date, total_amount, status) VALUES (?, ?, ?, ?, ?)",
                         (self.inv_num_entry.get(), party_id, self.date_entry.get(), total_amt, 'final'))
            inv_id = cur.lastrowid
            
            # invoice items
            for item in self.items:
                conn.execute("INSERT INTO invoice_items (invoice_id, item_id, quantity, rate, total) VALUES (?, ?, ?, ?, ?)",
                             (inv_id, item['id'], item['qty'], item['rate'], item['total']))
                
                # update stock
                conn.execute("UPDATE items SET stock_quantity = stock_quantity - ? WHERE id = ?", (item['qty'], item['id']))
            
            conn.commit()
            
            # PDF
            if messagebox.askyesno("Success", "Invoice Saved! Generate PDF?"):
                party_phone = "N/A"
                from common.pdf_generator import PDFGenerator
                pdf = PDFGenerator()
                path = pdf.generate_invoice(
                    {'number': self.inv_num_entry.get(), 'party_name': party_name, 'party_phone': party_phone, 'date': self.date_entry.get(), 'total_amount': total_amt},
                    self.items
                )
                os.startfile(path)

            # Clear
            self.items = []
            self.tree.delete(*self.tree.get_children())
            self.update_total()
            self.on_save_callback()
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Error", f"Save Failed: {e}")

class PartyMasterFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        
        # Add Party
        frame = ttk.LabelFrame(self, text="Add New Party")
        frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame, text="Phone:").grid(row=0, column=2, padx=5, pady=5)
        self.phone_entry = ttk.Entry(frame)
        self.phone_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Button(frame, text="Add Party", command=self.add_party).grid(row=0, column=4, padx=10)
        
        # List
        self.tree = ttk.Treeview(self, columns=("id", "name", "phone"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("phone", text="Phone")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh_list()

    def add_party(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        if name:
            self.db.execute_query("INSERT INTO parties (name, phone) VALUES (?, ?)", (name, phone), commit=True)
            self.name_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
            self.refresh_list()

    def refresh_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = self.db.execute_query("SELECT id, name, phone FROM parties")
        for row in rows:
            self.tree.insert("", "end", values=row)
