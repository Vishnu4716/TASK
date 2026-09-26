import sqlite3
from datetime import datetime, timezone
import json

from config import DB_PATH


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = connect()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS requests (
            request_id TEXT PRIMARY KEY,
            rider_name TEXT,
            rider_tier TEXT,
            trip_id TEXT,
            submitted_at TEXT,
            request_text TEXT,
            interpreted_json TEXT,
            status TEXT DEFAULT 'PENDING',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS decisions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT NOT NULL,
            supported INTEGER,
            auto_resolve INTEGER,
            resolution_type TEXT,
            amount REAL,
            rationale TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS actions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT NOT NULL,
            action_type TEXT NOT NULL,
            amount REAL,
            status TEXT NOT NULL,
            details TEXT,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS overrides (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id TEXT NOT NULL,
            reviewer TEXT NOT NULL,
            new_status TEXT NOT NULL,
            note TEXT,
            created_at TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()


def now():
    return datetime.now(timezone.utc).isoformat()


def save_request(request_row, interpreted):
    conn = connect()
    conn.execute(
        """INSERT OR REPLACE INTO requests
        (request_id, rider_name, rider_tier, trip_id, submitted_at,
         request_text, interpreted_json, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            request_row["request_id"],
            request_row["rider_name"],
            request_row["rider_tier"],
            request_row["trip_id"],
            request_row["submitted_at"],
            request_row["request_text"],
            json.dumps(interpreted),
            "PROCESSED",
            now(),
        ),
    )
    conn.commit()
    conn.close()


def save_decision(request_id, supported, auto_resolve,
                  resolution_type, amount, rationale):
    conn = connect()
    conn.execute(
        """INSERT INTO decisions
        (request_id, supported, auto_resolve, resolution_type, amount, rationale, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            request_id, int(supported), int(auto_resolve),
            resolution_type, amount, rationale, now()
        ),
    )
    conn.commit()
    conn.close()


def save_action(request_id, action_type, amount, status, details):
    conn = connect()
    conn.execute(
        """INSERT INTO actions
        (request_id, action_type, amount, status, details, created_at)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (request_id, action_type, amount, status, details, now()),
    )
    conn.commit()
    conn.close()


def save_override(request_id, reviewer, new_status, note):
    conn = connect()
    conn.execute(
        """INSERT INTO overrides
        (request_id, reviewer, new_status, note, created_at)
        VALUES (?, ?, ?, ?, ?)""",
        (request_id, reviewer, new_status, note, now()),
    )
    conn.commit()
    conn.close()


def get_history():
    conn = connect()
    rows = conn.execute(
        """SELECT r.request_id, r.rider_name, r.trip_id, r.status,
                  d.supported, d.auto_resolve, d.resolution_type,
                  d.amount, d.rationale, a.action_type, a.status AS action_status
           FROM requests r
           LEFT JOIN decisions d ON r.request_id = d.request_id
           LEFT JOIN actions a ON r.request_id = a.request_id
           ORDER BY r.created_at DESC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def action_exists(request_id, action_type):
    conn = connect()

    row = conn.execute(
        """
        SELECT 1
        FROM actions
        WHERE request_id = ?
          AND action_type = ?
          AND status IN ('EXECUTED', 'SCHEDULED')
        LIMIT 1
        """,
        (request_id, action_type),
    ).fetchone()
    conn.close()
    return row is not None
