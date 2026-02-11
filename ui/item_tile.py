import customtkinter as ctk

CATEGORY_COLORS = {
    "Batteries":   "#E67E22",  # Orange – energy/power
    "Cables":      "#34495E",  # Dark blue-gray – wiring/tech
    "Cameras":     "#8E44AD",  # Purple – vision/optics/tech
    "Conduits":    "#7F8C8D",  # Gray – pipes/structure
    "Connectors":  "#16A085",  # Teal – connectivity
    "Enclosures":  "#2C3E50",  # Dark navy – protection/strength
    "Lights":      "#F1C40F",  # Yellow – illumination
    "Sensors":     "#27AE60",  # Green – detection/smart
    "Switches":    "#2980B9",  # Blue – control
    "Outlets":     "#C0392B"   # Red – power point
}


class ItemTile(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        item,
        on_click
    ):
        """
        item = {
            id, name, description, category,
            price, stock, image_path
        }
        """

        color = CATEGORY_COLORS.get(item["category"], CATEGORY_COLORS["Cables"])

        super().__init__(
            parent,
            fg_color=color,
            corner_radius=18,  # rounded
            # corner_radius=0,  # square
            height=235,
            width=161,
            cursor="hand2"
        )
        self.pack_propagate(False)

        self.item = item
        self.on_click = on_click
        
        # ================= TOP ROW =================
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=8, pady=(10, 4))

        thumb_lbl = ctk.CTkLabel(top, image=item["image"], text="")
        thumb_lbl.pack(side="top", padx=(0, 8), pady=(10, 14))

        # hover_color = self.darken_color(color, 0.12)

        # thumb_lbl.bind("<Enter>", lambda e: self.animate_color(thumb_lbl, color, hover_color))
        # thumb_lbl.bind("<Leave>", lambda e: self.animate_color(thumb_lbl, hover_color, color))

        # Name + description
        text_frame = ctk.CTkFrame(top, height=75, corner_radius=0, fg_color="transparent")
        text_frame.pack(fill="x", expand=True)
        text_frame.pack_propagate(False)

        self.name_lbl = ctk.CTkLabel(
            text_frame,
            text=item["name"],
            font=ctk.CTkFont(family="Poppins", size=16, weight="bold"),
            text_color="white",
            anchor="w"   
        )
        self.name_lbl.pack(fill="x")

        product_desc = item["description"]
        if len(product_desc) > 40:
            product_desc = product_desc[:37] + "..."

        desc_lbl = ctk.CTkLabel(
            text_frame,
            text=product_desc,
            font=ctk.CTkFont(family="Poppins", size=13),
            text_color="#EAEAEA",
            anchor="w",
            wraplength=140,
            justify="left"
        )
        desc_lbl.pack(fill="x")

        # ================= BOTTOM ROW =================
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="x", padx=8, pady=(0, 0))

        price_lbl = ctk.CTkLabel(
            bottom,
            text=f"₱{item['price']:.2f}",
            font=ctk.CTkFont(family="Poppins", size=15, weight="bold"),
            text_color="white"
        )
        price_lbl.pack(side="left")

        stock_color = "#2ECC71" if item["stock"] > 0 else "#E74C3C"
        
        self.stock_lbl = ctk.CTkLabel(
            self,
            text=f"STOCK {item['stock']}",
            fg_color=stock_color,
            corner_radius=8,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="white",
            width=80,
            height=28
        )
        self.stock_lbl.pack(side="right", padx=(0, 10), pady=(0, 5))

        # ================= CLICK BINDINGS =================
        for widget in (self, top, thumb_lbl, self.name_lbl, desc_lbl, bottom, price_lbl, self.stock_lbl):
            widget.bind("<Button-1>", self.handle_click)


    def update_item(self, item):
        self.item = item
        stock_color = "#2ECC71" if item["stock"] > 0 else "#E74C3C"
        self.stock_lbl.configure(text=f"STOCK {item['stock']}", fg_color=stock_color)
        self.name_lbl.configure(text=item["name"])


    def handle_click(self, event):
        self.on_click(self.item)


    def on_hover(self, event):
        self.configure(fg_color=self.hover_color)


    def on_leave(self, event):
        self.configure(fg_color=self.default_color)


    def darken_color(self, hex_color, factor=0.12):
        hex_color = hex_color.lstrip("#")
        r, g, b = (int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r = int(r * (1 - factor))
        g = int(g * (1 - factor))
        b = int(b * (1 - factor))
        return f"#{r:02x}{g:02x}{b:02x}"
    

    def interpolate_color(self, c1, c2, t):
        return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


    def rgb_to_hex(self, rgb):
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
    
    
    def animate_color(self, widget, start, end, steps=8, delay=15):
        start_rgb = self.hex_to_rgb(start)
        end_rgb = self.hex_to_rgb(end)

        def step(i=0):
            if i > steps:
                return
            t = i / steps
            color = self.rgb_to_hex(self.interpolate_color(start_rgb, end_rgb, t))
            widget.configure(fg_color=color)
            widget.after(delay, step, i + 1)

        step()
