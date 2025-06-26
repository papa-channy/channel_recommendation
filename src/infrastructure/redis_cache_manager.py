import sqlite3
from typing import List

class CacheManager:
    def __init__(self, db_path: str = 'cache.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS labels_cache (content_hash TEXT PRIMARY KEY, labels TEXT)"
        )

    def get_labels(self, content_hash: str) -> List[str] | None:
        cur = self.conn.execute("SELECT labels FROM labels_cache WHERE content_hash=?", (content_hash,))
        row = cur.fetchone()
        if row:
            return row[0].split(',')
        return None

    def save_labels(self, content_hash: str, labels: List[str]) -> None:
        labels_str = ','.join(labels)
        self.conn.execute(
            "INSERT OR REPLACE INTO labels_cache(content_hash, labels) VALUES (?, ?)",
            (content_hash, labels_str),
        )
        self.conn.commit()
