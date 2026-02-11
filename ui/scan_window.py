from turtle import update
import customtkinter as ctk
from db.paths import IconPath
from ui.popups import InfoDialog


class ScanWindow(ctk.CTkToplevel):

    def __init__(self, master, repo, on_stock_updated=None):
        super().__init__(master)

        self.iconpath = IconPath()
        self.after(200, lambda: self.iconbitmap(self.iconpath.get_icon_cache("search", icon_type="bitmap")))

        self.title("Scan Product")
        self.geometry("450x300+490+230")
        self.resizable(False, False)
        self.configure(fg_color="#E9E5E5")
        self.transient(master)
        self.grab_set()
        self.lift()

        self.repo = repo
        self.on_stock_updated = on_stock_updated
        self.scanned_barcode = ""
        self.updater_toplevel = None

        self.bind("<Key>", self.handle_scan_input)

        self.inner_frame = ctk.CTkFrame(self, fg_color="#F4F3F3", border_width=1)
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
                
                self.open_product_stock_updater(self.item)

            # Reset buffer
            self.scanned_barcode = ""
            return

        # Ignore special keys
        if len(event.char) == 1:
            self.scanned_barcode += event.char

    def update_stock(self):
        if not hasattr(self, "item"):
            return

        try:
            new_qty = int(self.qty_var.get())
        except:
            return

        self.repo.update_stock(
            self.item["id"],
            new_qty
        )
        # self.master.master.refresh_items()
        self.master.master.reload_items_after_scan()
        self.destroy()

    def open_product_stock_updater(self, product):
        if self.updater_toplevel and self.updater_toplevel.winfo_exists():
            self.updater_toplevel.focus()
            return

        self.updater_toplevel = ctk.CTkToplevel(self)
        self.updater_toplevel.geometry("490x340+470+200")
        self.updater_toplevel.configure(fg_color="#FFFFFF")

        self.updater_toplevel.transient(self)
        self.updater_toplevel.grab_set()
        self.updater_toplevel.focus_force()

        self.updater_toplevel.protocol("WM_DELETE_WINDOW", self.updater_toplevel_on_close)
        
        # self.item = self.repo.get_item_by_barcode(barcode.strip())
        self.item = product

        product_frame = ctk.CTkFrame(self.updater_toplevel, fg_color="#FFFFFF")
        product_frame.pack(fill="both", expand=True, padx=3, pady=3)

        ctk.CTkLabel(
            product_frame, 
            text=f"stock: {self.item["stock"]}",
            font=ctk.CTkFont(family="Poppins", size=16, weight="normal"),
            text_color="#3E3E3E"
        ).pack(anchor="e", padx=5, pady=5)

        ctk.CTkLabel(
            product_frame, 
            text="",
            image=self.iconpath.get_icon_cache("product", (60, 60)),
            width=60,
            height=60,
            fg_color="lightgreen"
        ).pack(padx=5, pady=(25, 5))

        ctk.CTkLabel(
            product_frame, 
            text=self.item["name"],
            font=ctk.CTkFont(family="Poppins", size=22, weight="bold")
        ).pack(padx=5, pady=(5, 0))

        ctk.CTkLabel(
            product_frame, 
            text=self.item["description"],
            font=ctk.CTkFont(family="Poppins", size=16, weight="normal"),
            text_color="#3E3E3E"
        ).pack(padx=5, pady=5)

        ctk.CTkLabel(
            product_frame, 
            text=f"Add stock",
            font=ctk.CTkFont(family="Poppins", size=18, weight="normal"),
        ).pack(padx=5, pady=(25, 0))

        self.new_stock = ctk.CTkEntry(
            product_frame,
            width=250,
            height=35,
            border_color="lightgreen",
            font=("Poppins", 16)
        )
        self.new_stock.pack(padx=5, pady=(5, 0))

        self.updater_toplevel.after(10, self.new_stock.focus_set)
        self.new_stock.bind("<Return>", lambda event, id=self.item["id"]: self.update_product_stock(event, id))
    
    def update_product_stock(self, event, product_id):
        added_stock = self.new_stock.get().strip()

        if not added_stock.isdigit():
            InfoDialog(
                self.updater_toplevel,
                title="Warning",
                header="Invalid value",
                info="Stock must be a number",
                info_color="red",
                is_needed=False,
                posx=540,
                posy=365
            )
            self.new_stock.delete(0, "end")
            return
        
        added_stock = int(added_stock)
        
        if added_stock <= 0:
            InfoDialog(
                self.updater_toplevel,
                title="Warning",
                header="Invalid value",
                info="Value must be higher than 0",
                info_color="red",
                is_needed=False,
                posx=540,
                posy=365
            )
            self.new_stock.delete(0, "end")
            return
        
        else:
            total_new_stock = self.item["stock"] + added_stock

            dialog = InfoDialog(
                self.updater_toplevel,
                title="Info",
                header=f"Added  x{added_stock}  {self.item['name']}",
                info=f"New stock: {total_new_stock}",
                posx=540,
                posy=290
            )
            self.updater_toplevel.wait_window(dialog)
            self.repo.record_product_stock_in(product_id, added_stock)
            self.after_update_close()


    def after_update_close(self):
        self.updater_toplevel_on_close()

        if callable(self.on_stock_updated):
            self.on_stock_updated()


    def updater_toplevel_on_close(self):
        self.updater_toplevel.destroy()
        self.updater_toplevel = None

        self.focus_force()
        self.grab_set()

    def close_window(self):
        self.grab_release()
        self.destroy()
