import sqlite3
from db.paths import DB_DIR


class DBClass():
    def __init__(self):

        self.conn = sqlite3.connect(DB_DIR)
        self.cur = self.conn.cursor()

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            barcode TEXT PRIMARY KEY,
            name TEXT,
            category TEXT,
            quantity INTEGER DEFAULT 0,
            created_at TEXT
        )
        """)

        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode TEXT,
            action TEXT,
            qty INTEGER,
            timestamp TEXT
        )
        """)
        self.conn.commit()
        self.ensure_item_columns()

    def reset_db(self):
        self.cur.execute("DELETE FROM items")
        self.cur.execute("DELETE FROM sqlite_sequence WHERE name='items'")
        self.conn.commit()

    def ensure_item_columns(self):
        self.cur.execute("PRAGMA table_info(items)")
        existing_columns = [col[1] for col in self.cur.fetchall()]

        if "price" not in existing_columns:
            self.cur.execute("ALTER TABLE items ADD COLUMN price REAL DEFAULT 0")

        if "description" not in existing_columns:
            self.cur.execute("ALTER TABLE items ADD COLUMN description TEXT")

        self.conn.commit()
