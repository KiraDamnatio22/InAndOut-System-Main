import customtkinter as ctk
import tkinter.font as tkfont
from tkinter import ttk, filedialog
from tkcalendar import DateEntry
from datetime import date, datetime, timedelta
import csv

class TransactionHistoryWindow(ctk.CTkToplevel):
    def __init__(self, master, repo):
        super().__init__(master)

        self.title("Transaction History")
        self.geometry("1360x575+0+100")
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # toplevel window key bindings
        self.bind("<Escape>", lambda e: self.on_close())

        # important global variables
        self.repo = repo
        self.sort_reverse = {}
        self.last_row_count = 0
        self.exporting = False
        self.tooltip = None
        self.use_date_filter = False
        self.relative_time_var = ctk.BooleanVar(value=False)
        self.search_var = ctk.StringVar()

        # ---------------- Header ----------------
        ctk.CTkLabel(
            self,
            text="Transaction History",
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(pady=(15, 5))

        # ---------------- Filters ----------------
        filter_frame = ctk.CTkFrame(self)
        filter_frame.pack(fill="x", padx=20, pady=5)

        self.date_indicator = ctk.CTkLabel(
            self,
            text="Date Filter: OFF",
            text_color="gray",
            font=ctk.CTkFont(family="Poppins", size=15),
        )
        self.date_indicator.pack(anchor="center", padx=(0, 0), pady=(5, 0))

        ctk.CTkSwitch(
            self,
            text="Relative Time",
            font=ctk.CTkFont(family="Poppins", size=14),
            variable=self.relative_time_var,
            command=self.load_transactions
        ).pack(anchor="center", padx=(0, 0), pady=(5, 10))

        self.search_var.trace_add("write", lambda *_: self.load_transactions())
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            textvariable=self.search_var,
            width=320
        )
        self.search_entry.pack(side="left", padx=10, pady=10)
        self.after(100, self.search_entry.focus_set)

        self.date_from = DateEntry(
            filter_frame,
            date_pattern="yyyy-mm-dd",
            width=12
        )
        self.date_from.pack(side="left", padx=5)

        ctk.CTkLabel(filter_frame, text="to").pack(side="left")

        self.date_to = DateEntry(
            filter_frame,
            date_pattern="yyyy-mm-dd",
            width=12
        )
        self.date_to.pack(side="left", padx=5)

        self.date_from.bind("<<DateEntrySelected>>", self.enable_date_filter)
        self.date_to.bind("<<DateEntrySelected>>", self.enable_date_filter)

        ctk.CTkButton(
            filter_frame,
            text="Clear Filters",
            width=110,
            command=self.clear_filters
        ).pack(side="left", padx=10)

        self.preset_buttons = {}

        self.preset_buttons["today"] = ctk.CTkButton(
            filter_frame, text="Today", width=80,
            command=self.preset_today
        )
        self.preset_buttons["today"].pack(side="left", padx=5)

        self.preset_buttons["7days"] = ctk.CTkButton(
            filter_frame, text="Last 7 Days", width=110,
            command=self.preset_last_7_days
        )
        self.preset_buttons["7days"].pack(side="left", padx=5)

        self.preset_buttons["month"] = ctk.CTkButton(
            filter_frame, text="This Month", width=110,
            command=self.preset_this_month
        )
        self.preset_buttons["month"].pack(side="left", padx=(5, 0))

        ctk.CTkButton(
            filter_frame,
            text="Export ALL CSV",
            width=130,
            command=self.export_all_csv
        ).pack(side="right", padx=(5, 10))

        ctk.CTkButton(
            filter_frame,
            text="Export FILTERED CSV",
            width=160,
            command=self.export_filtered_csv
        ).pack(side="right", padx=(10, 0))

        # ---------------- Table ----------------
        table_frame = ctk.CTkFrame(self)
        table_frame.pack(fill="both", expand=True, padx=20, pady=10)

        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            table_frame,
            columns=("name", "barcode", "action", "qty", "timestamp"),
            show="headings",
            yscrollcommand=scrollbar.set,
            style="Custom.Treeview"
        )

        scrollbar.config(command=self.tree.yview)
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Double-1>", self.show_transaction_details)

        if hasattr(master, "_last_transaction_filter"):
            self._saved_filter = master._last_transaction_filter
            self.restore_filter_state()

        self.apply_theme()
        self.setup_columns()

        self.load_transactions()

        self.last_row_count = len(self.tree.get_children())
        self.auto_refresh()

        # today_str = date.today().strftime("%Y-%m-%d")
        today_str = date.today().strftime("%m/%d/%Y")
        print(today_str)


    def on_close(self):
        self.save_filter_state()
        self.master._last_transaction_filter = self._saved_filter

        self.grab_release()
        self.destroy()

    # ---------------- Setup ----------------
    def setup_columns(self):
        columns = {
            "name": ("Product Name", 250),
            "barcode": ("Barcode", 170),
            "action": ("Action", 80),
            "qty": ("Quantity", 80),
            "timestamp": ("Timestamp", 230),
        }

        for col, (text, width) in columns.items():
            self.tree.heading(col, text=text, command=lambda c=col: self.sort_by_column(c))
            self.tree.column(col, width=width, anchor="center")
            self.sort_reverse[col] = False


    def apply_theme(self):
        style = ttk.Style()

        # Enable heading font customization
        style.layout(
            "Custom.Treeview.Heading",
            [
                ("Treeheading.cell", {"sticky": "nswe"}),
                ("Treeheading.border", {"sticky": "nswe", "children": [
                    ("Treeheading.padding", {"sticky": "nswe", "children": [
                        ("Treeheading.text", {"sticky": "nswe"})
                    ]})
                ]})
            ]
        )

        if ctk.get_appearance_mode() == "Dark":
            style.configure(
                "Custom.Treeview",
                background="#1e1e1e",
                foreground="white",
                fieldbackground="#1e1e1e",
                rowheight=32,
                font=("Poppins", 12)
            )
            style.configure(
                "Custom.Treeview.Heading",
                background="#333333",
                foreground="white",
                font=("Poppins", 13, "bold")
            )
        else:
            style.configure(
                "Custom.Treeview",
                background="white",
                foreground="black",
                fieldbackground="white",
                rowheight=40,
                font=("Poppins", 10)
            )
            style.configure(
                "Custom.Treeview.Heading",
                background="#F1F1F1",
                foreground="#01AD6B",
                font=("Poppins", 10, "bold"),
                padding=(10, 16)
            )


    # ---------------- Data ----------------

    def auto_refresh(self):
        if self.exporting:
            self.after(2000, self.auto_refresh)
            return

        if not self.winfo_exists():
            return

        search = self.search_var.get().strip() or None

        if self.use_date_filter:
            date_from = self.date_from.get_date().strftime("%Y-%m-%d")
            date_to = self.date_to.get_date().strftime("%Y-%m-%d")
        else:
            date_from = None
            date_to = None

        rows = self.repo.get_transactions_filtered(
            search=search,
            date_from=date_from,
            date_to=date_to
        )

        if len(rows) != self.last_row_count:
            self.last_row_count = len(rows)
            self.tree.delete(*self.tree.get_children())

            today_str = date.today().strftime("%Y-%m-%d")

            for row in rows:
                timestamp = row[4]  # timestamp column
                tag = ()

                if timestamp.startswith(today_str):
                    tag = ("today",)

                timestamp_display = (
                    self.relative_time(row[4])
                    if self.relative_time_var.get()
                    else self.format_timestamp(row[4])
                )

                formatted_row = (
                    row[0], row[1], row[2], row[3],
                    timestamp_display
                )

                self.tree.insert("", "end", values=formatted_row, tags=tag)

            self.tree.tag_configure("today", font=("Poppins", 10))

        self.after(2000, self.auto_refresh)


    def load_transactions(self):
        self.tree.delete(*self.tree.get_children())

        search = self.search_var.get().strip() or None

        if self.use_date_filter:
            date_from = self.date_from.get_date().strftime("%Y-%m-%d")
            date_to = self.date_to.get_date().strftime("%Y-%m-%d")
        else:
            date_from = None
            date_to = None

        rows = self.repo.get_transactions_filtered(
            search=search,
            date_from=date_from,
            date_to=date_to
        )

        today_str = date.today().strftime("%Y-%m-%d")

        for row in rows:
            timestamp = row[4]  # timestamp column
            tag = ()

            if timestamp.startswith(today_str):
                tag = ("today",)

            timestamp_display = (
                self.relative_time(row[4])
                if self.relative_time_var.get()
                else self.format_timestamp(row[4])
            )

            formatted_row = (
                row[0], row[1], row[2], row[3],
                timestamp_display
            )

            self.tree.insert("", "end", values=formatted_row, tags=tag)

        self.tree.tag_configure("today", font=("Poppins", 10))


    def show_transaction_details(self, event):
        selected = self.tree.focus()
        if not selected:
            return

        name, barcode, action, qty, display_timestamp = self.tree.item(selected)["values"]

        win = ctk.CTkToplevel(self)
        win.title("Transaction Details")
        win.geometry("420x360+470+182")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        fields = {
            "Product Name": name,
            "Barcode": barcode,
            "Action": action,
            "Quantity": qty,
            "Timestamp": display_timestamp
        }

        for label, value in fields.items():
            ctk.CTkLabel(
                win,
                text=f"{label}:",
                font=ctk.CTkFont(weight="bold")
            ).pack(anchor="w", padx=20, pady=(12, 0))

            ctk.CTkLabel(
                win,
                text=str(value)
            ).pack(anchor="w", padx=20)


    def sort_by_column(self, col):
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]
        data.sort(reverse=self.sort_reverse[col])

        for index, (_, k) in enumerate(data):
            self.tree.move(k, "", index)

        self.sort_reverse[col] = not self.sort_reverse[col]


    # ---------------- Actions ----------------
    
    def clear_filters(self):
        self.use_date_filter = False
        self.search_entry.delete(0, "end")
        self.set_active_preset(None)
        self.update_date_indicator()
        self.load_transactions()


    def enable_date_filter(self, event=None):
        self.use_date_filter = True
        self.update_date_indicator()
        self.load_transactions()


    def save_filter_state(self):
        self._saved_filter = {
            "search": self.search_var.get(),
            "use_date": self.use_date_filter,
            "date_from": self.date_from.get_date(),
            "date_to": self.date_to.get_date(),
            "preset": next(
                (k for k, b in self.preset_buttons.items() if b.cget("fg_color") == "#1976D2"),
                None
            )
        }


    def restore_filter_state(self):
        s = self._saved_filter

        self.search_var.set(s["search"])
        self.use_date_filter = s["use_date"]

        if s["use_date"]:
            self.date_from.set_date(s["date_from"])
            self.date_to.set_date(s["date_to"])
            self.set_active_preset(s["preset"])

        self.update_date_indicator()
        self.load_transactions()


    def update_date_indicator(self):
        if self.use_date_filter:
            self.date_indicator.configure(
                text="Date Filter: ON",
                text_color="#00C853"  # green
            )
        else:
            self.date_indicator.configure(
                text="Date Filter: OFF",
                text_color="gray"
            )


    def set_active_preset(self, active_key=None):
        for key, btn in self.preset_buttons.items():
            if key == active_key:
                btn.configure(fg_color="#1976D2", hover_color="#3B8EE1")
            else:
                btn.configure(fg_color="#2CC985", hover_color="#2FA572")


    def preset_today(self):
        today = date.today()
        self.date_from.set_date(today)
        self.date_to.set_date(today)
        self.use_date_filter = True

        self.set_active_preset("today")
        self.update_date_indicator()
        self.load_transactions()


    def preset_last_7_days(self):
        today = date.today()
        self.date_from.set_date(today - timedelta(days=6))
        self.date_to.set_date(today)
        self.use_date_filter = True

        self.set_active_preset("7days")
        self.update_date_indicator()
        self.load_transactions()


    def preset_this_month(self):
        today = date.today()
        first_day = today.replace(day=1)
        self.date_from.set_date(first_day)
        self.date_to.set_date(today)
        self.use_date_filter = True

        self.set_active_preset("month")
        self.update_date_indicator()
        self.load_transactions()


    def relative_time(self, ts: str) -> str:
        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        delta = datetime.now() - dt

        seconds = int(delta.total_seconds())

        if seconds < 60:
            return "Just now"
        if seconds < 3600:
            return f"{seconds // 60} minutes ago"
        if seconds < 86400:
            return f"{seconds // 3600} hours ago"
        if seconds < 604800:
            return f"{seconds // 86400} days ago"

        return self.format_timestamp(ts)


    def write_csv(self, filepath, rows):
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


    def export_all_csv(self):
        self.exporting = True

        try:
            file = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")]
            )

            if not file:
                return

            # rows = self.repo.get_transactions_filtered()
            rows = [
                (
                    r[0], r[1], r[2], r[3],
                    self.format_timestamp(r[4])
                )
                for r in self.repo.get_transactions_filtered()
            ]

            self.write_csv(file, rows)
        
        finally:
            self.exporting = False

    
    def export_filtered_csv(self):
        self.exporting = True

        try:
            file = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv")]
            )

            if not file:
                return

            rows = [
                self.tree.item(row)["values"]
                for row in self.tree.get_children()
            ]

            self.write_csv(file, rows)

        finally:
            self.exporting = False


    def format_timestamp(self, ts: str) -> str:
        """
        Converts ISO timestamp to:
        January 06, 2026 2:00:15PM
        (Windows-safe)
        """
        if not ts:
            return ""

        ts = ts.replace("T", " ")
        dt = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")

        # Build hour manually (no leading zero)
        hour = dt.strftime("%I").lstrip("0") or "0"

        return (
            f"{dt.strftime('%B %d, %Y')} "
            f"{hour}:{dt.strftime('%M:%S%p')}"
        )


class Tooltip(ctk.CTkToplevel):
    def __init__(self, widget, text):
        super().__init__(widget)
        self.wm_overrideredirect(True)
        self.label = ctk.CTkLabel(self, text=text, padx=8, pady=4)
        self.label.pack()

    def show(self, x, y):
        self.geometry(f"+{x+15}+{y+10}")
        self.deiconify()

    def hide(self):
        self.withdraw()
