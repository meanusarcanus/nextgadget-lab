"""
database.py - SQLite state & tracking store for @nextgadget.lab pipeline.
Ensures zero duplicate gadget reviews and tracks link-in-bio products.
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, Set

logger = logging.getLogger("nextgadget_lab.database")

DB_PATH = "gadgets.db"


class GadgetDatabase:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initialize database schema if tables do not exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Table for gadget metadata & processing state
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS gadgets (
                    asin TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    rating REAL NOT NULL,
                    review_count INTEGER NOT NULL,
                    price TEXT,
                    image_url TEXT,
                    affiliate_url TEXT NOT NULL,
                    pros TEXT,
                    cons TEXT,
                    specs TEXT,
                    processed_at TEXT NOT NULL,
                    published_to_instagram INTEGER DEFAULT 0,
                    instagram_container_id TEXT,
                    published_at TEXT
                )
            """)

            # Table for Instagram post history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS post_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    asin TEXT NOT NULL,
                    hook TEXT NOT NULL,
                    caption TEXT NOT NULL,
                    slides_json TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (asin) REFERENCES gadgets (asin)
                )
            """)

            conn.commit()
            logger.info("Database initialized successfully.")

    def is_asin_processed(self, asin: str) -> bool:
        """Check if an ASIN has already been processed/reviewed."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM gadgets WHERE asin = ?", (asin.strip(),))
            return cursor.fetchone() is not None

    def get_processed_asins(self) -> Set[str]:
        """Return set of all processed ASINs."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT asin FROM gadgets")
            return {row["asin"] for row in cursor.fetchall()}

    def save_gadget(self, gadget: Dict[str, Any]) -> bool:
        """Save a new gadget item to database."""
        if self.is_asin_processed(gadget["asin"]):
            logger.warning(f"ASIN {gadget['asin']} already exists in database. Skipping insert.")
            return False

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO gadgets (
                    asin, title, category, rating, review_count, price,
                    image_url, affiliate_url, pros, cons, specs,
                    processed_at, published_to_instagram, instagram_container_id, published_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                gadget["asin"],
                gadget["title"],
                gadget.get("category", "Tech"),
                gadget.get("rating", 4.5),
                gadget.get("review_count", 250),
                gadget.get("price", "$99.99"),
                gadget.get("image_url", ""),
                gadget["affiliate_url"],
                json.dumps(gadget.get("pros", [])),
                gadget.get("cons", ""),
                json.dumps(gadget.get("specs", {})),
                datetime.utcnow().isoformat(),
                1 if gadget.get("published", False) else 0,
                gadget.get("instagram_container_id"),
                datetime.utcnow().isoformat() if gadget.get("published", False) else None
            ))
            conn.commit()
            logger.info(f"Saved gadget {gadget['asin']} - {gadget['title']} to database.")
            return True

    def mark_gadget_published(self, asin: str, container_id: Optional[str] = None):
        """Mark a gadget as successfully published to Instagram."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.utcnow().isoformat()
            cursor.execute("""
                UPDATE gadgets
                SET published_to_instagram = 1,
                    instagram_container_id = ?,
                    published_at = ?
                WHERE asin = ?
            """, (container_id, now, asin))
            conn.commit()
            logger.info(f"Marked ASIN {asin} as published to Instagram (Container: {container_id}).")

    def record_post(self, asin: str, hook: str, caption: str, slides: List[str], status: str = "PUBLISHED"):
        """Record an Instagram post entry into post_history."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO post_history (asin, hook, caption, slides_json, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (asin, hook, caption, json.dumps(slides), status, datetime.utcnow().isoformat()))
            conn.commit()

    def get_published_gadgets(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetch published gadgets for Link-in-Bio hub generation."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM gadgets
                ORDER BY datetime(published_at) DESC, datetime(processed_at) DESC
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            results = []
            for row in rows:
                item = dict(row)
                item["pros"] = json.loads(item["pros"]) if item["pros"] else []
                item["specs"] = json.loads(item["specs"]) if item["specs"] else {}
                results.append(item)
            return results
