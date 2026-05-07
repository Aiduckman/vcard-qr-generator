"""Generate app icons for vCard QR Generator (cross-platform).

Renders a stylized QR code onto a soft gradient with macOS-style rounded
corners, then writes:

  - icon_1024.png   master preview, used in README
  - icon.png        512x512, for Linux desktop entries / PyInstaller --icon
  - icon.ico        multi-size Windows icon (PyInstaller --icon on Win)
  - icon.icns       macOS icon (only if running on macOS — uses iconutil)

Run on each target platform; PyInstaller and py2app each pick the right file.
"""
import platform
import shutil
import subprocess
from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import SolidFillColorMask
from PIL import Image, ImageDraw

HERE = Path(__file__).parent

CANVAS = 1024
RADIUS = 224
PADDING = 110

BG_TOP = (244, 248, 255)
BG_BOT = (208, 220, 240)
QR_COLOR = (28, 38, 76)


def build_master() -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,
        box_size=20,
        border=0,
    )
    qr.add_data(
        "BEGIN:VCARD\nVERSION:3.0\n"
        "FN:vCard QR Generator\n"
        "NOTE:Built locally\n"
        "END:VCARD"
    )
    qr.make(fit=True)
    qr_img = qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        color_mask=SolidFillColorMask(
            back_color=(255, 255, 255), front_color=QR_COLOR
        ),
    ).convert("RGBA")

    # Vertical gradient background
    bg = Image.new("RGB", (CANVAS, CANVAS), BG_TOP)
    draw = ImageDraw.Draw(bg)
    for y in range(CANVAS):
        t = y / (CANVAS - 1)
        c = tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * t) for i in range(3))
        draw.line([(0, y), (CANVAS, y)], fill=c)
    bg = bg.convert("RGBA")

    # Inner white rounded card
    card_inset = 70
    card = Image.new("L", (CANVAS, CANVAS), 0)
    ImageDraw.Draw(card).rounded_rectangle(
        [(card_inset, card_inset), (CANVAS - 1 - card_inset, CANVAS - 1 - card_inset)],
        radius=140,
        fill=255,
    )
    bg.paste(Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255)), (0, 0), card)

    # QR centered
    qr_size = CANVAS - 2 * PADDING
    qr_img = qr_img.resize((qr_size, qr_size), Image.LANCZOS)
    bg.paste(qr_img, (PADDING, PADDING), qr_img)

    # Outer rounded mask (squircle approximation)
    mask = Image.new("L", (CANVAS, CANVAS), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        [(0, 0), (CANVAS - 1, CANVAS - 1)], radius=RADIUS, fill=255
    )
    icon = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    icon.paste(bg, (0, 0), mask)
    return icon


def write_icns(icon: Image.Image) -> None:
    """macOS only — uses iconutil. Builds an .iconset and converts."""
    iconset = HERE / "icon.iconset"
    if iconset.exists():
        shutil.rmtree(iconset)
    iconset.mkdir()

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
        icon.resize((size, size), Image.LANCZOS).save(iconset / name)

    subprocess.run(
        ["iconutil", "-c", "icns", str(iconset), "-o", str(HERE / "icon.icns")],
        check=True,
    )
    shutil.rmtree(iconset)


def write_ico(icon: Image.Image) -> None:
    """Windows multi-size .ico (Pillow handles resizing)."""
    sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    icon.save(HERE / "icon.ico", format="ICO", sizes=sizes)


def main() -> None:
    icon = build_master()
    icon.save(HERE / "icon_1024.png")
    icon.resize((512, 512), Image.LANCZOS).save(HERE / "icon.png")
    write_ico(icon)
    print(f"icon_1024.png  {(HERE / 'icon_1024.png').stat().st_size:>9} bytes")
    print(f"icon.png       {(HERE / 'icon.png').stat().st_size:>9} bytes")
    print(f"icon.ico       {(HERE / 'icon.ico').stat().st_size:>9} bytes")

    if platform.system() == "Darwin":
        write_icns(icon)
        print(f"icon.icns      {(HERE / 'icon.icns').stat().st_size:>9} bytes")
    else:
        print("(skipping icon.icns — not on macOS)")


if __name__ == "__main__":
    main()
