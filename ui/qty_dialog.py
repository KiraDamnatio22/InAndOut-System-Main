import customtkinter as ctk

from ui.popups import InfoDialog


class QuantityDialog(ctk.CTkToplevel):
    def __init__(self, master, max_stock):
        super().__init__(master)
        self.title("Enter Quantity")
        self.geometry("350x200+550+240")
        self.resizable(False, False)
        self.grab_set()  # modal
        self.focus_force()

        self.max_stock = max_stock
        self.qty = None

        # Label
        ctk.CTkLabel(
            self,
            text=f"Enter quantity (Max: {self.max_stock}):",
            font=ctk.CTkFont(size=16)
        ).pack(pady=(20, 10))

        # Entry
        self.entry = ctk.CTkEntry(self, width=100, font=ctk.CTkFont(size=16))
        self.entry.pack()
        self.after(150, self.entry.focus_set)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="OK", width=80, command=self.on_ok).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", width=80, command=self.on_cancel).pack(side="right", padx=5)

        self.bind("<Return>", lambda e: self.on_ok())
        self.bind("<Escape>", lambda e: self.on_cancel())

    def on_ok(self):
        try:
            value = int(self.entry.get())
            if value <= 0 or value > self.max_stock:
                raise ValueError
            self.qty = value
            self.destroy()
        except ValueError:
            InfoDialog(
                master=self,
                title="Warning",
                header="Invalid value",
                info=f"Value must not exceed {self.max_stock}",
                info_color="red",
                is_needed=False,
                posx=495,
                posy=250
            )
            self.entry.delete(0, "end")
            self.entry.focus_set()

    def on_cancel(self):
        self.qty = None
        self.destroy()
