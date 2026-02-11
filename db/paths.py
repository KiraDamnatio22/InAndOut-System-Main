import tkinter as tk

from pathlib import Path
import customtkinter as ctk
from PIL import Image, ImageTk


BASE_DIR = Path(__file__).resolve().parent
LABEL_DIR = BASE_DIR / "barcodes"
DB_DIR = BASE_DIR / "inventory.db"
ICONS_DIR = BASE_DIR / "assets" / "icons"
BITMAP_DIR = BASE_DIR / "assets" / "bitmap_icons"
RECEIPT_DIR = BASE_DIR / "receipts" / "receipt.pdf"


# Bitmap Icons
ADD_PRODUCT_ICO = BITMAP_DIR / "add_product.ico"
INFO_ICO = BITMAP_DIR / "info.ico"
UPDATE_ICO = BITMAP_DIR / "edit.ico"
SEARCH_ICO = BITMAP_DIR / "search.ico"
SYSTEM_ICO = BITMAP_DIR / "system.ico"
WARNING_ICO = BITMAP_DIR / "warning.ico"
WINDOW_ICO = BITMAP_DIR / "window.ico"

# Icons
ACCOUNT = ICONS_DIR / "account_circle_gy.png"
BACK_ARROW = ICONS_DIR / "back_arrow.png"
BACK_IOS = ICONS_DIR / "back_ios.png"
CHECK = ICONS_DIR / "check.png"
CHECK_CIRCLE = ICONS_DIR / "check_circle.png"
CLOSE_B = ICONS_DIR / "close_b.png"
CLOSE_W = ICONS_DIR / "close_w.png"
DELETE = ICONS_DIR / "delete.png"

DOWNLOAD_B = ICONS_DIR / "download_b.png"
DOWNLOAD_W = ICONS_DIR / "download_w.png"
DOWNLOAD_DONE_B = ICONS_DIR / "download_done_b.png"
DOWNLOAD_DONE_W = ICONS_DIR / "download_done_w.png"
DOWNLOAD_OFFLINE_B = ICONS_DIR / "offline_download_b.png"
DOWNLOAD_OFFLINE_W = ICONS_DIR / "offline_download_w.png"

EMAIL_W = ICONS_DIR / "email_w.png"
EMAIL_B = ICONS_DIR / "email_b.png"

GO_IOS = ICONS_DIR / "go_ios.png"
HOME_W = ICONS_DIR / "home_w.png"
HOME_B = ICONS_DIR / "home_b.png"
MENU = ICONS_DIR / "menu.png"
MORE_VERT = ICONS_DIR / "more_vert.png"
SAVE = ICONS_DIR / "save.png"
SCANNER = ICONS_DIR / "scanner.png"
SEARCH = ICONS_DIR / "search.png"
SETTINGS = ICONS_DIR / "settings.png"
SHOPPING_CART_W = ICONS_DIR / "shopping_cart_w.png"
SHOPPING_CART_B = ICONS_DIR / "shopping_cart_b.png"
STAR = ICONS_DIR / "star.png"
PAYMENTS_W = ICONS_DIR / "payments_w.png"
PAYMENTS_B = ICONS_DIR / "payments_b.png"
PRICE_CHECK_W = ICONS_DIR / "price_check_w.png"
PRICE_CHECK_B = ICONS_DIR / "price_check_b.png"
PRINT_W = ICONS_DIR / "print_w.png"
PRINT_B = ICONS_DIR / "print_b.png"
PRODUCT = ICONS_DIR / "product.png"

