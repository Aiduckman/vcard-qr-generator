"""Generate icon.icns for vCard QR Generator.

Renders a stylized QR code onto a soft gradient with macOS-style rounded
corners, then runs iconutil to produce icon.icns.
"""
import subprocess
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageDraw

HERE = Path(__file__).parent
ICONSET = HERE / "icon.iconset"
ICONSET.mkdir(exist_ok=True)

CANVAS = 1024
RADIUS = 224          # ~Big Sur+ corner radius for 1024px icons
PADDING = 110         # space around QR inside the rounded square

# Soft cool-blue gradient + deep navy QR — readable but not stark
BG_TOP = (244, 248, 255)
BG_BOT = (208, 220, 240)
QR_COLOR = (28, 38, 76)

# 1) Build the QR
qr = qrcode.QRCode(
    version=None,
    error_correction=ERROR_CORRECT_H,
    box_size=20,
    border=0,
)
qr.add_data(
    "BEGIN:VCARD\nVERSION:3.0\n"
    "FN:vCard QR Generator\n"
    "NOTE:Built locally with py2app\n"
    "END:VCARD"
)
qr.make(fit=True)

qr_img = qr.make_image(
    image_factory=StyledPilImage,
    module_drawer=RoundedModuleDrawer(),
    color_mask=SolidFillColorMask(back_color=(255, 255, 255), front_color=QR_COLOR),
).convert("RGBA")

# 2) Vertical gradient background
bg = Image.new("RGB", (CANVAS, CANVAS), BG_TOP)
draw = ImageDraw.Draw(bg)
for y in range(CANVAS):
    t = y / (CANVAS - 1)
    r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
    g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
    b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
    draw.line([(0, y), (CANVAS, y)], fill=(r, g, b))
bg = bg.convert("RGBA")

# 3) Inner white card behind QR — gives the QR breathing room
card_inset = 70
card = Image.new("L", (CANVAS, CANVAS), 0)
ImageDraw.Draw(card).rounded_rectangle(
    [(card_inset, card_inset), (CANVAS - 1 - card_inset, CANVAS - 1 - card_inset)],
    radius=140,
    fill=255,
)
white_layer = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
bg.paste(white_layer, (0, 0), card)

# 4) Resize QR and paste centered
qr_size = CANVAS - 2 * PADDING
qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
bg.paste(qr_img, (PADDING, PADDING), qr_img)

# 5) Apply outer rounded mask for the macOS squircle look
mask = Image.new("L", (CANVAS, CANVAS), 0)
ImageDraw.Draw(mask).rounded_rectangle(
    [(0, 0), (CANVAS - 1, CANVAS - 1)], radius=RADIUS, fill=255
)

icon = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
icon.paste(bg, (0, 0), mask)

icon.save(HERE / "icon_1024.png")

# 6) Generate iconset PNGs
sizes = [
    (16,   "icon_16x16.png"),
    (32,   "icon_16x16@2x.png"),
    (32,   "icon_32x32.png"),
    (64,   "icon_32x32@2x.png"),
    (128,  "icon_128x128.png"),
    (256,  "icon_128x128@2x.png"),
    (256,  "icon_256x256.png"),
    (512,  "icon_256x256@2x.png"),
    (512,  "icon_512x512.png"),
    (1024, "icon_512x512@2x.png"),
]
for size, name in sizes:
    icon.resize((size, size), Image.LANCZOS).save(ICONSET / name)

# 7) Run iconutil
subprocess.run(
    ["iconutil", "-c", "icns", str(ICONSET), "-o", str(HERE / "icon.icns")],
    check=True,
)
print(f"OK: {(HERE / 'icon.icns').stat().st_size} bytes")
