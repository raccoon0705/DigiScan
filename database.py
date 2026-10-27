"""
Database persistence module for DigiScan.
Lightweight SQLite storage for document analysis history and conversations.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "history.db")


def get_connection():
    """Returns a SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the history database schema if not present."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS document_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_name TEXT NOT NULL,
                analyzed_at TEXT NOT NULL,
                document_text TEXT NOT NULL,
                analysis_json TEXT NOT NULL,
                summary_preview TEXT NOT NULL,
                chat_history TEXT NOT NULL DEFAULT '[]'
            )
            """
        )
        conn.commit()


def save_history(
    document_name: str,
    document_text: str,
    analysis_data: Dict[str, Any],
    chat_history: Optional[List[Dict[str, str]]] = None,
) -> int:
    """
    Saves or updates a document analysis record in SQLite.
    Returns the record ID.
    """
    init_db()
    now_str = datetime.now().strftime("%B %d, %Y • %I:%M %p")
    
    # Generate 1-2 sentence preview from summary points or findings
    summary_preview = ""
    points = analysis_data.get("summary_points", [])
    if points and isinstance(points, list):
        summary_preview = points[0].get("text", "") if isinstance(points[0], dict) else str(points[0])
    if not summary_preview:
        clauses = analysis_data.get("clauses", [])
        if clauses:
            summary_preview = f"Analysis identified {len(clauses)} critical and review-worthy contractual clauses."
        else:
            summary_preview = "Document analyzed successfully."

    chat_json = json.dumps(chat_history or [], ensure_ascii=False)
    analysis_json = json.dumps(analysis_data, ensure_ascii=False)

    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO document_history (
                document_name, analyzed_at, document_text, analysis_json, summary_preview, chat_history
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (document_name, now_str, document_text, analysis_json, summary_preview, chat_json),
        )
        conn.commit()
        return cursor.lastrowid


def update_history_chat(doc_id: int, chat_history: List[Dict[str, str]]):
    """Updates the chat history for an existing analysis record."""
    init_db()
    chat_json = json.dumps(chat_history, ensure_ascii=False)
    with get_connection() as conn:
        conn.execute(
            "UPDATE document_history SET chat_history = ? WHERE id = ?",
            (chat_json, doc_id),
        )
        conn.commit()


def get_all_history() -> List[Dict[str, Any]]:
    """Retrieves all past analyses ordered by newest first."""
    init_db()
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, document_name, analyzed_at, summary_preview FROM document_history ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_history_by_id(doc_id: int) -> Optional[Dict[str, Any]]:
    """Retrieves full document record by ID."""
    init_db()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM document_history WHERE id = ?",
            (doc_id,),
        ).fetchone()
        if not row:
            return None
        data = dict(row)
        try:
            data["analysis_data"] = json.loads(data["analysis_json"])
        except Exception:
            data["analysis_data"] = {}
        try:
            data["chat_history"] = json.loads(data["chat_history"])
        except Exception:
            data["chat_history"] = []
        return data


def delete_history_item(doc_id: int):
    """Removes a single history item."""
    init_db()
    with get_connection() as conn:
        conn.execute("DELETE FROM document_history WHERE id = ?", (doc_id,))
        conn.commit()
