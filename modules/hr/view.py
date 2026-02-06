import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from datetime import date
import os

class HRModule(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        
        ttk.Label(self, text="HR & Payroll", style="Header.TLabel").pack(pady=10)
        
        # Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.employee_frame = EmployeeListFrame(self.notebook, self.db)
        self.notebook.add(self.employee_frame, text="Employees")
        
        self.payroll_frame = PayrollFrame(self.notebook, self.db)
        self.notebook.add(self.payroll_frame, text="Payroll Calculator")

class EmployeeListFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        
        # Add Employee Form
        form = ttk.LabelFrame(self, text="Add New Employee")
        form.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(form, text="Name:").grid(row=0, column=0, padx=5)
        self.name_entry = ttk.Entry(form)
        self.name_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(form, text="Role:").grid(row=0, column=2, padx=5)
        self.role_entry = ttk.Entry(form)
        self.role_entry.grid(row=0, column=3, padx=5)
        
        ttk.Label(form, text="Base Salary:").grid(row=0, column=4, padx=5)
        self.salary_entry = ttk.Entry(form)
        self.salary_entry.grid(row=0, column=5, padx=5)
        
        ttk.Button(form, text="Add", command=self.add_emp).grid(row=0, column=6, padx=10)
        
        # Toolbar
        tool = ttk.Frame(self)
        tool.pack(fill="x", padx=10)
        ttk.Button(tool, text="📊 Export CSV", command=self.export_csv).pack(side="left")
        ttk.Button(tool, text="🗑️ Delete", command=self.delete_emp, style="Danger.TButton").pack(side="right")
        
        # List
        self.tree = ttk.Treeview(self, columns=("id", "name", "role", "salary"), show="headings")
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("role", text="Role")
        self.tree.heading("salary", text="Salary")
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.refresh()

    def add_emp(self):
        name = self.name_entry.get()
        role = self.role_entry.get()
        salary = self.salary_entry.get()
        
        if not name: return
        
        try:
            self.db.execute_query("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    role TEXT,
                    base_salary REAL
                )
            """, commit=True)
            
            self.db.execute_query("INSERT INTO employees (name, role, base_salary) VALUES (?, ?, ?)", 
                                  (name, role, float(salary) if salary else 0), commit=True)
            self.refresh()
            self.name_entry.delete(0, tk.END)
            self.role_entry.delete(0, tk.END)
            self.salary_entry.delete(0, tk.END)
            
        except Exception as e:
             messagebox.showerror("Error", str(e))

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            rows = self.db.execute_query("SELECT id, name, role, base_salary FROM employees")
            for row in rows:
                self.tree.insert("", "end", values=tuple(row))
        except:
            pass 

    def delete_emp(self):
        sel = self.tree.selection()
        if not sel: return
        if messagebox.askyesno("Delete", "Remove Employee?"):
            eid = self.tree.item(sel[0], "values")[0]
            self.db.execute_query("DELETE FROM employees WHERE id=?", (eid,), commit=True)
            self.refresh()

    def export_csv(self):
        filename = filedialog.asksaveasfilename(defaultextension=".csv")
        if not filename: return
        rows = self.db.execute_query("SELECT * FROM employees")
        with open(filename, 'w', newline='') as f:
            csv.writer(f).writerows(rows)
        messagebox.showinfo("Done", "Exported")

class PayrollFrame(ttk.Frame):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        
        header = ttk.Frame(self)
        header.pack(fill="x", padx=20, pady=10)
        ttk.Label(header, text="Salary Slip Generator", style="SubHeader.TLabel").pack(side="left")
        
        # Select Employee
        form = ttk.LabelFrame(self, text="Payroll Details")
        form.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(form, text="Select Employee:").grid(row=0, column=0, padx=5, pady=5)
        self.emp_var = tk.StringVar()
        self.emp_combo = ttk.Combobox(form, textvariable=self.emp_var, state="readonly")
        self.emp_combo.grid(row=0, column=1, padx=5, pady=5)
        self.emp_combo.bind("<Button-1>", self.load_emps) # Refresh on click
        self.emp_combo.bind("<<ComboboxSelected>>", self.on_select)
        
        self.lbl_role = ttk.Label(form, text="Role: -")
        self.lbl_role.grid(row=0, column=2, padx=10)
        
        self.lbl_base = ttk.Label(form, text="Base Salary: ₹ 0")
        self.lbl_base.grid(row=0, column=3, padx=10)
        
        # Month
        ttk.Label(form, text="Month:").grid(row=1, column=0, padx=5, pady=5)
        self.month_str = tk.StringVar(value=date.today().strftime("%B %Y"))
        ttk.Entry(form, textvariable=self.month_str).grid(row=1, column=1, padx=5, pady=5)
        
        # Bonus
        ttk.Label(form, text="Bonus/Incentive:").grid(row=1, column=2, padx=5, pady=5)
        self.bonus_entry = ttk.Entry(form)
        self.bonus_entry.grid(row=1, column=3, padx=5, pady=5)
        self.bonus_entry.insert(0, "0")
        
        # Actions
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=20)
        ttk.Button(btn_frame, text="🖨️ Generate PDF Slip", command=self.generate_pdf_slip).pack(side="left", padx=10)
        
        # Preview
        self.result_label = ttk.Label(self, text="Select an employee to see preview...", font=("Courier", 10), justify="left", background="white", relief="sunken")
        self.result_label.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.emp_map = {}
        self.current_emp_data = None

    def load_emps(self, event=None):
        try:
            rows = self.db.execute_query("SELECT id, name, role, base_salary FROM employees")
            self.emp_map = {r[1]: {'id': r[0], 'role': r[2], 'salary': r[3]} for r in rows}
            self.emp_combo['values'] = list(self.emp_map.keys())
        except:
            pass

    def on_select(self, event):
        name = self.emp_var.get()
        if name in self.emp_map:
            data = self.emp_map[name]
            self.lbl_role.config(text=f"Role: {data['role']}")
            self.lbl_base.config(text=f"Base Salary: ₹ {data['salary']}")
            self.current_emp_data = data
            self.preview_slip()

    def get_totals(self):
        if not self.current_emp_data: return None
        try:
            bonus = float(self.bonus_entry.get())
        except: bonus = 0
        base = self.current_emp_data['salary']
        total = base + bonus
        return base, bonus, total

    def preview_slip(self):
        vals = self.get_totals()
        if not vals: return
        base, bonus, total = vals
        
        slip = f"""
PREVIEW:
--------------------------------
Name:  {self.emp_var.get()}
Role:  {self.current_emp_data['role']}
Month: {self.month_str.get()}

Base:  ₹ {base:,.2f}
Bonus: ₹ {bonus:,.2f}
Total: ₹ {total:,.2f}
--------------------------------
Click 'Generate PDF' to save.
        """
        self.result_label.config(text=slip)

    def generate_pdf_slip(self):
        vals = self.get_totals()
        if not vals:
            messagebox.showerror("Error", "Select Employee first")
            return
            
        base, bonus, total = vals
        name = self.emp_var.get()
        
        slip_data = {
            'name': name,
            'role': self.current_emp_data['role'],
            'month': self.month_str.get(),
            'generated_on': date.today().strftime("%Y-%m-%d"),
            'base': base,
            'bonus': bonus,
            'total': total
        }
        
        try:
            from common.pdf_generator import PDFGenerator
            gen = PDFGenerator(output_dir="payslips")
            path = gen.generate_salary_slip(slip_data)
            
            if messagebox.askyesno("Success", f"Payslip Generated:\n{path}\n\nOpen now?"):
                os.startfile(path)
        except Exception as e:
            messagebox.showerror("Error", f"PDF Error: {e}")
