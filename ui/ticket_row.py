# import customtkinter as ctk
# # from sympy import expand

# class TicketRow(ctk.CTkFrame):
#     def __init__(self, parent, item, qty):
#         super().__init__(parent, fg_color="transparent")

#         self.grid_columnconfigure((0), weight=1)

#         left = ctk.CTkFrame(self, fg_color="transparent")
#         left.grid(row=0, column=0, sticky="w", columnspan=2)

#         ctk.CTkLabel(
#             left,
#             text=item["name"],
#             text_color="#2E2E2E",
#             font=ctk.CTkFont(family="Poppins", size=16, weight="bold"),
#             anchor="w"
#         ).pack(anchor="w", padx=(6, 0))

#         ctk.CTkLabel(
#             left,
#             text=item["description"],
#             font=ctk.CTkFont(family="Poppins", size=13),
#             text_color="#777",
#             anchor="w"
#         ).pack(anchor="w", padx=(6, 0))

#         self.insert_divider(left)

#         right = ctk.CTkFrame(self, fg_color="transparent")
#         right.grid(row=0, column=1, sticky="ew", padx=10, pady=(0, 10))

#         self.qty_label= ctk.CTkLabel(
#             right,
#             text=f"x{qty}",
#             font=ctk.CTkFont(family="Poppins", size=16, weight="bold"),
#             anchor="nw"
#         )
#         self.qty_label.pack(side="left", anchor="w", padx=(0, 50))

#         ctk.CTkLabel(
#             right,
#             text=f"{item['price'] * qty:.2f}",
#             font=ctk.CTkFont(family="Poppins", size=15),
#             anchor="nw"
#         ).pack(side="right", anchor="e")

#     def insert_divider(self, master):
#         divider = ctk.CTkFrame(master, border_width=0.8, fg_color="transparent", height=2, width=600)
#         divider.pack(pady=(12, 0))
#         divider.pack_propagate(False)

#     def update_qty(self, qty):
#         self.qty = qty
#         self.qty_label.configure(text=f"×{qty}")





import customtkinter as ctk

class TicketRow(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")

        self.item_id = None
        self.qty = 0

        self.grid_columnconfigure(0, weight=1)

        # LEFT
        self.left = ctk.CTkFrame(self, fg_color="transparent")
        self.left.grid(row=0, column=0, sticky="w", columnspan=2)

        self.name_label = ctk.CTkLabel(
            self.left,
            text="",
            text_color="#2E2E2E",
            font=ctk.CTkFont(family="Poppins", size=16, weight="bold"),
            anchor="w"
        )
        self.name_label.pack(anchor="w", padx=(6, 0))

        self.desc_label = ctk.CTkLabel(
            self.left,
            text="",
            font=ctk.CTkFont(family="Poppins", size=13),
            text_color="#777",
            anchor="w"
        )
        self.desc_label.pack(anchor="w", padx=(6, 0))

        self.insert_divider(self.left)

        # RIGHT
        self.right = ctk.CTkFrame(self, fg_color="transparent")
        self.right.grid(row=0, column=1, sticky="ew", padx=10, pady=(0, 10))

        self.qty_label = ctk.CTkLabel(
            self.right,
            text="×0",
            font=ctk.CTkFont(family="Poppins", size=16, weight="bold"),
            anchor="nw"
        )
        self.qty_label.pack(side="left", padx=(0, 50))

        self.price_label = ctk.CTkLabel(
            self.right,
            text="0.00",
            font=ctk.CTkFont(family="Poppins", size=15),
            anchor="nw"
        )
        self.price_label.pack(side="right")


    def update(self, item, qty):
        self.item_id = item["id"]
        self.qty = qty

        self.name_label.configure(text=item["name"])
        self.desc_label.configure(text=item["description"])
        self.qty_label.configure(text=f"×{qty}")
        self.price_label.configure(text=f"{item['price'] * qty:.2f}")


    def insert_divider(self, master):
        divider = ctk.CTkFrame(
            master,
            border_width=0.8,
            fg_color="transparent",
            height=2,
            width=600
        )
        divider.pack(pady=(12, 0))
        divider.pack_propagate(False)
