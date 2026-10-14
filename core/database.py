"""SQLite persistence. User-specific records are always queried by user_id."""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "careerai.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db() -> None:
    with get_connection() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE COLLATE NOCASE,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resume_name TEXT NOT NULL,
            resume_text TEXT NOT NULL,
            extracted_json TEXT NOT NULL,
            results_json TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE INDEX IF NOT EXISTS idx_analyses_user_created ON analyses(user_id, created_at DESC);
        """)

def create_user(email: str, full_name: str, password_hash: str) -> int:
    with get_connection() as conn:
        cur = conn.execute("INSERT INTO users(email, full_name, password_hash) VALUES (?, ?, ?)",
                           (email.strip().lower(), full_name.strip(), password_hash))
        return int(cur.lastrowid)

def get_user_by_email(email: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),)).fetchone()
        return dict(row) if row else None

def save_analysis(user_id: int, resume_name: str, resume_text: str,
                  extracted: dict[str, Any], results: dict[str, Any]) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO analyses(user_id, resume_name, resume_text, extracted_json, results_json) VALUES (?, ?, ?, ?, ?)",
            (user_id, resume_name, resume_text, json.dumps(extracted), json.dumps(results)))
        return int(cur.lastrowid)

def list_analyses(user_id: int) -> list[dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute("SELECT id, resume_name, created_at FROM analyses WHERE user_id = ? ORDER BY created_at DESC, id DESC", (user_id,)).fetchall()
        return [dict(r) for r in rows]

def get_analysis(user_id: int, analysis_id: int) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM analyses WHERE id = ? AND user_id = ?", (analysis_id, user_id)).fetchone()
        if not row:
            return None
        result = dict(row)
        result["extracted"] = json.loads(result.pop("extracted_json"))
        result["results"] = json.loads(result.pop("results_json"))
        return result

def delete_analysis(user_id: int, analysis_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.execute("DELETE FROM analyses WHERE id = ? AND user_id = ?", (analysis_id, user_id))
        return cur.rowcount > 0
