"""Conversation memory store — SQLite-backed persistent memory.

Stores conversation history with metadata for retrieval.
"""

from __future__ import annotations

import json
import logging
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger("memory.store")


@dataclass
class ConversationTurn:
    """A single turn in a conversation."""
    role: str  # 'user' | 'assistant' | 'system'
    content: str
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


@dataclass
class Session:
    """A conversation session."""
    session_id: str
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    title: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class MemoryStore:
    """SQLite-backed conversation memory store."""

    def __init__(self, db_path: str = "./data/memory.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

    @property
    def conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self.db_path))
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
        return self._conn

    def _init_db(self) -> None:
        """Initialize database schema."""
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                title TEXT DEFAULT '',
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                metadata TEXT DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp REAL NOT NULL,
                metadata TEXT DEFAULT '{}',
                FOREIGN KEY (session_id) REFERENCES sessions(session_id)
            );

            CREATE INDEX IF NOT EXISTS idx_messages_session
                ON messages(session_id, timestamp);
        """)
        self.conn.commit()

    # --- Session operations ---

    def create_session(self, session_id: str) -> Session:
        """Create a new conversation session."""
        now = time.time()
        self.conn.execute(
            "INSERT OR IGNORE INTO sessions (session_id, created_at, updated_at) VALUES (?, ?, ?)",
            (session_id, now, now),
        )
        self.conn.commit()
        return Session(session_id=session_id, created_at=now, updated_at=now)

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        row = self.conn.execute(
            "SELECT * FROM sessions WHERE session_id = ?", (session_id,)
        ).fetchone()
        if not row:
            return None
        return Session(
            session_id=row["session_id"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
            title=row["title"],
            metadata=json.loads(row["metadata"]),
        )

    def list_sessions(self, limit: int = 20, offset: int = 0) -> list[Session]:
        """List recent sessions."""
        rows = self.conn.execute(
            "SELECT * FROM sessions ORDER BY updated_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [
            Session(
                session_id=r["session_id"],
                created_at=r["created_at"],
                updated_at=r["updated_at"],
                title=r["title"],
                metadata=json.loads(r["metadata"]),
            )
            for r in rows
        ]

    def delete_session(self, session_id: str) -> bool:
        """Delete a session and all its messages."""
        self.conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        self.conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
        self.conn.commit()
        return self.conn.total_changes > 0

    # --- Message operations ---

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> int:
        """Add a message to a session. Returns message ID."""
        now = time.time()
        cursor = self.conn.execute(
            "INSERT INTO messages (session_id, role, content, timestamp, metadata) VALUES (?, ?, ?, ?, ?)",
            (session_id, role, content, now, json.dumps(metadata or {})),
        )
        # Update session timestamp
        self.conn.execute(
            "UPDATE sessions SET updated_at = ? WHERE session_id = ?",
            (now, session_id),
        )
        self.conn.commit()
        return cursor.lastrowid

    def get_history(
        self,
        session_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ConversationTurn]:
        """Get conversation history for a session."""
        rows = self.conn.execute(
            "SELECT role, content, timestamp, metadata FROM messages "
            "WHERE session_id = ? ORDER BY timestamp ASC LIMIT ? OFFSET ?",
            (session_id, limit, offset),
        ).fetchall()
        return [
            ConversationTurn(
                role=r["role"],
                content=r["content"],
                timestamp=r["timestamp"],
                metadata=json.loads(r["metadata"]),
            )
            for r in rows
        ]

    def search_messages(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Full-text search across all messages."""
        try:
            self.conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(content, session_id)")
        except sqlite3.OperationalError:
            pass  # Table already exists

        # Insert unindexed content
        self.conn.execute(
            "INSERT OR IGNORE INTO messages_fts (rowid, content, session_id) "
            "SELECT id, content, session_id FROM messages WHERE id NOT IN (SELECT rowid FROM messages_fts)"
        )
        self.conn.commit()

        rows = self.conn.execute(
            "SELECT m.id, m.session_id, m.role, m.content, m.timestamp, rank "
            "FROM messages_fts f JOIN messages m ON f.rowid = m.id "
            "WHERE messages_fts MATCH ? ORDER BY rank LIMIT ?",
            (query, limit),
        ).fetchall()

        return [
            {
                "id": r["id"],
                "session_id": r["session_id"],
                "role": r["role"],
                "content": r["content"],
                "timestamp": r["timestamp"],
            }
            for r in rows
        ]

    def clear_session(self, session_id: str) -> None:
        """Clear all messages for a session (keep session)."""
        self.conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
        self.conn.commit()

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