class IconPath():

    def __init__(self):
        self.title = "Where you find all icons."
        self.icon_cache = {}
        self.bitmap_icon_cache = {}


    def get_icons(self, icon_key, icon_size):
        icons = {
            "account": ctk.CTkImage(light_image=Image.open(ACCOUNT), size=icon_size),
            "back_arrow": ctk.CTkImage(light_image=Image.open(BACK_ARROW), size=icon_size),
            "back_ios": ctk.CTkImage(light_image=Image.open(BACK_IOS), size=icon_size),
            "check": ctk.CTkImage(light_image=Image.open(CHECK), size=icon_size),
            "check_circle": ctk.CTkImage(light_image=Image.open(CHECK_CIRCLE), size=icon_size),
            "close_b": ctk.CTkImage(light_image=Image.open(CLOSE_B), size=icon_size),
            "close_w": ctk.CTkImage(light_image=Image.open(CLOSE_W), size=icon_size),
            "delete": ctk.CTkImage(light_image=Image.open(DELETE), size=icon_size),

            # DOWNLOAD ICONS
            "download_w": ctk.CTkImage(light_image=Image.open(DOWNLOAD_W), size=icon_size),
            "download_b": ctk.CTkImage(light_image=Image.open(DOWNLOAD_B), size=icon_size),
            "download_done_w": ctk.CTkImage(light_image=Image.open(DOWNLOAD_DONE_W), size=icon_size),
            "download_done_b": ctk.CTkImage(light_image=Image.open(DOWNLOAD_DONE_B), size=icon_size),
            "download_offline_w": ctk.CTkImage(light_image=Image.open(DOWNLOAD_OFFLINE_W), size=icon_size),
            "download_offline_b": ctk.CTkImage(light_image=Image.open(DOWNLOAD_OFFLINE_B), size=icon_size),
            
            "email_w": ctk.CTkImage(light_image=Image.open(EMAIL_W), size=icon_size),
            "email_b": ctk.CTkImage(light_image=Image.open(EMAIL_B), size=icon_size),
            "go_ios": ctk.CTkImage(light_image=Image.open(GO_IOS), size=icon_size),
            "home_w": ctk.CTkImage(light_image=Image.open(HOME_W), size=icon_size),
            "home_b": ctk.CTkImage(light_image=Image.open(HOME_B), size=icon_size),
            "menu": ctk.CTkImage(light_image=Image.open(MENU), size=icon_size),
            "more_vert": ctk.CTkImage(light_image=Image.open(MORE_VERT), size=icon_size),
            "save": ctk.CTkImage(light_image=Image.open(SAVE), size=icon_size),
            "scanner": ctk.CTkImage(light_image=Image.open(SCANNER), size=icon_size),
            "search": ctk.CTkImage(light_image=Image.open(SEARCH), size=icon_size),
            "settings": ctk.CTkImage(light_image=Image.open(SETTINGS), size=icon_size),
            "shopping_cart_w": ctk.CTkImage(light_image=Image.open(SHOPPING_CART_W), size=icon_size),
            "shopping_cart_b": ctk.CTkImage(light_image=Image.open(SHOPPING_CART_B), size=icon_size),
            "star": ctk.CTkImage(light_image=Image.open(STAR), size=icon_size),
            "payments_w": ctk.CTkImage(light_image=Image.open(PAYMENTS_W), size=icon_size), 
            "payments_b": ctk.CTkImage(light_image=Image.open(PAYMENTS_B), size=icon_size),
            "price_check_w": ctk.CTkImage(light_image=Image.open(PRICE_CHECK_W), size=icon_size),
            "price_check_b": ctk.CTkImage(light_image=Image.open(PRICE_CHECK_B), size=icon_size),
            "print_w": ctk.CTkImage(light_image=Image.open(PRINT_W), size=icon_size),
            "print_b": ctk.CTkImage(light_image=Image.open(PRINT_B), size=icon_size),
            "product": ctk.CTkImage(light_image=Image.open(PRODUCT), size=icon_size),
        }
        return icons[icon_key]
    

    def get_bitmap_icons(self, icon_key):
        bitmap_icons = {
            "add_product": ADD_PRODUCT_ICO,
            "info": INFO_ICO,
            "update": UPDATE_ICO,
            "search": SEARCH_ICO,
            "system": SYSTEM_ICO,
            "warning": WARNING_ICO,
            "window": WINDOW_ICO,
        }
        return bitmap_icons[icon_key]
    

    def get_icon_cache(self, name, size=(35, 35), icon_type="regular"):
        key = (name, size)

        if icon_type == "regular":
            if key in self.icon_cache:
                return self.icon_cache[key]
            
            icon = self.get_icons(name, size)
            self.icon_cache[key] = icon

        elif icon_type == "bitmap":
            if key in self.bitmap_icon_cache:
                return self.bitmap_icon_cache[key]
            
            icon = self.get_bitmap_icons(name)
            self.bitmap_icon_cache[key] = icon

        return icon
    
    
    def __repr__(self):
        return self.title









"""

BASE COLOR: (self.sidebar) 41DD99
             Text Colors: 1F2933, 0F172A
    Secondary/Muted Text: 4B5563, 475569
          Headers/Titles: 064E3B, 065F46, 0B2545
         Primary Buttons: B(0F766E) - T(FFFFFF)
                          B(064E3B) - T(ECFDF5)
       Secondary Buttons: B(ECFDF5) - T(065F46) - Border(34D399)
    Icons, Active States, Links: 22D3EE, 34D399

COMBO SAMPLE: 
            Frame BG: 41DD99
            Header T: 064E3B
              Body T: 1F2933
         Secondary T: 475569
         Primary Btn: 0F766E
            Button T: FFFFFF
         Accent/Icon: 34D399

"""