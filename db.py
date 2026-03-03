# db.py
import sqlite3
import json
from datetime import datetime

def connect(db_path="ocr_data.db"):
    return sqlite3.connect(db_path)

def init_db(conn):
    conn.execute("""
    CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        template_id TEXT,
        data_json TEXT,
        created_at TEXT
    )
    """)
    conn.commit()

def insert_json_record(conn, template_id, data: dict):
    json_str = json.dumps(data)
    timestamp = datetime.utcnow().isoformat()

    conn.execute(
        "INSERT INTO records (template_id, data_json, created_at) VALUES (?, ?, ?)",
        (template_id, json_str, timestamp)
    )
    conn.commit()

def find_compatible_record(conn, template_id, data: dict):
    """
    Returns record ID if an existing row has the same keys (order independent)
    """
    cursor = conn.execute(
        "SELECT id, data_json FROM records WHERE template_id = ?",
        (template_id,)
    )

    incoming_keys = set(data.keys())

    for row_id, json_str in cursor.fetchall():
        existing_data = json.loads(json_str)
        existing_keys = set(existing_data.keys())

        if incoming_keys == existing_keys:
            return row_id

    return None