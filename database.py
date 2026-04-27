"""SQLite helpers for storing sent alerts."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone


class AlertDatabase:
    def __init__(self, db_path: str = "alerts.db") -> None:
        self.db_path = db_path
        self._initialize()

    def _initialize(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sent_alerts (
                    opportunity_id TEXT PRIMARY KEY,
                    sport_key TEXT NOT NULL,
                    event_id TEXT NOT NULL,
                    event_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    implied_total REAL NOT NULL,
                    edge_percent REAL NOT NULL,
                    sent_at TEXT NOT NULL
                )
                """
            )

    def was_sent(self, opportunity_id: str) -> bool:
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                "SELECT 1 FROM sent_alerts WHERE opportunity_id = ?",
                (opportunity_id,),
            ).fetchone()
        return row is not None

    def save_alert(
        self,
        opportunity_id: str,
        sport_key: str,
        event_id: str,
        event_name: str,
        start_time: str,
        implied_total: float,
        edge_percent: float,
    ) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO sent_alerts (
                    opportunity_id,
                    sport_key,
                    event_id,
                    event_name,
                    start_time,
                    implied_total,
                    edge_percent,
                    sent_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    opportunity_id,
                    sport_key,
                    event_id,
                    event_name,
                    start_time,
                    implied_total,
                    edge_percent,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
