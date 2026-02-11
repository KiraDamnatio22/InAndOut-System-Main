from turtle import width
import customtkinter as ctk
from tkinter import ttk
from tkinter import TclError

from db.paths import IconPath
from ui.popups import InfoDialog
from ui.qty_dialog import QuantityDialog



class ScanSearchItems(ctk.CTkToplevel):

    def __init__(self, master, repo, on_search=None):
        super().__init__(master)

        self.master = master
        self.repo = repo
        self.on_search = on_search
    
        self.geometry("400x160+848+135")
        self.configure(fg_color="gray80")
        self.overrideredirect(True)
        self.grab_set()

        self.iconpath = IconPath()

        self.inner_frame = ctk.CTkFrame(self, fg_color="#E9E5E5", border_width=1)
        self.inner_frame.pack(fill="both", expand=True, padx=4, pady=4)

        self.btn_frame = ctk.CTkFrame(self.inner_frame, fg_color="#D7D4D4", border_width=1, height=130, width=380)
        self.btn_frame.pack(expand=True)
        self.btn_frame.pack_propagate(False)

        style = ttk.Style()
        style.theme_use("default")

        style.configure(
            "Treeview",
            font=("Segoe UI", 10),
            rowheight=28,
            background="#ffffff",
            fieldbackground="#ffffff",
            foreground="#222222",
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#f1f5f9",
            foreground="#1f2933",
            borderwidth=0,
            rowheight=50
        )

        style.map(
            "Treeview",
            background=[("selected", "#dbeafe")],
            foreground=[("selected", "#1e3a8a")]
        )

        self.place_buttons()

        self.bind("<Button-1>", self.check_scansearch_click, add="+")

    def place_buttons(self):
        search_btn = ctk.CTkButton(
            self.btn_frame, 
            text="Search", 
            font=ctk.CTkFont(family="Poppins", size=18, weight="bold"), 
            fg_color="#919191", 
            hover_color="#646363", 
            height=50, 
            command=self.open_search_pane
        )
        search_btn.pack(side="left", expand=True, padx=(15, 0))

        ctk.CTkLabel(
            self.btn_frame, 
            text="or",
            font=ctk.CTkFont(family="Poppins", size=18, weight="normal")
        ).pack(side="left", padx=3)

        scan_btn = ctk.CTkButton(
            self.btn_frame, 
            text="Scan", 
            font=ctk.CTkFont(family="Poppins", size=18, weight="bold"), 
            height=50,
            command=self.open_scan_pane
        )
        scan_btn.pack(side="right", expand=True, padx=(0, 15))

    def open_search_pane(self):
        self.grab_release()
        self.lower()

        self.search_window = ctk.CTkToplevel(self)
        self.search_window.configure(fg_color="#E9E5E5")
        self.search_window.geometry("690x160+350+240")
        self.search_window.grab_set()
        self.search_window.overrideredirect(True)

        inner_window = ctk.CTkFrame(self.search_window, fg_color="#F4F3F3", border_width=1)
        inner_window.pack(fill="both", expand=True, padx=3, pady=3)

        inner_window.grid_columnconfigure((0, 1), weight=1)
        inner_window.grid_rowconfigure((0, 1, 2), weight=1)

        # CLOSE BUTTON
        ctk.CTkButton(
            inner_window,
            text="",
            image=self.iconpath.get_icon_cache("close_b", (28, 28)),
            width=60,
            height=35,
            fg_color="#F4F3F3",
            hover_color="#CAC8C8",
            command=self.close_search_pane,
        ).grid(row=0, column=3, padx=(0, 10), pady=(10, 0), sticky="nw")

        # SEARCH PRODUCT LABEL
        ctk.CTkLabel(
            inner_window,
            text="Search product",
            font=ctk.CTkFont(family="Poppins", size=22, weight="normal")
        ).grid(row=0, column=0, rowspan=2, columnspan=3, padx=(10, 0), pady=(0, 0), sticky="s")

        # SEARCH ENTRY
        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            inner_window,
            textvariable=search_var,
            width=400,
            height=40,
            font=ctk.CTkFont(family="Poppins", size=18)
        )
        search_entry.grid(row=2, column=0, rowspan=3, columnspan=3, padx=30, pady=(0, 12), sticky="ew")
        self.search_window.after(10, search_entry.focus_set())

        def on_change(*_):
            if self.on_search:
                self.on_search(search_var.get())

        search_var.trace_add("write", on_change)

    def open_scan_pane(self):
        
        self.scanner_window = ctk.CTkToplevel(self)
        self.scanner_window.title("Scan Product")
        self.scanner_window.after(200, lambda: self.scanner_window.iconbitmap(self.iconpath.get_icon_cache("search", icon_type="bitmap")))
        self.scanner_window.geometry("450x300+490+230")
        self.scanner_window.resizable(False, False)
        self.scanner_window.configure(fg_color="#E9E5E5")
        # scanner_window.transient(self)
        self.scanner_window.grab_set()
        self.scanner_window.lift()

        self.scanned_barcode = ""
        self.scanner_window.bind("<Key>", self.handle_scan_input)

        self.inner_frame = ctk.CTkFrame(self.scanner_window, fg_color="#F4F3F3", border_width=1)
        self.inner_frame.pack(fill="both", expand=True, padx=3, pady=3)

        ctk.CTkLabel(
            self.inner_frame,
            text="",
            image=self.iconpath.get_icon_cache("scanner", (130, 130))
        ).pack(pady=(50, 15))

        self.scan_label = ctk.CTkLabel(
            self.inner_frame,
            text="Scan Barcode",
            text_color="#3E3E3E",
            font=ctk.CTkFont(size=17, weight="bold")
        )
        self.scan_label.pack(pady=(20, 15))

    def open_product_lister(self):
        self.product_lister = ctk.CTkToplevel(self.scanner_window)
        self.product_lister.title("Product Searched List")
        self.product_lister.geometry("1300x200+20+390")
        self.product_lister.grab_set()
        self.product_lister.focus_force()

        self.product_lister.grid_columnconfigure(0, weight=1)
        self.product_lister.grid_rowconfigure(0, weight=1)

        self.product_table = ttk.Treeview(
            self.product_lister,
            columns=["name", "barcode", "price", "desc", "stock"],
            show="headings"
        )
        self.product_table.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        # Headings
        self.product_table.heading("name", text="Product Name")
        self.product_table.heading("barcode", text="Barcode")
        self.product_table.heading("price", text="Price")
        self.product_table.heading("desc", text="Description")
        self.product_table.heading("stock", text="Stock")

        # Column sizes
        self.product_table.column("name", width=200, anchor="center")
        self.product_table.column("barcode", width=130, anchor="center")
        self.product_table.column("price", width=60, anchor="center")
        self.product_table.column("desc", width=300, anchor="center")
        self.product_table.column("stock", width=50, anchor="center")

        # print(self.item)
        self.product_table.insert("", "end", values=(
            self.item["name"],
            self.item["id"],
            self.item["price"],
            self.item["description"],
            self.item["stock"]
        ))

        options_frame = ctk.CTkFrame(self.product_lister, fg_color="#F3F1F1", width=350)
        options_frame.pack_propagate(False)
        options_frame.grid(row=0, column=1, pady=5, sticky="ns")

        ctk.CTkButton(
            options_frame, 
            text="Add To Ticket",
            command=lambda i=self.item: self.add_product_to_ticket(i)
        ).pack(pady=(45, 0))
        ctk.CTkButton(options_frame, text="Get Stock", state="disabled").pack(pady=15)

    def add_product_to_ticket(self, item):
        # Ask for quantity
        dialog = QuantityDialog(self, max_stock=item["stock"])
        self.wait_window(dialog)

        if dialog.qty is None:
            # User cancelled
            return

        self.close_all_children()
        self.safe_destroy()

        # Pass the quantity to the ticket
        self.master.add_to_ticket(item, qty=dialog.qty)

    # def add_product_to_ticket(self, item):
    #     # Ask for quantity
    #     dialog = QuantityDialog(self, max_stock=item["stock"])
    #     self.wait_window(dialog)

    #     if dialog.qty is None:
    #         # User cancelled
    #         return

    #     item_to_add = item.copy()
    #     item_to_add["qty"] = dialog.qty

    #     self.close_all_children()
    #     self.safe_destroy()

    #     # Pass item with quantity to master
    #     self.master.add_to_ticket(item_to_add)

    # def add_product_to_ticket(self, item):
        # self.open_qty_dialog(self, item["stock"])

        # self.close_all_children()
        # self.safe_destroy()
        # self.master.add_to_ticket(item)

    def handle_scan_input(self, event):
        # When Enter is pressed → process barcode
        if event.keysym == "Return":

            if self.scanned_barcode:
                self.item = self.repo.get_item_by_barcode(self.scanned_barcode.strip())
                if not self.item:
                    dialog = InfoDialog(
                        master=self,
                        title="Warning",
                        header="Item Not Found",
                        info="Barcode is not registered.",
                        info_color="red",
                        is_needed=False,
                        posx=538,
                        posy=325
                    )
                    self.wait_window(dialog)
                    self.focus_set()
                    return
                
                self.open_product_lister()

            # Reset buffer
            self.scanned_barcode = ""
            return

        # Ignore special keys
        if len(event.char) == 1:
            self.scanned_barcode += event.char

    def check_scansearch_click(self, event):
        try:
            if not self.winfo_ismapped():
                return

            x1 = self.winfo_rootx()
            y1 = self.winfo_rooty()
            x2 = x1 + self.winfo_width()
            y2 = y1 + self.winfo_height()

            # If click outside sidebar
            if not (x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2):
                self.grab_release()
                self.lower()
        except TclError:
            # Widget has been destroyed, ignore
            pass

    def safe_destroy(self):
        # Release grab safely
        try:
            self.grab_release()
        except TclError:
            pass

        # Unbind global clicks
        try:
            self.unbind_all("<Button-1>")
        except TclError:
            pass

        # Destroy the window safely
        try:
            self.destroy()
        except TclError:
            pass

    def close_all_children(self):
        for child in ["product_lister", "scanner_window", "search_window"]:
            window = getattr(self, child, None)
            if window is not None:
                try:
                    window.grab_release()
                    window.destroy()
                except TclError:
                    pass
                setattr(self, child, None)

    def close_search_pane(self):
        self.search_window.grab_release()
        self.search_window.destroy()
        self.lower()
