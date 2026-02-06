import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv

class InventoryModule(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        
        # Header
        header = ttk.Frame(self)
        header.pack(fill="x", padx=20, pady=10)
        ttk.Label(header, text="Inventory & Stock", style="Header.TLabel").pack(side="left")
        
        # Global Actions
        btn_frame = ttk.Frame(header)
        btn_frame.pack(side="right")
        ttk.Button(btn_frame, text="+ Add Item", command=self.show_add_item).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📊 Export CSV", command=self.export_csv).pack(side="left", padx=5)
        
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Pass self to StockListFrame so it can callback to notebook
        self.stock_list_frame = StockListFrame(self.notebook, self.db)
        self.notebook.add(self.stock_list_frame, text="Current Stock")
        
        self.add_item_frame = AddItemFrame(self.notebook, self.db, self.on_item_saved)

    def show_add_item(self):
        if "Add Item" not in [self.notebook.tab(i, "text") for i in range(self.notebook.index("end"))]:
            self.notebook.add(self.add_item_frame, text="Add Item")
        self.notebook.select(self.add_item_frame)

    def on_item_saved(self):
        messagebox.showinfo("Success", "Item Saved Successfully!")
        self.stock_list_frame.refresh_data()
        self.notebook.forget(self.add_item_frame)

    def export_csv(self):
        try:
            filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
            if not filename: return
            
            # Calculated Export: Value = Price * Stock
            query = "SELECT name, sku, price, stock_quantity, (price * stock_quantity) as value FROM items"
            rows = self.db.execute_query(query)
            
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Item Name", "SKU", "Price", "Stock Qty", "Total Value"])
                writer.writerows(rows)
                
            messagebox.showinfo("Success", f"Inventory Exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

class StockListFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        
        # Toolbar
        tool_frame = ttk.Frame(self)
        tool_frame.pack(fill="x", pady=5)
        ttk.Button(tool_frame, text="🗑️ Delete Selected", command=self.delete_item, style="Danger.TButton").pack(side="right", padx=5)
        
        self.tree = ttk.Treeview(self, columns=("id", "sku", "name", "price", "stock", "value"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("sku", text="SKU")
        self.tree.heading("name", text="Item Name")
        self.tree.heading("price", text="Price")
        self.tree.heading("stock", text="Stock Qty")
        self.tree.heading("value", text="Stock Value")
        
        self.tree.column("id", width=50)
        self.tree.pack(fill="both", expand=True)
        
        self.refresh_data()

    def refresh_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        query = "SELECT id, sku, name, price, stock_quantity FROM items"
        rows = self.db.execute_query(query)
        for row in rows:
            r = list(row)
            try:
                val = r[3] * r[4]
            except: val = 0
            self.tree.insert("", "end", values=(r[0], r[1], r[2], f"₹ {r[3]}", r[4], f"₹ {val:.2f}"))

    def delete_item(self):
        sel = self.tree.selection()
        if not sel: return
        
        if not messagebox.askyesno("Confirm", "Delete selected item? This cannot be undone."):
            return
            
        try:
            item_id = self.tree.item(sel[0], "values")[0]
            self.db.execute_query("DELETE FROM items WHERE id=?", (item_id,), commit=True)
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")

class AddItemFrame(ttk.Frame):
    def __init__(self, parent, db, on_save):
        super().__init__(parent)
        self.db = db
        self.on_save = on_save
        
        form = ttk.LabelFrame(self, text="Item Details")
        form.pack(fill="x", padx=20, pady=20)
        
        ttk.Label(form, text="Item Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name = ttk.Entry(form)
        self.name.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form, text="SKU Code:").grid(row=0, column=2, padx=5, pady=5)
        self.sku = ttk.Entry(form)
        self.sku.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form, text="Selling Price:").grid(row=1, column=0, padx=5, pady=5)
        self.price = ttk.Entry(form)
        self.price.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form, text="Opening Stock:").grid(row=1, column=2, padx=5, pady=5)
        self.stock = ttk.Entry(form)
        self.stock.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(form, text="Tax Rate (%):").grid(row=2, column=0, padx=5, pady=5)
        self.tax = ttk.Entry(form)
        self.tax.grid(row=2, column=1, padx=5, pady=5)
        self.tax.insert(0, "18.0")
        
        ttk.Button(self, text="Save Item", command=self.save).pack(pady=20)

    def save(self):
        try:
            self.db.execute_query(
                "INSERT INTO items (name, sku, price, stock_quantity, tax_rate) VALUES (?, ?, ?, ?, ?)",
                (self.name.get(), self.sku.get(), float(self.price.get()), float(self.stock.get()), float(self.tax.get())),
                commit=True
            )
            val = self.on_save()
        except Exception as e:
            messagebox.showerror("Error", str(e))
