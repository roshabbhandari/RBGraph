import json
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

from core.models import Diagram


DB_PATH = Path(__file__).resolve().parent / "rbgraph.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA foreign_keys=ON")
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS diagrams (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, diagram_type TEXT NOT NULL, payload TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
        )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS idx_diagrams_created_at ON diagrams(created_at DESC)"
        )


def save_diagram(diagram: Diagram) -> int:
    payload = json.dumps(diagram.model_dump(mode="json"))
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO diagrams (name, diagram_type, payload) VALUES (?, ?, ?)",
            (diagram.name, diagram.diagram_type.value, payload),
        )
        return int(cursor.lastrowid)


def list_diagrams(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    if not 1 <= limit <= 200:
        raise ValueError("History limit must be between 1 and 200.")
    if offset < 0:
        raise ValueError("History offset cannot be negative.")

    with get_connection() as connection:
        rows = connection.execute(
            "SELECT id, name, diagram_type, created_at FROM diagrams ORDER BY id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [dict(row) for row in rows]


def get_saved_diagram(diagram_id: int) -> Optional[Diagram]:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT payload FROM diagrams WHERE id = ?",
            (diagram_id,),
        ).fetchone()
    if not row:
        return None
    return Diagram.model_validate(json.loads(row["payload"]))


def delete_diagram(diagram_id: int) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            "DELETE FROM diagrams WHERE id = ?",
            (diagram_id,),
        )
        return cursor.rowcount > 0
