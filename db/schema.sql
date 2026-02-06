
-- Companies & Users
CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT,
    gstin TEXT,
    phone TEXT,
    email TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL, -- Simplify for prototype
    role TEXT DEFAULT 'admin', -- admin, accountant, viewer
    company_id INTEGER,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);

-- Masters
CREATE TABLE IF NOT EXISTS parties (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT, -- 'customer', 'supplier'
    gstin TEXT,
    phone TEXT,
    email TEXT,
    address TEXT,
    company_id INTEGER,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sku TEXT,
    unit TEXT DEFAULT 'pcs',
    price REAL DEFAULT 0.0,
    stock_quantity REAL DEFAULT 0.0,
    tax_rate REAL DEFAULT 0.0,
    hsn_code TEXT,
    company_id INTEGER,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);

-- Invoices
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT NOT NULL,
    party_id INTEGER,
    date DATE,
    total_amount REAL,
    status TEXT DEFAULT 'draft', -- draft, final, paid, cancelled
    company_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(party_id) REFERENCES parties(id),
    FOREIGN KEY(company_id) REFERENCES companies(id)
);

CREATE TABLE IF NOT EXISTS invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    item_id INTEGER,
    quantity REAL,
    rate REAL,
    tax_amount REAL,
    total REAL,
    FOREIGN KEY(invoice_id) REFERENCES invoices(id),
    FOREIGN KEY(item_id) REFERENCES items(id)
);

-- Documents
CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    doc_type TEXT, -- invoice, bill, receipt, contract
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tags TEXT,
    company_id INTEGER,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);

-- Approvals
CREATE TABLE IF NOT EXISTS approval_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module TEXT,
    reference_id INTEGER,
    status TEXT DEFAULT 'pending', -- pending, approved, rejected
    requested_by INTEGER,
    approved_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(requested_by) REFERENCES users(id),
    FOREIGN KEY(approved_by) REFERENCES users(id)
);

-- HR & Payroll (Missing previously)
CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    role TEXT,
    base_salary REAL,
    company_id INTEGER,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);

-- Compliance (Missing previously)
CREATE TABLE IF NOT EXISTS compliance_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    due_date DATE,
    status TEXT DEFAULT 'pending', -- pending, done
    company_id INTEGER,
    FOREIGN KEY(company_id) REFERENCES companies(id)
);
