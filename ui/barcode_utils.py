import barcode
from barcode.writer import ImageWriter
from pathlib import Path
from db.paths import LABEL_DIR

BARCODE_DIR = Path("barcodes")
BARCODE_DIR.mkdir(exist_ok=True)

def generate_code128_image(code: str, product_name: str):
    code128 = barcode.get_barcode_class("code128")

    writer = ImageWriter()

    writer.set_options({
        "module_width": 0.2,
        "module_height": 15,
        "font_size": 12,
        "text_distance": 4,
        "quiet_zone": 3,
        "dpi": 300
    })

    barcode_obj = code128(code, writer=writer)

    file_path = LABEL_DIR / product_name
    barcode_obj.save(str(file_path))
