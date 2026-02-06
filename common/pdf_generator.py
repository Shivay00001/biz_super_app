from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import os

class PDFGenerator:
    def __init__(self, output_dir="invoices"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_invoice(self, invoice_data, items, output_filename=None):
        if not output_filename:
            output_filename = f"{invoice_data['number']}.pdf"
        
        filepath = os.path.join(self.output_dir, output_filename)
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        
        # --- Header ---
        c.setFont("Helvetica-Bold", 20)
        c.drawString(50, height - 50, "BizSuperApp Demo Company")
        
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 70, "123, Tech Street, Bangalore, KA - 560001")
        c.drawString(50, height - 85, "GSTIN: 29AAAAA0000A1Z5 | Phone: 9876543210")
        
        c.setFont("Helvetica-Bold", 16)
        c.drawRightString(width - 50, height - 50, "TAX INVOICE")
        
        # --- Bill To & Invoice Details ---
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, height - 120, "Bill To:")
        c.setFont("Helvetica", 10)
        c.drawString(50, height - 135, invoice_data['party_name'])
        c.drawString(50, height - 150, f"Phone: {invoice_data.get('party_phone', 'N/A')}")
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(350, height - 120, "Invoice Details:")
        c.setFont("Helvetica", 10)
        c.drawString(350, height - 135, f"Invoice No: {invoice_data['number']}")
        c.drawString(350, height - 150, f"Date: {invoice_data['date']}")
        
        # --- Items Table ---
        # Data preparation
        data = [['Item', 'Qty', 'Rate', 'Tax %', 'Total']]
        for item in items:
            data.append([
                item['name'],
                str(item['qty']),
                f"₹ {item['rate']:.2f}",
                # Mock tax for now, logic could be passed
                str(item.get('tax', '18%')), 
                f"₹ {item['total']:.2f}"
            ])
            
        # Total Row
        data.append(['', '', '', 'Grand Total:', f"₹ {invoice_data['total_amount']:.2f}"])
        
        # Style
        table = Table(data, colWidths=[200, 50, 80, 60, 100])
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -2), 1, colors.black),
            ('LINEBELOW', (0, -1), (-1, -1), 2, colors.black),
        ])
        table.setStyle(style)
        
        # Draw Table
        table.wrapOn(c, width, height)
        table.drawOn(c, 50, height - 200 - (len(data) * 20))
        
        # --- Footer ---
        y_pos = height - 200 - (len(data) * 20) - 50
        c.setFont("Helvetica", 8)
        c.drawString(50, y_pos, "Terms & Conditions:")
        c.drawString(50, y_pos - 15, "1. Goods once sold will not be taken back.")
        c.drawString(50, y_pos - 30, "2. Interest @ 18% p.a. will be charged if not paid within due date.")
        
        c.setFont("Helvetica-Bold", 10)
        c.drawRightString(width - 50, y_pos - 30, "For BizSuperApp Demo Company")
        c.drawString(width - 150, y_pos - 60, "Authorized Signatory")
        
        c.save()
        return filepath

    def generate_salary_slip(self, slip_data):
        """
        Generates a PDF salary slip.
        slip_data: dict with keys 'name', 'role', 'month', 'base', 'bonus', 'total'
        """
        filename = f"Payslip_{slip_data['name']}_{slip_data['month']}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        c = canvas.Canvas(filepath, pagesize=A4)
        width, height = A4
        
        # Header
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(width/2, height - 50, "BIZSUPERAPP DEMO COMPANY")
        c.setFont("Helvetica", 10)
        c.drawCentredString(width/2, height - 70, "123, Tech Street, Bangalore, KA")
        
        c.setLineWidth(1)
        c.line(50, height - 90, width - 50, height - 90)
        
        # Title
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(width/2, height - 120, f"PAYSLIP FOR {slip_data['month'].upper()}")
        
        # Employee Details Box
        c.rect(50, height - 220, width - 100, 80)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(70, height - 160, f"Employee Name: {slip_data['name']}")
        c.drawString(70, height - 190, f"Designation: {slip_data['role']}")
        
        c.drawString(350, height - 160, f"Pay Period: {slip_data['month']}")
        c.drawString(350, height - 190, f"Generated On: {slip_data['generated_on']}")
        
        # Earnings Table
        data = [
            ['EARNINGS', 'AMOUNT (INR)', 'DEDUCTIONS', 'AMOUNT (INR)'],
            ['Basic Salary', f"{slip_data['base']:,.2f}", 'PF', '0.00'],
            ['Allowance', '0.00', 'Tax (TDS)', '0.00'],
            ['Bonus', f"{slip_data['bonus']:,.2f}", '', ''],
            ['', '', '', ''],
            ['Gross Earnings', f"{slip_data['total']:,.2f}", 'Total Deductions', '0.00']
        ]
        
        table = Table(data, colWidths=[150, 100, 150, 100])
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'), # Total Row
        ])
        table.setStyle(style)
        
        table.wrapOn(c, width, height)
        table.drawOn(c, 50, height - 400)
        
        # Net Pay
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 450, f"NET PAYABLE: ₹ {slip_data['total']:,.2f}")
        c.setFont("Helvetica-Oblique", 10)
        # Placeholder for number to words
        c.drawString(50, height - 470, "(Indian Rupees Only)") 
        
        # Footer
        c.setFont("Helvetica", 8)
        c.drawCentredString(width/2, 50, "This is a computer-generated payslip and does not require a signature.")
        
        c.save()
        return filepath
