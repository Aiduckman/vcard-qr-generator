#!/usr/bin/env python3
"""
vCard QR Generator — Mac app version.

Tkinter UI wrapping the original vcard_qr.py logic.
Bundle into a .app with: python setup.py py2app
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image, ImageTk

# Pillow 10+ moved resampling constants
try:
    RESAMPLE = Image.Resampling.LANCZOS
except AttributeError:
    RESAMPLE = Image.LANCZOS


# ─── vCard + QR logic (unchanged from the CLI version) ───────────────────────

def build_vcard(f: dict) -> str:
    """Assemble a vCard 3.0 string from a dict of fields."""
    return (
        "BEGIN:VCARD\n"
        "VERSION:3.0\n"
        f"N:{f['last_name']};{f['first_name']};;;\n"
        f"FN:{f['first_name']} {f['last_name']}\n"
        f"TITLE:{f['title']}\n"
        f"ORG:{f['org']}\n"
        f"TEL;TYPE=CELL:{f['phone']}\n"
        f"EMAIL:{f['email']}\n"
        f"URL:{f['url']}\n"
        f"ADR;TYPE=WORK:;;{f['city']};;;{f['country']}\n"
        f"NOTE:{f['note']}\n"
        "END:VCARD"
    )


def generate_qr_image(data: str) -> Image.Image:
    """Build a high-error-correction QR and return a PIL image."""
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,  # 30% redundancy
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").convert("RGB")


# ─── UI ──────────────────────────────────────────────────────────────────────

FIELDS = [
    ("first_name", "First name"),
    ("last_name",  "Last name"),
    ("title",      "Title"),
    ("org",        "Organization"),
    ("phone",      "Phone (e.g. +33612345678)"),
    ("email",      "Email"),
    ("url",        "Website"),
    ("city",       "City"),
    ("country",    "Country"),
    ("note",       "Note"),
]


class VCardQRApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("vCard QR Generator")
        self.geometry("780x560")
        self.minsize(680, 480)

        self._current_image: Image.Image | None = None
        self._tk_img: ImageTk.PhotoImage | None = None  # keep ref to avoid GC

        self._build_ui()

    def _build_ui(self):
        # Outer container
        main = ttk.Frame(self, padding=12)
        main.pack(fill="both", expand=True)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        # Left: form
        form = ttk.LabelFrame(main, text="Contact info", padding=10)
        form.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        form.columnconfigure(1, weight=1)

        self.entries: dict[str, ttk.Entry] = {}
        for i, (key, label) in enumerate(FIELDS):
            ttk.Label(form, text=label).grid(row=i, column=0, sticky="w", pady=4)
            entry = ttk.Entry(form, width=34)
            entry.grid(row=i, column=1, sticky="ew", pady=4, padx=(8, 0))
            self.entries[key] = entry

        # Right: preview + actions
        right = ttk.Frame(main)
        right.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        right.rowconfigure(0, weight=1)
        right.columnconfigure(0, weight=1)

        self.preview_label = ttk.Label(
            right,
            text="(QR preview will appear here)",
            anchor="center",
            relief="solid",
            borderwidth=1,
            padding=20,
        )
        self.preview_label.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        btns = ttk.Frame(right)
        btns.grid(row=1, column=0, sticky="ew")
        btns.columnconfigure(0, weight=1)
        btns.columnconfigure(1, weight=1)

        ttk.Button(btns, text="Generate", width=14, command=self.on_generate).grid(
            row=0, column=0, sticky="ew", padx=(0, 4)
        )
        ttk.Button(btns, text="Save as PNG…", width=16, command=self.on_save).grid(
            row=0, column=1, sticky="ew", padx=(4, 0)
        )

        # Status bar
        self.status = ttk.Label(self, text="Ready.", anchor="w", padding=(12, 4))
        self.status.pack(fill="x", side="bottom")

    # ─── actions ──────────────────────────────────────────────────────────

    def on_generate(self):
        fields = {k: e.get().strip() for k, e in self.entries.items()}
        # Strip spaces from phone — some scanners choke on them
        fields["phone"] = fields["phone"].replace(" ", "")

        if not fields["first_name"] and not fields["last_name"]:
            messagebox.showwarning(
                "Missing info",
                "At least a first or last name is required.",
            )
            return

        try:
            vcard = build_vcard(fields)
            img = generate_qr_image(vcard)
            self._current_image = img
            self._show_preview(img)
            self.status.config(
                text=f"Generated — {img.size[0]}×{img.size[1]} px. Click 'Save as PNG…'."
            )
        except Exception as exc:
            messagebox.showerror("Error", f"Could not generate QR:\n{exc}")
            self.status.config(text="Error.")

    def _show_preview(self, img: Image.Image):
        preview = img.copy()
        preview.thumbnail((320, 320), RESAMPLE)
        self._tk_img = ImageTk.PhotoImage(preview)
        self.preview_label.config(image=self._tk_img, text="")

    def on_save(self):
        if self._current_image is None:
            messagebox.showinfo("Nothing to save", "Generate a QR code first.")
            return

        first = self.entries["first_name"].get().strip()
        last = self.entries["last_name"].get().strip()
        default = f"{first}_{last}_qr.png".strip("_")
        if default == "_qr.png":
            default = "contact_qr.png"

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG image", "*.png")],
            initialfile=default,
        )
        if path:
            self._current_image.save(path)
            self.status.config(text=f"Saved: {path}")


def main():
    app = VCardQRApp()
    app.mainloop()


if __name__ == "__main__":
    main()
