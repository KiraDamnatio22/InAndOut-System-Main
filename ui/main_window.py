import tkinter as tk
import customtkinter as ctk
from functools import partial
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import LETTER

from db.paths import IconPath, RECEIPT_DIR
from db.db_base import DBClass
from db.inventory_repository import InventoryRepository
from ui.item_tile import ItemTile
from ui.ticket_row import TicketRow
from ui.scan_item import ScanSearchItems
from ui.popups import InfoDialog
from ui.product_manager import ProductManagementWindow
from ui.transaction_window import TransactionHistoryWindow

from models.ticket_model import TicketModel


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


class ViewManager:
    def __init__(self, root):
        self.root = root
        self.views = {}

    def add(self, name, frame):
        self.views[name] = frame
        frame.grid(row=0, column=0, sticky="nsew")

    def show(self, name):
        frame = self.views.get(name)
        if frame:
            # frame.tkraise()
            frame.lift()

    def hide(self, name):
        frame = self.views.get(name)
        if frame:
            frame.lower()


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.iconpath = IconPath()

        self.title("Electrical Supplies Inventory")
        self.iconbitmap(self.iconpath.get_icon_cache("system", icon_type="bitmap"))
        self.geometry("1200x680+100+5")
        self.resizable(False, False)
        # self.protocol("WM_DELETE_WINDOW", self.on_closing) # Optional

        # global variables
        self.db = DBClass()
        self.repo = InventoryRepository(self.db)
        # self.repo.record_product_stock_in("E2602091319003", 10)  # Camera X
        # self.repo.record_product_stock_in("E2602072308001", 10)  # Aerotape
        # self.repo.record_product_stock_in("E2602072322002", 100)  # Polytape
        # self.repo.record_product_stock_in("E2602091511004", 10)  # Conduits X
        # print("success in")
        self.ticket_model = TicketModel()
        self.ticket_model.subscribe(self.on_ticket_update)

        self.all_items = []    # raw item data cache
        self.item_tiles = {}   # {item_id: ItemTile}
        self.purchase_list = []

        self.ticket_row_pool = []
        self.active_ticket_rows = {}
        self.ticket_rows = {}   # {item_id: TicketRow}

        self.checkout_row_pool = []
        self.active_checkout_rows = {}
        self.checkout_rows = {}
        self.checkout_total = 0
        self.change = 0
        self.checkout_total_var = ctk.StringVar(value="0.00")
        self.receipt_text_str = ""
        self.checkout_state = "panel"   # or "charge"

        self.render_pending = False
        
        # global frames
        self.main_frame = ctk.CTkFrame(self, fg_color="#eaeaea", corner_radius=0)
        self.main_frame.pack(fill="both", expand=True)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

        self.details_view = ctk.CTkFrame(self.main_frame, fg_color="#aca7a7", corner_radius=0)
        # self.details_view.grid(row=0, column=0)
        self.details_view.grid_rowconfigure(1, weight=1)

        self.checkout_view = ctk.CTkFrame(self.main_frame, fg_color="#eaeaea")
        # self.checkout_view.grid(row=0, column=0, sticky="nsew")
        self.checkout_view.grid_columnconfigure(0, weight=1)
        self.checkout_view.grid_columnconfigure(1, weight=0)
        self.checkout_view.grid_rowconfigure(2, weight=1)
        self.checkout_view.grid_propagate(False)

        self.view_manager = ViewManager(self.main_frame)
        self.view_manager.add("main", self.details_view)
        self.view_manager.add("checkout", self.checkout_view)
        self.view_manager.show("main") # show details frame initially

        # startup methods
        self.build_details_section()
        self.build_checkout_view()
        # self.checkout_view.grid_remove()

        # key bindings
        self.bind("<Escape>", lambda e: self.back_to_main_menu())
        self.bind("<F12>", lambda e: self.open_checkout())
        self.bind("<Button-1>", self.check_sidebar_click)


    def build_details_section(self):
        # ===================== MENU SECTION ========================= #
        menu_frame = ctk.CTkFrame(
            self.details_view, 
            fg_color="#2CC985", 
            corner_radius=0,
            # width=700,
            height=80
        )
        menu_frame.grid(row=0, column=0, sticky="nsew")
        menu_frame.grid_propagate(False)
        menu_frame.grid_columnconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(
            self.details_view,
            fg_color="#41DD99",
            width=220,
            height=576,
            corner_radius=0
        )
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="MENU",
            font=ctk.CTkFont(family="Poppins", size=18, weight="bold"),
            text_color="#FFFFFF"
            # text_color="#1F2933"
        ).pack(anchor="w", padx=(16, 0), pady=(40, 5))

        ctk.CTkButton(
            self.sidebar,
            text="Manage Products",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Poppins", size=14),
            anchor="w",
            fg_color="#0F766E",
            hover_color="#15504B",
            command=self.open_product_manager
        ).pack(fill="x", padx=15, pady=(15, 0))

        ctk.CTkButton(
            self.sidebar,
            text="Transaction History",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Poppins", size=14),
            anchor="w",
            fg_color="#0F766E",
            hover_color="#15504B",
            command=self.open_transaction_window
        ).pack(fill="x", padx=15, pady=(12, 0))
        
        # SIDEBAR MENU ICON BUTTON
        ctk.CTkButton(
            menu_frame, 
            text="", 
            image=self.iconpath.get_icon_cache("menu"),
            fg_color="transparent",
            hover_color="#1FA169",
            width=50,
            height=50,
            command=self.open_sidebar
        ).grid(row=0, column=0, padx=(25, 0), pady=(15, 0))

        ctk.CTkLabel(menu_frame, text="SPB Electrical Supply", text_color="#FFFFFF", font=ctk.CTkFont(family="Poppins", size=27, weight="normal")).grid(row=0, column=1, padx=(15, 0), pady=(17, 0), sticky="w")

        product_categories = ["All items", "Batteries", "Cables", "Cameras", "Conduits", "Connectors", "Enclosures", "Lights", "Sensors", "Switches", "Outlets"]
        optionmenu_var = ctk.StringVar(value="All items")
        optionmenu = ctk.CTkOptionMenu(
            menu_frame,
            values=product_categories,
            variable=optionmenu_var,
            font=ctk.CTkFont(family="Poppins", size=22),
            dropdown_font=ctk.CTkFont(family="Poppins", size=16),
            fg_color="#2CC985",
            button_color="#2CC985",
            width=105,
            height=50,
            command=self.optionmenu_callback,
        )
        optionmenu.grid(row=0, column=2, padx=(0, 10), pady=(18, 0))

        search_btn = ctk.CTkLabel(
            menu_frame, 
            text="", 
            image=self.iconpath.get_icon_cache("search", (32, 32)),
            width=50,
            height=50,
            cursor="hand2",
        )
        search_btn.grid(row=0, column=3, padx=(0, 25), pady=(15, 0), sticky="e")
        search_btn.bind("<Button-1>", self.open_search_scan_window)


        # ===================== TICKET SECTION ========================= #
        ticket_frame = ctk.CTkFrame(self.details_view, fg_color="#fffefe", corner_radius=0)
        ticket_frame.grid(row=0, column=1, sticky="nsew")
        ticket_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(ticket_frame, text="Ticket", font=ctk.CTkFont(family="Poppins", size=25, weight="normal"), fg_color="transparent").grid(row=0, column=0, padx=(30, 0), pady=(20, 0), sticky="w")

        account_btn = ctk.CTkLabel(
            ticket_frame, 
            text="", 
            image=self.iconpath.get_icon_cache("account", (38, 38)),
            width=50,
            height=40,
            cursor="hand2",
            # fg_color="lightgreen"
        )
        account_btn.grid(row=0, column=1, padx=(25, 0), pady=(15, 0))
        account_btn.bind("<Button-1>", self.open_account_pane)

        ticket_options_btn = ctk.CTkLabel(
            ticket_frame, 
            text="", 
            image=self.iconpath.get_icon_cache("more_vert"),
            width=50,
            height=40,
            cursor="hand2",
            # fg_color="lightgreen"
        )
        ticket_options_btn.grid(row=0, column=2, padx=(15, 25), pady=(15, 0))
        ticket_options_btn.bind("<Button-1>", self.open_ticket_option_menu)


        # ===================== ITEMS SECTION ========================= #
        
        self.items_frame = ctk.CTkFrame(self.details_view, fg_color="#eaeaea", corner_radius=0, width=700, height=610)
        self.items_frame.grid(row=1, column=0)
        self.items_frame.grid_propagate(False)

        self.all_items = self.fetch_items_for_ui()
        self.build_item_tiles(self.items_frame, self.all_items)


        # ===================== ORDERS SECTION ========================= #

        orders_frame = ctk.CTkFrame(self.details_view, fg_color="#fffefe", corner_radius=0, border_width=1)
        orders_frame.grid(row=1, column=1, sticky="nsew")
        orders_frame.grid_rowconfigure(2, weight=1)

        self.purchase_option_var = ctk.StringVar(value="Delivery")
        purchase_option = ctk.CTkOptionMenu(
            orders_frame,
            values=["Delivery", "Walk-In"],
            variable=self.purchase_option_var,
            font=ctk.CTkFont(family="Poppins", size=17),
            text_color="#6D6D6D",
            dropdown_font=ctk.CTkFont(family="Poppins", size=16),
            fg_color="#fffefe",
            button_color="#fffefe",
            button_hover_color="#c3c0c0",
            height=50
            # command=self.optionmenu_callback,
        )
        purchase_option.grid(row=0, column=0, sticky="nsew", padx=(15, 25), pady=(15, 10))

        divider = ctk.CTkFrame(orders_frame, border_width=0.8, fg_color="transparent", height=2)

        divider.grid(row=1, column=0, sticky="nsew", padx=(16, 25))

        if not hasattr(self, "ticket_items_frame"):
            self.ticket_items_frame = ctk.CTkScrollableFrame(
                orders_frame,
                fg_color="transparent",
                width=460
            )
            self.ticket_items_frame.grid(row=2, column=0, sticky="nsew", padx=10)

        self.ticket_action_frame = ctk.CTkFrame(orders_frame, fg_color="transparent")
        self.ticket_action_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=10)

        ctk.CTkButton(
            self.ticket_action_frame,
            text="Clear Ticket",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Poppins", size=15, weight="bold"),
            height=45,
            command=self.clear_ticket
        ).pack(side="left", expand=True, fill="x", padx=(0, 8))

        ctk.CTkButton(
            self.ticket_action_frame,
            text="Charge",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Poppins", size=15, weight="bold"),
            height=45,
            fg_color="#2CC985",
            command=self.open_checkout
        ).pack(side="right", expand=True, fill="x", padx=(8, 0))


    def build_checkout_view(self):
        # # Back to menu button
        # back_btn = ctk.CTkButton(
        #     self.checkout_view,
        #     text="",
        #     image=self.iconpath.get_icon_cache("back_ios"),
        #     fg_color="#EAEAEA",
        #     hover_color="#959494",
        #     width=65,
        #     height=40,
        #     command=self.back_to_main_menu
        # )
        # back_btn.grid(row=0, column=0, columnspan=2, padx=(15, 0), pady=(15, 0), sticky="w")

        # Header
        header = ctk.CTkLabel(
            self.checkout_view,
            text="Checkout",
            font=ctk.CTkFont(family="Poppins", size=28, weight="bold")
        )
        header.grid(row=1, column=0, columnspan=2)

        # # LEFT — Order Summary
        self.checkout_orders = ctk.CTkFrame(self.checkout_view, fg_color="#E5E1E1")
        self.checkout_orders.grid(row=2, column=0, sticky="nsew", padx=(15, 0), pady=10)

        self.checkout_view.grid_columnconfigure(0, weight=1)
        self.checkout_view.grid_columnconfigure(1, weight=0)
        self.checkout_view.grid_rowconfigure(2, weight=1)

        self.checkout_orders_inner = ctk.CTkFrame(self.checkout_orders,fg_color="#E5E1E1")
        self.checkout_orders_inner.pack(fill="both", expand=True, padx=10, pady=10)

        self.build_checkout_orders()

        # RIGHT — Payment
        self.checkout_payment = ctk.CTkFrame(
            self.checkout_view, 
            width=600, 
            corner_radius=0,
            # border_width=1
        )
        self.checkout_payment.grid(row=2, column=1, padx=(0, 15), pady=10, sticky="ns")
        self.checkout_payment.grid_propagate(False)
        self.checkout_payment.grid_columnconfigure(0, weight=1)
        # self.checkout_payment.grid_rowconfigure((2), weight=1)

        self.build_payment_panel()
        # self.after_idle(self.build_payment_panel)


    def schedule_render(self):
        """Batch UI redraws into a single frame update."""
        if self.render_pending:
            return
        
        self.render_pending = True
        self.after(16, self.perform_render)  # 60fps batching


    def perform_render(self):
        """Execute the queued UI redraw."""
        self.render_pending = False
        # self.update_idletasks()


    def build_checkout_orders(self):
        for w in self.checkout_orders_inner.winfo_children():
            w.destroy()

        top_frame = ctk.CTkFrame(self.checkout_orders_inner, corner_radius=0, border_width=0)
        top_frame.pack(fill="both")

        ctk.CTkLabel(
            top_frame,
            text="Ticket",
            text_color="#414141",
            font=ctk.CTkFont(family="Poppins", size=22),
            anchor="w"
        ).grid(row=0, column=0, pady=10, padx=(20, 0), sticky="ew")

        bot_frame = ctk.CTkFrame(self.checkout_orders_inner, corner_radius=0, border_width=0)
        bot_frame.pack(fill="both", expand=True)

        bot_frame.grid_columnconfigure(0, weight=3)  # name
        bot_frame.grid_columnconfigure(1, weight=4)  # descr
        bot_frame.grid_columnconfigure(2, weight=1)  # qty
        bot_frame.grid_columnconfigure(3, weight=2)  # price

        ctk.CTkFrame(
            bot_frame,
            height=3,
            border_width=1,
        ).grid(row=0, column=0, columnspan=4, sticky="ew", padx=10)

        ctk.CTkLabel(
            bot_frame,
            text=self.purchase_option_var.get(),
            text_color="#6D6D6D",
            font=ctk.CTkFont(family="Poppins", size=16),
            anchor="w",
        ).grid(row=1, column=0, pady=(10, 25), padx=(10, 0), sticky="ew")

        self.total = 0
        row = 2

        # for item_id, entry in self.ticket_items.items():
        for item_id, entry in self.ticket_model.items.items():
            item = self.get_item_by_id(item_id)
            if not item:
                continue

            qty = entry["qty"]
            line_total = item["price"] * qty
            self.total += line_total

            # NAME
            ctk.CTkLabel(
                bot_frame,
                text=item["name"],
                text_color="#6D6D6D",
                font=ctk.CTkFont(family="Poppins", size=16),
                anchor="w"
            ).grid(row=row, column=0, sticky="w", padx=(10, 4), pady=4)

            # DESCRIPTION
            ctk.CTkLabel(
                bot_frame,
                text=item["description"],
                text_color="#6D6D6D",
                font=ctk.CTkFont(family="Poppins", size=16),
                anchor="w"
            ).grid(row=row, column=1, sticky="w", padx=4)

            # QTY
            ctk.CTkLabel(
                bot_frame,
                text=f"×{qty}",
                text_color="#6D6D6D",
                font=ctk.CTkFont(family="Poppins", size=16),
                anchor="center"
            ).grid(row=row, column=2, sticky="e", padx=4)

            # PRICE
            ctk.CTkLabel(
                bot_frame,
                text=f"{line_total:.2f}",
                text_color="#404040",
                font=ctk.CTkFont(family="Poppins", size=17),
                anchor="e"
            ).grid(row=row, column=3, sticky="e", padx=(4, 10))

            row += 1

        total_frame = ctk.CTkFrame(bot_frame, fg_color="transparent")
        total_frame.grid(row=row, column=0, columnspan=4, padx=9, pady=(29, 0), sticky="ew")

        total_frame.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            total_frame,
            text="Total",
            text_color="#212121",
            font=ctk.CTkFont(family="Poppins", size=17),
        ).grid(row=0, column=0, pady=5, sticky="w")

        ctk.CTkLabel(
            total_frame,
            text=f"{self.total:,.02f}",
            text_color="#212121",
            font=ctk.CTkFont(family="Poppins", size=17),
        ).grid(row=0, column=1, pady=5, sticky="e")


    def build_payment_panel(self):

        self.checkout_state = "panel"

        self.calculate_checkout_total()  # Ensure latest total
        
        self.clear_checkout_payment()

        total_due_frame = ctk.CTkFrame(
            self.checkout_payment,
            fg_color="transparent"
        )
        total_due_frame.grid(row=0, column=0, padx=5, pady=(50, 5), sticky="ew")
        total_due_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            total_due_frame,
            textvariable=self.checkout_total_var,
            text_color="#414141",
            font=ctk.CTkFont(family="Poppins", size=35)
        ).grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        ctk.CTkLabel(
            total_due_frame,
            text=f"Total amount due",
            text_color="#6D6D6D",
            font=ctk.CTkFont(family="Poppins", size=18)
        ).grid(row=0, column=0, padx=5, pady=(62, 5), sticky="ew")

        self.payment_frame = ctk.CTkFrame(
            self.checkout_payment,
            fg_color="transparent"
        )
        self.payment_frame.grid(row=1, column=0, padx=26, pady=(30, 5), sticky="ew")

        ctk.CTkLabel(
            self.payment_frame,
            text="Cash received",
            text_color="#6D6D6D",
            font=ctk.CTkFont(family="Poppins", size=18),
            anchor="w"
        ).grid(row=0, column=0, columnspan=2, padx=(15, 0), pady=(10, 0), sticky="ew")

        ctk.CTkLabel(
            self.payment_frame,
            text="",
            image=self.iconpath.get_icon_cache("payments_b"),
            height=45,
        ).grid(row=1, column=0, padx=(15, 0), pady=(0, 10))

        self.cash_received = ctk.StringVar(value="")
        self.cash_received.trace_add("write", self.on_cash_received_change)

        self.cash_entry = ctk.CTkEntry(
            self.payment_frame,
            textvariable=self.cash_received,
            height=50,
            width=300,
            font=ctk.CTkFont(family="Poppins", size=20),
            text_color="#414141",
            justify="center"
        )
        self.cash_entry.grid(row=1, column=1, padx=(10, 0), pady=(0, 10), sticky="w")
        self.after(100, self.cash_entry.focus_set)

        self.charge_button = ctk.CTkButton(
            self.payment_frame,
            text="CHARGE",
            font=ctk.CTkFont(family="Poppins", size=15, weight="bold"),
            height=55,
            corner_radius=0,
            state="disabled",
            fg_color="#939191",
            command=self.build_payment_charge_section
        )
        self.charge_button.grid(row=0, rowspan=2, column=2, padx=(20, 0), pady=(0, 11), sticky="sew")

        self.cash_status_var = ctk.StringVar(value="")
        self.cash_status_label = ctk.CTkLabel(
            self.payment_frame,
            textvariable=self.cash_status_var,
            font=ctk.CTkFont(family="Poppins", size=18),
            text_color="#6D6D6D"
        )
        self.cash_status_label.grid(row=2, column=1, padx=(10, 0), pady=(0, 0), sticky="ew")

        cash_options_frame = ctk.CTkFrame(
            self.checkout_payment,
            fg_color="transparent",
        )
        cash_options_frame.grid(row=2, column=0, padx=5, pady=(0, 5), sticky="ew")

        self.cash_option_buttons = []

        # Remove old BEST label if it exists
        if hasattr(self, "best_cash_label") and self.best_cash_label:
            self.best_cash_label.destroy()
            self.best_cash_label = None

        cash_options, step = self.get_cash_options()

        for col, amount in enumerate(cash_options):
            is_best = (col == 0)

            btn = ctk.CTkButton(
                cash_options_frame,
                text=str(amount),
                text_color="#FFFFFF" if is_best else "#414141",
                font=ctk.CTkFont(
                    family="Poppins",
                    size=16,
                    weight="bold" if is_best else "normal"
                ),
                fg_color="#2CC985" if is_best else "gray80",
                hover_color="#30CE8A" if is_best else "gray75",
                width=100,
                height=60,
                corner_radius=0,
                command=partial(self.enter_suggested_cash_option, amount)
            )

            btn.grid(
                row=0,
                column=col,
                padx=(80, 10) if col == 0 else (0, 10),
                pady=(10, 3)
            )

            self.cash_option_buttons.append(btn)

            # Best label
            if is_best:
                self.best_cash_label = ctk.CTkLabel(
                    cash_options_frame,
                    text="BEST",
                    compound="right",
                    image=self.iconpath.get_icon_cache("star", (18, 18)),
                    font=ctk.CTkFont(family="Poppins", size=13, weight="bold"),
                    text_color="#08995A",
                    padx=5,
                    pady=5   
                )
                self.best_cash_label.grid(
                    row=1,
                    column=col,
                    padx=(80, 10),
                    pady=(0, 10)
                )

        # self.cash_status_var = ctk.StringVar(value="")
        # self.cash_status_label = ctk.CTkLabel(
        #     self.checkout_payment,
        #     textvariable=self.cash_status_var,
        #     font=ctk.CTkFont(family="Poppins", size=18),
        #     text_color="#6D6D6D"
        # )
        # self.cash_status_label.grid(row=3, column=0, pady=(0, 0))

        # EXACT button
        if self.checkout_total % step == 0:
            self.exact_button = ctk.CTkButton(
                self.checkout_payment,
                text="EXACT",
                font=ctk.CTkFont(family="Poppins", size=16, weight="bold"),
                fg_color="#087799",
                hover_color="#254D59",
                # hover_color="#30CE8A",
                width=100,
                height=35,
                corner_radius=0,
                command=lambda: self.enter_suggested_cash_option(self.checkout_total)
            )
            self.exact_button.grid(row=4, column=0, pady=(0, 20))
        else:
            self.exact_button = None

        back_btn = ctk.CTkButton(
            self.checkout_payment,
            image=self.iconpath.get_icon_cache("home_b", (30, 30)),
            compound="right",
            # text="Menu",
            text="←",
            text_color="#000000",
            font=ctk.CTkFont(family="Poppins", size=18, weight="bold"),
            fg_color="#DBDBDB",
            hover_color="#B7B7B7",
            command=self.back_to_main_menu
        )
        back_btn.grid(row=5, column=0, padx=250, pady=(45, 0), sticky="ew")


    def build_payment_charge_section(self):
        
        self.calculate_checkout_total()  # Ensure latest total

        self.clear_checkout_payment()

        button_frame = ctk.CTkFrame(self.checkout_payment, fg_color="transparent")
        button_frame.grid(row=99, column=0, pady=20)

        ctk.CTkButton(
            button_frame,
            text="← Back to Payment",
            command=self.build_payment_panel
        ).pack(side="left", padx=10)

        # ctk.CTkButton(
        #     button_frame,
        #     text="← Main Menu",
        #     command=self.back_to_main_menu
        # ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            image=self.iconpath.get_icon_cache("back_ios", (18, 18)),
            text="Menu",
            text_color="#000000",
            font=ctk.CTkFont(family="Poppins", size=18),
            command=self.back_to_main_menu
        ).pack(side="left", padx=10)


        total_charge_frame = ctk.CTkFrame(
            self.checkout_payment,
            fg_color="transparent"
        )
        total_charge_frame.grid(row=0, column=0, padx=5, pady=(50, 50), sticky="ew")
        total_charge_frame.grid_columnconfigure((0), weight=1)

        left_frame = ctk.CTkFrame(total_charge_frame)
        left_frame.grid(row=0, column=0, padx=(90, 10), pady=2)
        left_frame.grid_columnconfigure(0, weight=1)

        right_frame = ctk.CTkFrame(
            total_charge_frame, 
            width=200,
            height=100
        )
        right_frame.grid_propagate(False)
        right_frame.grid(row=0, column=1, padx=(0, 30))
        right_frame.grid_columnconfigure(0, weight=1)

        # Total paid
        ctk.CTkLabel(
            left_frame,
            # text=f"₱{int(self.cash_received.get()):,.2f}",
            text=f"{float(self.cash_received.get()):,.2f}",
            text_color="#414141",
            font=ctk.CTkFont(family="Poppins", size=35)
        ).grid(row=0, column=0, padx=0, pady=5, sticky="e")

        ctk.CTkLabel(
            left_frame,
            text=f"Total paid",
            text_color="#6D6D6D",
            font=ctk.CTkFont(family="Poppins", size=18)
        ).grid(row=0, column=0, padx=0, pady=(63, 5), sticky="w")

        # Change
        ctk.CTkLabel(
            right_frame,
            text=f"{self.change:,.2f}",
            text_color="#414141",
            font=ctk.CTkFont(family="Poppins", size=35)
        ).grid(row=0, column=0, padx=0, pady=5, sticky="w")

        ctk.CTkLabel(
            right_frame,
            text=f"Change",
            text_color="#6D6D6D",
            font=ctk.CTkFont(family="Poppins", size=18)
        ).grid(row=0, column=0, padx=0, pady=(63, 5), sticky="w")


        # -------------------------------------------------------------------

        receipt_frame = ctk.CTkFrame(
            self.checkout_payment,
            fg_color="transparent",
            # border_width=1
        )
        receipt_frame.grid(row=1, column=0, padx=5, pady=(5, 5), sticky="ew")

        # Email Icon
        ctk.CTkLabel(
            receipt_frame,
            text="",
            image=self.iconpath.get_icon_cache("email_b")
        ).grid(row=0, column=0, padx=(65, 5), pady=(0, 0), sticky="ew")

        email_entry = ctk.CTkEntry(
            receipt_frame,
            placeholder_text="Enter email",
            font=ctk.CTkFont(family="Poppins", size=14),
            width=300, 
            height=35,
            fg_color="gray86",
            border_color="gray76"
        )
        email_entry.grid(row=0, column=1, padx=(5, 0), pady=(0, 0))

        # SEND RECEIPT BUTTON
        ctk.CTkButton(
            receipt_frame,
            text="SEND RECEIPT",
            text_color="#5C5C5C",
            font=ctk.CTkFont(family="Poppins", weight="bold"),
            fg_color="#CFCFCF",
            hover_color="#C1C1C1",
            height=33,
            width=100,
            corner_radius=0
        ).grid(row=0, column=2, padx=(10, 0), pady=(0, 0))

        # PRINT RECEIPT BUTTON
        ctk.CTkButton(
            receipt_frame,
            image=self.iconpath.get_icon_cache("print_b"),
            text="PRINT RECEIPT",
            text_color="#4A4A4A",
            font=ctk.CTkFont(family="Poppins", weight="bold"),
            fg_color="#DBDBDB",
            hover_color="#DBDBDB",
            height=33,
            width=100,
            corner_radius=0,
            command=self.open_receipt_printing_window
        ).grid(row=1, column=0, columnspan=3, padx=(65, 0), pady=(50, 0))

        # NEXT SALE BUTTON
        ctk.CTkButton(
            self.checkout_payment,
            image=self.iconpath.get_icon_cache("price_check_w"),
            text="NEXT SALE",
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Poppins", weight="bold"),
            corner_radius=0,
            command=self.complete_transaction
        ).grid(row=2, column=0, padx=120, pady=(125, 10), sticky="ew")


    def clear_checkout_payment(self):
        for w in self.checkout_payment.winfo_children():
            w.destroy()


    # def clear_checkout_payment(self):
    #     for w in self.checkout_payment.winfo_children():
    #         w.grid_remove()
    #     print("cleared checkout payment") 


    def get_cash_step(self):
        total = self.checkout_total

        if total < 1000:
            return 100
        elif total < 5000:
            return 500
        else:
            return 1000
        

    def get_cash_options(self, count=4):
        step = self.get_cash_step()
        total = self.checkout_total

        first = ((int(total) + step - 1) // step) * step
        options = [first + step * i for i in range(count)]

        return options, step


    def enter_suggested_cash_option(self, amount):
        self.cash_received.set(str(amount))
        self.cash_entry.focus_set()
        self.cash_entry.icursor("end")


    def refresh_cash_options(self):
        # If checkout UI is not active or buttons are gone → bail
        if not hasattr(self, "cash_option_buttons"):
            return

        if not self.cash_option_buttons:
            return

        # Check if first button still exists in Tk
        if not self.cash_option_buttons[0].winfo_exists():
            return

        cash_options, _ = self.get_cash_options()

        # Remove old BEST label safely
        if hasattr(self, "best_cash_label") and self.best_cash_label:
            if self.best_cash_label.winfo_exists():
                self.best_cash_label.destroy()
            self.best_cash_label = None

        for i, (btn, amount) in enumerate(zip(self.cash_option_buttons, cash_options)):
            if not btn.winfo_exists():
                continue

            is_best = (i == 0)

            btn.configure(
                text=str(amount),
                fg_color="#2CC985" if is_best else "gray80",
                text_color="#FFFFFF" if is_best else "#414141",
                hover_color="#30CE8A" if is_best else "gray75",
                command=partial(self.enter_suggested_cash_option, amount)
            )

            if is_best:
                self.best_cash_label = ctk.CTkLabel(
                    btn.master,
                    text="BEST",
                    compound="right",
                    image=self.iconpath.get_icon_cache("star", (18, 18)),
                    font=ctk.CTkFont(family="Poppins", size=13, weight="bold"),
                    text_color="#08995A",
                    padx=5,
                    pady=5
                )
                self.best_cash_label.grid(
                    row=1,
                    column=i,
                    padx=(80, 10),
                    pady=(0, 10)
                )


    def on_cash_received_change(self, *args):
        cash_str = self.cash_received.get().strip()

        # Empty input → reset UI
        if not cash_str:
            self.cash_status_var.set("")
            self.charge_button.configure(state="disabled", fg_color="#939191")
            return

        try:
            cash = float(cash_str)
        except ValueError:
            self.cash_status_var.set("Invalid amount")
            self.cash_status_label.configure(text_color="#C0392B")
            self.charge_button.configure(state="disabled", fg_color="#939191")
            return

        self.change = cash - self.checkout_total

        if self.change < 0:
            self.cash_status_var.set("Insufficient cash")
            self.cash_status_label.configure(text_color="#C0392B")
            self.charge_button.configure(state="disabled", fg_color="#939191")
        else:
            self.cash_status_var.set("")
            self.charge_button.configure(
                state="normal",
                fg_color="#08995A",
                hover_color="#30CE8A"
            )


    def calculate_checkout_total(self):
        self.checkout_total = self.ticket_model.total()
        self.checkout_total_var.set(f"{self.checkout_total:,.2f}")
        return self.checkout_total


    def deduct_purchased_items(self):
        for item_id, entry in self.ticket_model.items.items():
            try:
                self.repo.record_product_stock_out(item_id, entry["qty"])
            except ValueError as e:
                InfoDialog(
                    master=self,
                    title="Stock Error",
                    header="Transaction Failed",
                    info=str(e),
                    posx=633,
                    posy=122
                )
                raise


    def build_item_tiles(self, parent, items):
        col_count = 4
        row = col = 0

        for item in items:
            tile = ItemTile(
                parent,
                item=item,
                on_click=lambda product=item: self.open_quantity_prompt(product)
            )

            tile.grid(row=row, column=col, padx=7, pady=7, sticky="nsew")

            self.item_tiles[item["id"]] = tile

            col += 1
            if col == col_count:
                col = 0
                row += 1


    def freeze_layout(self, widget):
        widget.grid_propagate(False)


    def unfreeze_layout(self, widget):
        widget.grid_propagate(True)


    def optionmenu_callback(self, choice):
        if choice == "All items":
            filtered = self.all_items
        else:
            filtered = [item for item in self.all_items if item["category"] == choice]

        self.filter_items(filtered)


    def search_items(self, query: str):
        query = query.strip().lower()

        if not query:
            self.filter_items(self.all_items)
            return

        filtered = [
            item for item in self.all_items
            if query in item["name"].lower()
            or query in item["id"].lower()
        ]

        self.filter_items(filtered)


    def filter_items(self, items_to_show):
        for tile in self.item_tiles.values():   # Hide all tiles first
            tile.grid_remove()

        col_count = 4
        row = col = 0

        for item in items_to_show:
            tile = self.item_tiles.get(item["id"])
            if not tile:
                continue

            tile.grid(row=row, column=col, padx=7, pady=7, sticky="nsew")

            col += 1
            if col == col_count:
                col = 0
                row += 1


    def fetch_items_for_ui(self):
        rows = self.repo.get_all_items() or []
        items = []

        for row in rows:
            barcode, name, category, qty, created_at, price, description = row
            
            items.append({
                "id": barcode,    # UI still uses "id"
                "name": name,
                "description": description,
                "category": category,
                "price": price,
                "stock": qty,
                "image": self.iconpath.get_icon_cache("product", (50, 50))
            })
        return items
    

    def get_ticket_row(self):
        if self.ticket_row_pool:
            return self.ticket_row_pool.pop()
        return TicketRow(self.ticket_items_frame)


    def release_ticket_row(self, row):
        row.pack_forget()
        self.ticket_row_pool.append(row)


    def update_ticket_rows(self, items):

        existing = set(self.active_ticket_rows.keys())
        incoming = set(items.keys())

        # Remove old
        for item_id in existing - incoming:
            row = self.active_ticket_rows.pop(item_id)
            self.release_ticket_row(row)

        # Add / update
        for item_id, entry in items.items():
            item = self.get_item_by_id(item_id)
            if not item:
                continue

            if item_id in self.active_ticket_rows:
                self.active_ticket_rows[item_id].update(item, entry["qty"])
            else:
                row = self.get_ticket_row()
                row.update(item, entry["qty"])
                row.pack(fill="x", pady=6)
                self.active_ticket_rows[item_id] = row


    def on_ticket_update(self, items):
        self.update_ticket_rows(items)
        self.update_checkout_orders()
        self.update_payment_panel()

        self.schedule_render()


    def add_to_ticket(self, product, qty=1):
        if qty <= 0:
            return

        item_id = product["id"]

        # quantity already in ticket
        current_qty = self.ticket_model.items.get(item_id, {}).get("qty", 0)

        # remaining stock
        remaining = product["stock"] - current_qty

        if qty > remaining:
            InfoDialog(
                master=self,
                title="Warning",
                header="Stock Warning",
                info=f"Only {remaining} item(s) remaining.",
                posx=632,
                posy=115
            )
            return

        self.ticket_model.add_item(product, qty)


    def refresh_ticket(self):
        existing_ids = set(self.ticket_rows.keys())
        new_ids = set(self.ticket_items.keys())

        # Remove deleted rows
        for item_id in existing_ids - new_ids:
            self.ticket_rows[item_id].destroy()
            del self.ticket_rows[item_id]

        # Add or update rows
        for item_id, entry in self.ticket_items.items():
            # item = entry["item"]
            item = self.get_item_by_id(item_id)
            qty = entry["qty"]

            if item_id in self.ticket_rows:
                self.ticket_rows[item_id].update_qty(qty)
            else:
                row = TicketRow(self.ticket_items_frame, item, qty)
                row.pack(fill="x", pady=6)
                self.ticket_rows[item_id] = row


    def clear_ticket(self) -> None:
        # Clear ticket data
        self.ticket_model.clear()

        # Reset checkout totals
        self.checkout_total = 0
        self.checkout_total_var.set("0.00")

        # Clear checkout orders UI
        if hasattr(self, "checkout_orders_inner"):
            for w in self.checkout_orders_inner.winfo_children():
                w.destroy()

        # Reset checkout flag so it rebuilds cleanly
        self.checkout_initialized = False

        # Only reset cash when checkout is active
        if self.view_manager.views.get("checkout") == self.checkout_view:
            if hasattr(self, "cash_entry") and self.cash_entry.winfo_exists():
                self.cash_received.set("")


    def update_item_tile_states(self):
        for item in self.all_items:
            item_id = item["id"]
            in_ticket = self.ticket_model.items.get(item_id, {}).get("qty", 0)
            remaining = item["stock"] - in_ticket

            tile = self.item_tiles.get(item_id)
            if tile:
                tile.set_disabled(remaining <= 0)


    def reload_items_after_scan(self):
        self.all_items = self.fetch_items_for_ui()

        for item in self.all_items:
            tile = self.item_tiles.get(item["id"])
            if tile:
                tile.update_item(item)

        self.schedule_render()


    def get_item_by_id(self, item_id):
        return next(
            (item for item in self.all_items if item["id"] == item_id),
            None
        )


    def complete_transaction(self):
        self.deduct_purchased_items()       # Deduct stock in DB
        self.reload_items_after_scan()      # Update Item Tiles
        self.clear_ticket()                 # IMPORTANT: clear ticket
        self.view_manager.show("main")      # Return to main screen
        self.schedule_render()


    def update_checkout_orders(self):
        self.calculate_checkout_total()
        self.checkout_total_var.set(f"{self.checkout_total:,.2f}")


    def update_payment_panel(self):
        self.refresh_cash_options()


    def back_to_main_menu(self):
        self.checkout_state = "panel"
        self.cash_status_var.set("")
        self.view_manager.show("main")
        self.after_idle(self.build_payment_panel)
        self.view_manager.hide("checkout")
        self.schedule_render()


    def open_checkout(self):
        self.calculate_checkout_total()
        self.checkout_total_var.set(f"{self.checkout_total:,.2f}")

        self.view_manager.hide("main")
        self.view_manager.show("checkout")

        # Do NOT rebuild everything
        self.schedule_render()


    # def open_checkout(self):
        # self.build_checkout_orders()
    #     # self.build_payment_panel()
    #     self.view_manager.hide("main")
    #     self.view_manager.show("checkout")
    #     self.schedule_render()

        
    def open_quantity_prompt(self, product):

        qty_window = ctk.CTkToplevel(self)
        qty_window.geometry("350x180+870+200")
        qty_window.title("Enter Quantity")
        qty_window.after(200, lambda: qty_window.iconbitmap(self.iconpath.get_icon_cache("window", icon_type="bitmap")))
        qty_window.transient(self)
        qty_window.grab_set()

        ctk.CTkLabel(
            qty_window, 
            text=product["name"],
            font=ctk.CTkFont(family="Poppins", size=20)
        ).pack(pady=(20, 0))

        qty_entry = ctk.CTkEntry(
            qty_window,
            font=ctk.CTkFont(family="Poppins", size=16),
            width=180,
            height=35,
            border_color="#2CC985",
            justify="center"
        )
        qty_entry.pack(pady=(15, 10))
        self.after(100, qty_entry.focus)

        def confirm():
            qty = qty_entry.get().strip()
            if not qty.isdigit():
                return

            qty = int(qty)
            if qty <= 0:
                return

            self.add_to_ticket(product, qty)
            qty_window.destroy()

        qty_entry.bind("<Return>", lambda e: confirm())


    def open_sidebar(self):
        if self.sidebar.winfo_ismapped():
            self.sidebar.grid_remove()
        else:
            self.sidebar.grid(row=0, column=0, rowspan=2, pady=(80, 0), sticky="nw")
            self.sidebar.lift()


    def open_account_pane(self, event):
        print("Account pane open.")


    def open_ticket_option_menu(self, event):
        print("Ticket options open.")


    def open_product_manager(self):
        if self.sidebar.winfo_ismapped():
            self.sidebar.grid_remove()
        ProductManagementWindow(self)


    def open_transaction_window(self):
        if self.sidebar.winfo_ismapped():
            self.sidebar.grid_remove()
        TransactionHistoryWindow(self, self.repo)


    def open_search_scan_window(self, event):
        ScanSearchItems(self, self.repo, on_search=self.search_items)


    def check_sidebar_click(self, event):

        if not self.sidebar.winfo_ismapped():
            return

        x1 = self.sidebar.winfo_rootx()
        y1 = self.sidebar.winfo_rooty()
        x2 = x1 + self.sidebar.winfo_width()
        y2 = y1 + self.sidebar.winfo_height()

        # If click outside sidebar
        if not (x1 <= event.x_root <= x2 and y1 <= event.y_root <= y2):
            self.sidebar.grid_remove()
        

    def compute_receipt(self):

        # Reset purchases so re-printing doesn't accumulate prior items
        self.purchase_list.clear()

        for item_id, entry in self.ticket_model.items.items():
            item = self.get_item_by_id(item_id)
            if not item:
                continue

            qty = entry["qty"]
            line_total = item["price"] * qty
            self.total += line_total
            item_name = item["name"]
            full_desc = f"{item_name} {item["description"]}"
            # print(f"\n{qty}  {full_desc}     {line_total}")
            self.purchase_list.append((qty, full_desc, line_total))

    
    def open_receipt_printing_window(self):

        self.compute_receipt()

        def generate_transaction_number():
            now = datetime.now()
            return now.strftime("%Y%m%d%H%M%S")

        def tailored_description_text(description):
            max_len = 21
            lines = [description[i:i+max_len] for i in range(0, len(description), max_len)]
            return "\n ".join(lines)
        
        def generate_receipt(purchases, **details):
            RECEIPT_WIDTH = 45

            global receipt
            receipt = ""

            receipt += details['name'].center(RECEIPT_WIDTH) + "\n"
            receipt += f"OWNED BY: {details['owner']}".center(RECEIPT_WIDTH) + "\n"
            receipt += f"VAT REG TIN: {details['vat_reg_tin']}".center(RECEIPT_WIDTH) + "\n"
            receipt += f"SERIAL NO: {details['serial_no']}".center(RECEIPT_WIDTH) + "\n"
            receipt += details['address'].center(RECEIPT_WIDTH) + "\n"

            receipt += "SALES INVOICE".center(RECEIPT_WIDTH) + "\n\n"
            receipt += "-" * RECEIPT_WIDTH + "\n"
            
            receipt += f" Payment Method: {details['payment_method']}\n"
            # receipt += f" CASHIER: {details['cashier_name']} {'TRAN#:':>15} {"4/0099423"}\n"
            transaction_no = generate_transaction_number()

            receipt += f" CASHIER: {details['cashier_name']} {'TRAN#:':>10} {transaction_no}\n"


            dt = datetime.now()
            formatted_date = f"{dt.month}/{dt.day}/{dt.year}"
            formatted_time = f"{dt.strftime('%I:%M:%S %p').lstrip('0')}"

            receipt += f" DATE: {formatted_date} {'TIME:':>16} {formatted_time}\n"
            receipt += "-" * RECEIPT_WIDTH + "\n"
            receipt += f" {'QTY':<7}{'DESCRIPTION':<29}{'AMOUNT':>7}\n\n"

            total_qty = 0
            total = 0

            for qty, desc, amount in purchases:
                total += amount
                total_qty += qty

                formatted_desc = tailored_description_text(desc)
                desc_lines = formatted_desc.split("\n")

                # First line
                receipt += f" {qty:<7}{desc_lines[0]:<29}{amount:>7,.2f}\n"

                # Wrapped description lines
                for line in desc_lines[1:]:
                    receipt += f"{'':<7}{line}\n"

            change = details["cash_received"] - total

            receipt += "-" * RECEIPT_WIDTH + "\n"
            receipt += f" {'Total QTY':<36}{total_qty:>7}\n"
            receipt += f" {'AMOUNT DUE':<36}{total:>7,.2f}\n"
            receipt += f" {'Cash':<36}{details['cash_received']:>7,.2f}\n"
            receipt += f" {'Change':<36}{change:>7,.2f}\n"
            receipt += "-" * RECEIPT_WIDTH + "\n"
            # receipt += details["address"].center(RECEIPT_WIDTH) + "\n"
            receipt += "Thank you for your purchase!".center(RECEIPT_WIDTH) + "\n"

            return receipt
        
        def on_generate_receipt(purchases):

            self.receipt_text_str = generate_receipt(
                purchases,
                name = "SPB ELECTRICAL SUPPLY",
                owner = "MICHAEL VINCENT GAYTANO",
                vat_reg_tin = "NONE",
                serial_no = "NONE",
                address = "SAN ANTONIO, SAN PASCUAL, BATANGAS",
                cashier_name = "mechelle",
                payment_method = "CASH",
                cash_received = float(self.cash_received.get())
            )

            text_receipt.delete("1.0", tk.END)
            text_receipt.insert(tk.END, self.receipt_text_str)


        def download_pdf():
            if not self.receipt_text_str:
                InfoDialog(
                    win,
                    title="Warning",
                    header="No Receipt",
                    info="Please generate a receipt first."
                )
                return

            file_path = RECEIPT_DIR

            c = canvas.Canvas(str(file_path), pagesize=LETTER)

            # Create text object (this preserves spacing)
            textobject = c.beginText()
            
            # if textobject.getY() < 50:
            #     c.drawText(textobject)
            #     c.showPage()
            #     textobject = c.beginText(50, 750)
            #     textobject.setFont("Courier", 10)

            textobject.setTextOrigin(50, 750)
            textobject.setFont("Courier", 8)  # MONOSPACED FONT

            for line in self.receipt_text_str.split("\n"):
                textobject.textLine(line)

            c.drawText(textobject)
            c.showPage()
            c.save()

            InfoDialog(
                win,
                title="Info",
                header="Download Complete",
                info="Receipt downloaded as receipt.pdf"
            )


        def on_close():
            win.grab_release()
            win.destroy()

        win = ctk.CTkToplevel(self.checkout_payment)
        win.geometry("500x620+500+5")
        win.transient(self.checkout_payment)
        win.grab_set()
        win.protocol("WM_DELETE_WINDOW", on_close)


        receipt_frame = ctk.CTkScrollableFrame(win)
        receipt_frame.pack(padx=10, pady=5, fill="both", expand=True)

        # Receipt output
        text_receipt = tk.Text(receipt_frame, height=30, width=59)
        text_receipt.grid(row=0, column=0, padx=10, pady=5)

        on_generate_receipt(self.purchase_list)

        ctk.CTkButton(win, text="Download as pdf", command=download_pdf).pack(pady=(10, 10))
