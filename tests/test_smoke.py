"""Structural smoke test (generated). Verifies modules parse and expose entry points."""
import ast
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))


def test_all_python_files_parse():
    bad = []
    for f in sorted(ROOT.rglob('*.py')):
        if '__pycache__' in f.parts or 'tests' in f.parts:
            continue
        try:
            ast.parse(f.read_text(encoding='utf-8'), filename=str(f))
        except SyntaxError as e:
            bad.append(f"{f}: {e}")
    assert not bad, "\n".join(bad)


def test_db_manager_creates_tables():
    from db.db_manager import DBManager
    with tempfile.TemporaryDirectory() as d:
        db = DBManager(db_path=os.path.join(d, "smoke.db"))
        tables = [t[0] for t in
                  db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")]
        assert tables, "no tables created"
