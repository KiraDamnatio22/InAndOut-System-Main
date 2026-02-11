import customtkinter as ctk
from db.paths import IconPath
from ui.add_product_window import AddProductWindow
from ui.scan_window import ScanWindow



class ProductManagementWindow(ctk.CTkToplevel):

    def __init__(self, master):
        super().__init__(master)

        self.title("Manage Product")
        self.geometry("650x400+400+190")
        self.resizable(False, False)
        self.overrideredirect(True)
        self.grab_set()
        self.configure(fg_color="#2CC985")

        self.iconpath = IconPath()
        self.build_ui()


    def build_ui(self):
        self.grid_columnconfigure(1, weight=1)

        # CLOSE BUTTON
        ctk.CTkButton(
            self,
            text="",
            image=self.iconpath.get_icon_cache("close_w", (28, 28)),
            width=40,
            height=35,
            fg_color="#DD4141",
            hover_color="#FF6464",
            command=self.close_window
        ).grid(row=0, column=2, columnspan=3, padx=(0, 18), pady=(18, 0))

        ctk.CTkLabel(
            self, 
            text="", 
        ).grid(row=1, column=1, sticky="nsew")

        # PRODUCT LABEL
        ctk.CTkLabel(
            self, 
            text="Manage Product ", 
            image=self.iconpath.get_icon_cache("product", (35, 35)),
            text_color="#FFFFFF",
            font=ctk.CTkFont(family="Poppins", size=24, weight="bold"),
            compound="right",
        ).grid(row=1, column=0, padx=(35, 0), pady=(0, 0))

        ctk.CTkFrame(
            self,
            border_width=0.8,
            fg_color="#FFFFFF",
            height=1
        ).grid(row=2, column=0, columnspan=2, padx=(35, 0), pady=(10, 20), sticky="ew")

        ctk.CTkButton(
            self,
            width=180,
            text="Add Product",
            text_color="#14A969",
            font=ctk.CTkFont(family="Poppins", size=14, weight="bold"),
            fg_color="#FFFFFF",
            hover_color="#FFFFFF",
            command=self.open_add_product_window,
        ).grid(row=3, column=0, columnspan=2, padx=(35, 0), pady=(20, 0), sticky="w")

        ctk.CTkButton(
            self,
            width=180,
            text="Replenish Stocks",
            text_color="#14A969",
            font=ctk.CTkFont(family="Poppins", size=14, weight="bold"),
            fg_color="#FFFFFF",
            hover_color="#FFFFFF",
            command=self.open_replenishment_stock_window,
        ).grid(row=4, column=0, columnspan=2, padx=(35, 0), pady=(18, 0), sticky="w")


    def open_add_product_window(self):
        self.grab_release()
        AddProductWindow(self, self.master.repo, self.master.build_item_tiles)


    def open_replenishment_stock_window(self):
        self.grab_release()
        self.lower()
        ScanWindow(
            self, 
            self.master.repo,
            on_stock_updated=self.master.reload_items_after_scan
        )


    def close_window(self):
        self.grab_release()
        self.destroy()