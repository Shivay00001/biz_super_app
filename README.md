# Biz Super App (Enterprise Edition)

Desktop GUI app (tkinter). Business suite with analytics, billing, HR, inventory, and compliance (GST calendar) modules; SQLite storage (`biz_app.db` is created on first run).

## Run

```bash
python main.py
```

Requires Python 3.10+ with tkinter. Verified boot on Python 3.12 (Linux, xvfb, 2026-09-24) — window initializes with no errors.

Not a web/cloud app: it is a desktop tool. Package with PyInstaller for distribution.
