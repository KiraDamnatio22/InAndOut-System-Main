import customtkinter as ctk
from db.paths import IconPath
from ui.barcode_utils import generate_code128_image

class AddProductWindow(ctk.CTkToplevel):
    def __init__(self, master, repo, on_product_creation=None):
        super().__init__(master)

        self.iconpath = IconPath()
        self.after(200, lambda: self.iconbitmap(self.iconpath.get_icon_cache("add_product", icon_type="bitmap")))

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.title("Add Product")
        self.geometry("700x450+275+195")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.repo = repo
        self.on_product_creation = on_product_creation

        self.name_var = ctk.StringVar()
        self.product_category_var = ctk.StringVar(value="-- Select --")
        self.barcode_category_var = ctk.StringVar(value="-- Select --")
        self.price_var = ctk.StringVar()

        self.build_ui()

    def build_ui(self):
        # PRODUCT NAME
        ctk.CTkLabel(
            self, 
            text="Product Name", 
            font=ctk.CTkFont(family="Poppins", size=16)
        ).grid(row=0, column=0, padx=(5, 0), pady=(45, 4), ipadx=60)

        product = ctk.CTkEntry(
            self, 
            textvariable=self.name_var, 
            font=ctk.CTkFont(family="Poppins", size=13),
            width=300,
            height=30,
            justify="center"
        )
        product.grid(row=0, column=1, padx=(0, 0), pady=(45, 4))
        self.after(150, product.focus_set)

        # PRODUCT CATEGORY
        product_categories = ["Batteries", "Cables", "Cameras", "Conduits", "Connectors", "Enclosures", "Lights", "Sensors", "Switches", "Outlets"]
        ctk.CTkLabel(
            self,
            text="Product Category",
            font=ctk.CTkFont(family="Poppins", size=16)
        ).grid(row=1, column=0, padx=(5, 0), pady=(12, 4), ipadx=60)

        ctk.CTkOptionMenu(
            self,
            values=product_categories,
            font=ctk.CTkFont(family="Poppins", size=14),
            text_color="#323232",
            variable=self.product_category_var,
            fg_color="#FFFFFF",
            anchor="center",
            width=160
        ).grid(row=1, column=1, padx=(0, 0), pady=(12, 4))

        # BARCODE CATEGORY
        ctk.CTkLabel(
            self, 
            text="Barcode Category", 
            font=ctk.CTkFont(family="Poppins", size=16)
        ).grid(row=2, column=0, padx=(5, 0), pady=(12, 4), ipadx=60)

        ctk.CTkOptionMenu(
            self,
            values=["Electrical",],
            font=ctk.CTkFont(family="Poppins", size=14),
            text_color="#323232",
            variable=self.barcode_category_var,
            fg_color="#FFFFFF",
            anchor="center",
            width=160
        ).grid(row=2, column=1, padx=(0, 0), pady=(12, 4))

        # PRICE
        ctk.CTkLabel(
            self, 
            text="Price", 
            font=ctk.CTkFont(family="Poppins", size=16)
        ).grid(row=3, column=0, padx=(5, 0), pady=(12, 4), ipadx=60)

        ctk.CTkEntry(
            self, 
            textvariable=self.price_var, 
            width=220,
            justify="center"
        ).grid(row=3, column=1, padx=(0, 0), pady=(12, 4))

        # DESCRIPTION
        ctk.CTkLabel(
            self, 
            text="Description", 
            font=ctk.CTkFont(family="Poppins", size=16)
        ).grid(row=4, column=0, padx=(5, 0), pady=(12, 0), ipadx=60)

        self.description_entry = ctk.CTkTextbox(self, height=80, width=350, border_width=2, corner_radius=0)
        self.description_entry.grid(row=4, column=1, padx=(0, 0), pady=(30, 0))

        # SAVE PRODUCT BUTTON
        ctk.CTkButton(
            self,
            text="Save Product",
            font=ctk.CTkFont(family="Poppins", size=14, weight="bold"),
            fg_color="#2CC985",
            width=145,
            height=38,
            command=self.save_product,
            corner_radius=0
        ).grid(row=5, column=1, padx=(5, 0), pady=(35, 0))

    def save_product(self):
        barcode = self.repo.create_item(
            name=self.name_var.get(),
            product_category=self.product_category_var.get(),
            barcode_category=self.barcode_category_var.get(),
            price=float(self.price_var.get()),
            description=self.description_entry.get("0.0", "end").strip()
        )

        generate_code128_image(barcode, self.name_var.get())
        # self.master.master.refresh_items()
        self.master.master.reload_items_after_scan()
        self.after_creation_close()

    def after_creation_close(self):
        self.on_closing()

        if callable(self.on_product_creation):
            all_items = self.master.master.fetch_items_for_ui()
            self.on_product_creation(self.master.master.items_frame, all_items)

    def on_closing(self):
        self.grab_release()
        self.destroy()
        print("ADD PRODUCT WINDOW CLOSED.")
