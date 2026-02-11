import csv
from datetime import datetime

BARCODE_CATEGORY_PREFIX = {
    "Electrical": "E",
    "Mechanical": "M",
    "Consumable": "C",
    "Tooling": "T"
}

class InventoryRepository:
    def __init__(self, db):
        self.db = db
        self.cur = db.cur
        self.conn = db.conn


    # self
    def get_next_product_code(self):
        """
        Returns the next incremental product code (0001, 0002, ...)
        based on existing barcodes.
        """
        self.cur.execute("""
            SELECT barcode
            FROM items
            ORDER BY barcode DESC
            LIMIT 1
        """)
        row = self.cur.fetchone()

        if not row:
            return 1  # first product

        last_barcode = row[0]
        last_code = int(last_barcode[-3:])  # last 4 digits
        return last_code + 1


    # self
    def generate_barcode(self, barcode_category: str) -> str:
        prefix = BARCODE_CATEGORY_PREFIX.get(barcode_category)

        if not prefix:
            raise ValueError(f"No prefix for barcode category: {barcode_category}")

        now = datetime.now()
        date_part = now.strftime("%y%m%d")
        time_part = now.strftime("%H%M")

        product_code = self.get_next_product_code()
        product_part = f"{product_code:03d}"

        return f"{prefix}{date_part}{time_part}{product_part}"


    # main_window.py
    def get_all_items(self):
        self.cur.execute("""
            SELECT barcode, name, category, quantity, created_at, price, description
            FROM items
            ORDER BY name
        """)
        return self.cur.fetchall()


    # scan_window.py
    def get_item_by_barcode(self, barcode):

        row = self.cur.execute(
            "SELECT barcode, name, category, quantity, price, description FROM items WHERE barcode=?",
            (barcode,)
        ).fetchone()

        if not row:
            return None

        barcode, name, cat, qty, price, desc = row

        return {
            "id": barcode,
            "name": name,
            "category": cat,
            "stock": qty,
            "price": price,
            "description": desc
        }
    

    # transaction_window.py
    def get_transactions(self):
        self.cur.execute("""
            SELECT
                items.name,
                items.barcode,
                transactions.action,
                transactions.qty,
                transactions.timestamp
            FROM transactions
            JOIN items ON items.barcode = transactions.barcode
            ORDER BY transactions.timestamp DESC
        """)
        return self.cur.fetchall()
    
    def get_transactions_filtered(self, search=None, date_from=None, date_to=None):
        query = """
            SELECT
                items.name,
                items.barcode,
                transactions.action,
                transactions.qty,
                transactions.timestamp
            FROM transactions
            JOIN items ON items.barcode = transactions.barcode
            WHERE 1=1
        """
        params = []

        if search:
            query += " AND (items.name LIKE ? OR items.barcode LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])

        if date_from:
            query += " AND DATE(transactions.timestamp) >= ?"
            params.append(date_from)

        if date_to:
            query += " AND DATE(transactions.timestamp) <= ?"
            params.append(date_to)

        query += " ORDER BY transactions.timestamp DESC"

        self.cur.execute(query, params)
        return self.cur.fetchall()
    

    def record_transaction(self, barcode, action, qty):
        self.cur.execute("""
            INSERT INTO transactions (barcode, action, qty, timestamp)
            VALUES (?, ?, ?, ?)
        """, (
            barcode,
            action,                  # "STOCK_IN" or "STOCK_OUT"
            qty,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        self.conn.commit()


    def record_product_stock_in(self, barcode, qty):
        # get current stock
        self.cur.execute("SELECT quantity FROM items WHERE barcode=?", (barcode,))
        current_qty = self.cur.fetchone()[0]

        new_qty = current_qty + qty
        self.update_stock(barcode, new_qty)

        self.record_transaction(barcode, "IN", qty)


    def record_product_stock_out(self, barcode, qty):
        self.cur.execute("SELECT quantity FROM items WHERE barcode=?", (barcode,))
        current_qty = self.cur.fetchone()[0]

        if qty > current_qty:
            raise ValueError("Not enough stock")

        new_qty = current_qty - qty
        self.update_stock(barcode, new_qty)

        self.record_transaction(barcode, "OUT", qty)


    def export_transactions_to_csv(self, filepath):
        rows = self.get_transactions()

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Product Name",
                "Barcode",
                "Action",
                "Quantity",
                "Timestamp"
            ])
            writer.writerows(rows)


    # scan_window.py
    # self
    def update_stock(self, barcode, qty):
        self.cur.execute("UPDATE items SET quantity=? WHERE barcode=?", (qty, barcode))
        self.conn.commit()


    # add_product_window.py
    def create_item(self, name, product_category, barcode_category, price=0, description=""):
        
        barcode = self.generate_barcode(barcode_category)

        self.cur.execute("""
            INSERT INTO items (barcode, name, category, quantity, created_at, price, description)
            VALUES (?, ?, ?, 0, ?, ?, ?)
        """, (
            barcode,
            name,
            product_category,
            datetime.now().isoformat(),
            price,
            description
        ))

        self.conn.commit()
        print(f"\nnewly added barcode: {barcode}\n")
        return barcode

    

    



































    """                         operations.py                         """

    # def update_quantity(self, barcode, new_qty):
    #     self.cur.execute("""
    #         UPDATE items SET quantity=? WHERE barcode=?
    #     """, (new_qty, barcode))

    # def count_items(self):
    #     self.cur.execute("SELECT COUNT(*) FROM items")
    #     return self.cur.fetchone()[0]

    # def record_transaction(self, barcode, action, qty):
    #     self.cur.execute("""
    #         INSERT INTO transactions (barcode, action, qty, timestamp)
    #         VALUES (?, ?, ?, ?)
    #     """, (barcode, action, qty, datetime.now().isoformat()))
    #     self.conn.commit()


    """                         db_window.py                         """

    # def update_item(self, barcode, data):
    #     self.cur.execute("""
    #         UPDATE items
    #         SET name=?, category=?, price=?, description=?
    #         WHERE barcode=?
    #     """, (
    #         data["name"],
    #         data["category"],
    #         data["price"],
    #         data["description"],
    #         barcode
    #     ))
    #     self.conn.commit()

    # def get_item_full(self, barcode):
    #     self.cur.execute("""
    #         SELECT barcode, name, category, quantity, price, description
    #         FROM items
    #         WHERE barcode=?
    #     """, (barcode,))
    #     row = self.cur.fetchone()

    #     return {
    #         "barcode": row[0],
    #         "name": row[1],
    #         "category": row[2],
    #         "quantity": row[3],
    #         "price": row[4],
    #         "description": row[5]
    #     }

    


    """                         discarded                            """    

    # def get_items_by_category(self, category):
    #     self.cur.execute("""
    #         SELECT barcode, name, category, quantity, created_at, price, description
    #         FROM items
    #         WHERE category = ?
    #         ORDER BY name
    #     """, (category,))
    #     return self.cur.fetchall()