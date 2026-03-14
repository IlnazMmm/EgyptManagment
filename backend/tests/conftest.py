import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Lightweight psycopg stub so unit tests can import db.py without real dependency.
if "psycopg" not in sys.modules:
    psycopg_stub = types.ModuleType("psycopg")
    psycopg_rows_stub = types.ModuleType("psycopg.rows")

    def _connect(*args, **kwargs):
        raise RuntimeError("psycopg connect should not be used in unit tests")

    psycopg_stub.connect = _connect
    psycopg_rows_stub.dict_row = object()

    sys.modules["psycopg"] = psycopg_stub
    sys.modules["psycopg.rows"] = psycopg_rows_stub
