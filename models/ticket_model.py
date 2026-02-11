
class TicketModel:
    def __init__(self):
        self.items = {}
        self.listeners = []

    def subscribe(self, callback):
        self.listeners.append(callback)

    def notify(self):
        for cb in self.listeners:
            cb(self.items)

    def add_item(self, item, qty=1):
        item_id = item["id"]

        if item_id in self.items:
            self.items[item_id]["qty"] += qty
        else:
            self.items[item_id] = {
                "item": item,
                "qty": qty
            }

        self.notify()

    def clear(self):
        self.items.clear()
        self.notify()

    def total(self):
        return sum(
            e["item"]["price"] * e["qty"]
            for e in self.items.values()
        )
