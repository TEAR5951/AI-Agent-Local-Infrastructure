"""Task scheduler — lightweight cron-style job scheduling.

Supports one-shot, recurring, and cron-expression based scheduling.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sqlite3
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Coroutine, Optional

import re

logger = logging.getLogger("scheduler")


@dataclass
class ScheduledTask:
    """A scheduled task definition."""
    task_id: str
    name: str
    schedule: str  # "30m", "2h", cron expression, or ISO timestamp
    action: str  # "webhook" | "command" | "callback"
    params: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    repeat: int = 0  # 0 = forever
    run_count: int = 0
    last_run: Optional[float] = None
    next_run: Optional[float] = None
    created_at: float = field(default_factory=time.time)


class Scheduler:
    """Lightweight async task scheduler."""

    def __init__(self, db_path: str = "./data/scheduler.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._running = False
        self._task: Optional[asyncio.Task] = None
        self._handlers: dict[str, Callable[..., Coroutine]] = {}
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                schedule TEXT NOT NULL,
                action TEXT NOT NULL,
                params TEXT DEFAULT '{}',
                enabled INTEGER DEFAULT 1,
                repeat INTEGER DEFAULT 0,
                run_count INTEGER DEFAULT 0,
                last_run REAL,
                next_run REAL,
                created_at REAL NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def register_handler(self, action: str, handler: Callable[..., Coroutine]) -> None:
        """Register a coroutine handler for an action type."""
        self._handlers[action] = handler

    def add_task(self, task: ScheduledTask) -> None:
        """Add a task to the database."""
        task.next_run = self._compute_next_run(task.schedule)
        conn = sqlite3.connect(str(self.db_path))
        conn.execute(
            """INSERT OR REPLACE INTO tasks
               (task_id, name, schedule, action, params, enabled, repeat, run_count, last_run, next_run, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                task.task_id, task.name, task.schedule, task.action,
                json.dumps(task.params), int(task.enabled), task.repeat,
                task.run_count, task.last_run, task.next_run, task.created_at,
            ),
        )
        conn.commit()
        conn.close()
        logger.info("Task added: %s (%s)", task.name, task.schedule)

    def remove_task(self, task_id: str) -> bool:
        """Remove a task by ID."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.execute("DELETE FROM tasks WHERE task_id = ?", (task_id,))
        removed = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return removed

    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        """Get a task by ID."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
        conn.close()
        if not row:
            return None
        return self._row_to_task(row)

    def list_tasks(self, enabled_only: bool = False) -> list[ScheduledTask]:
        """List all scheduled tasks."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        query = "SELECT * FROM tasks"
        if enabled_only:
            query += " WHERE enabled = 1"
        query += " ORDER BY next_run ASC"
        rows = conn.execute(query).fetchall()
        conn.close()
        return [self._row_to_task(r) for r in rows]

    def _row_to_task(self, row) -> ScheduledTask:
        return ScheduledTask(
            task_id=row["task_id"],
            name=row["name"],
            schedule=row["schedule"],
            action=row["action"],
            params=json.loads(row["params"]),
            enabled=bool(row["enabled"]),
            repeat=row["repeat"],
            run_count=row["run_count"],
            last_run=row["last_run"],
            next_run=row["next_run"],
            created_at=row["created_at"],
        )

    def _compute_next_run(self, schedule: str) -> float:
        """Compute the next run timestamp from a schedule string."""
        now = datetime.now()

        # Relative: "30m", "2h", "1d"
        rel_match = re.match(r"^(\d+)([mhd])$", schedule)
        if rel_match:
            amount = int(rel_match.group(1))
            unit = rel_match.group(2)
            delta_map = {"m": "minutes", "h": "hours", "d": "days"}
            delta = timedelta(**{delta_map[unit]: amount})
            return (now + delta).timestamp()

        # ISO timestamp
        try:
            return datetime.fromisoformat(schedule).timestamp()
        except ValueError:
            pass

        # Simple cron-like: "HH:MM"
        try:
            parts = schedule.split(":")
            hour, minute = int(parts[0]), int(parts[1])
            next_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_time <= now:
                next_time += timedelta(days=1)
            return next_time.timestamp()
        except (ValueError, IndexError):
            pass

        # Default: run in 1 minute
        logger.warning("Unrecognized schedule format '%s', defaulting to 1m", schedule)
        return (now + timedelta(minutes=1)).timestamp()

    async def start(self, check_interval: int = 30) -> None:
        """Start the scheduler loop."""
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._run_loop(check_interval))
        logger.info("Scheduler started (check interval: %ss)", check_interval)

    async def stop(self) -> None:
        """Stop the scheduler loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        logger.info("Scheduler stopped")

    async def _run_loop(self, check_interval: int) -> None:
        """Main scheduler loop."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row

        try:
            while self._running:
                now = time.time()
                rows = conn.execute(
                    "SELECT * FROM tasks WHERE enabled = 1 AND next_run IS NOT NULL AND next_run <= ?",
                    (now,),
                ).fetchall()

                for row in rows:
                    task = self._row_to_task(row)
                    await self._execute_task(task)
                    self._update_after_run(conn, task)

                await asyncio.sleep(check_interval)
        finally:
            conn.close()

    async def _execute_task(self, task: ScheduledTask) -> None:
        """Execute a single scheduled task."""
        logger.info("Executing task: %s (%s)", task.name, task.action)

        handler = self._handlers.get(task.action)
        if handler:
            try:
                await handler(task)
            except Exception as e:
                logger.exception("Task handler failed: %s", task.task_id)
        else:
            logger.warning("No handler registered for action: %s", task.action)

    def _update_after_run(self, conn, task: ScheduledTask) -> None:
        """Update task state after execution."""
        now = time.time()
        task.run_count += 1
        task.last_run = now

        if task.repeat > 0 and task.run_count >= task.repeat:
            # One-shot: disable after final run
            conn.execute(
                "UPDATE tasks SET run_count = ?, last_run = ?, next_run = NULL, enabled = 0 WHERE task_id = ?",
                (task.run_count, now, task.task_id),
            )
            logger.info("Task completed (final run): %s", task.name)
        else:
            task.next_run = self._compute_next_run(task.schedule)
            conn.execute(
                "UPDATE tasks SET run_count = ?, last_run = ?, next_run = ? WHERE task_id = ?",
                (task.run_count, now, task.next_run, task.task_id),
            )
        conn.commit()
