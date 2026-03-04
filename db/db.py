# ============================================================
# ======================= DATABASE LAYER =====================
# ============================================================
# This module handles all database operations for the OCR app.
#
# Responsibilities:
# - connect to SQLite database
# - initialize tables using schema.sql
# - insert extracted OCR records
# - find compatible records for comparison
# ============================================================


import sqlite3
import json
from datetime import datetime
import os

# project logger
from utils.logging import log, debug, error


# ============================================================
# ===================== PATH CONFIGURATION ===================
# ============================================================
from pathlib import Path

# ensure data directory exists
DATA_DIR = Path("data")
DATA_DIR.mkdir(parents=True, exist_ok=True)

# location of SQLite database file
DB_PATH = DATA_DIR / "ocr_data.db"

# schema file used to create tables
SCHEMA_PATH = Path("db") / "schema.sql"


# ============================================================
# ===================== DATABASE CONNECT =====================
# ============================================================

def connect(db_path=DB_PATH):
    """
    Opens a connection to the SQLite database.
    SQLite automatically creates the file if it does not exist.
    """

    log(f"Connecting to database: {db_path}")

    return sqlite3.connect(str(db_path))


# ============================================================
# ==================== DATABASE INITIALIZATION ===============
# ============================================================

def init_db(conn):
    """
    Executes schema.sql to create required tables.

    This function reads SQL commands from the schema file
    and executes them in the database.
    """

    log("Initializing database schema")

    if not os.path.exists(SCHEMA_PATH):

        error(f"Schema file not found: {SCHEMA_PATH}")

        raise FileNotFoundError(f"Schema file not found: {SCHEMA_PATH}")

    # read SQL schema
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()

    debug("Executing schema SQL", enabled=True)

    # executes multiple SQL statements
    conn.executescript(schema_sql)

    conn.commit()

    log("Database initialized successfully")


# ============================================================
# ====================== INSERT RECORD =======================
# ============================================================

def insert_json_record(conn, template_id, data: dict):
    """
    Inserts OCR extracted data into the database.

    Parameters:
        conn        → database connection
        template_id → which template produced the data
        data        → dictionary of extracted OCR fields
    """

    log(f"Inserting record for template: {template_id}")

    # convert Python dict → JSON string for storage
    json_str = json.dumps(data)

    # UTC timestamp for record creation
    timestamp = datetime.utcnow().isoformat()

    conn.execute(
        """
        INSERT INTO records (template_id, data_json, created_at)
        VALUES (?, ?, ?)
        """,
        (template_id, json_str, timestamp)
    )

    conn.commit()

    debug("Record inserted successfully", enabled=True)


# ============================================================
# ==================== FIND COMPATIBLE RECORD ================
# ============================================================

def find_compatible_record(conn, template_id, data: dict):
    """
    Finds an existing record that has the same field structure.

    Compatibility rule:
    The keys of the JSON object must match exactly
    (order does not matter).

    Example:
        {name, regno, dob}
    matches
        {dob, regno, name}

    Returns:
        record_id if found
        None if no compatible record exists
    """

    log(f"Searching compatible record for template: {template_id}")

    cursor = conn.execute(
        "SELECT id, data_json FROM records WHERE template_id = ?",
        (template_id,)
    )

    # incoming OCR result keys
    incoming_keys = set(data.keys())

    debug(f"Incoming keys: {incoming_keys}", enabled=True)

    for row_id, json_str in cursor.fetchall():

        existing_data = json.loads(json_str)
        existing_keys = set(existing_data.keys())

        debug(f"Checking record {row_id} with keys {existing_keys}", enabled=True)

        # compare sets (order independent)
        if incoming_keys == existing_keys:

            log(f"Compatible record found: {row_id}")

            return row_id

    log("No compatible record found")

    return None