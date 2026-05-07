<p align="center">
  <img src="icon_1024.png" width="180" alt="vCard QR Generator icon"/>
</p>

<h1 align="center">vCard QR Generator</h1>

<p align="center">
  A tiny Tkinter app that turns contact details into a scannable vCard QR code, bundled as a native macOS <code>.app</code>.
</p>

---

## What it does

Fill in name, phone, email, etc., click **Generate**, see the QR preview, click **Save as PNG…** to export. The QR encodes a vCard 3.0 string with high error correction (≈30%), so it scans reliably even on a slightly worn business card.

## Quick start (run from source)

```bash
git clone https://github.com/<your-username>/vcard-qr-mac.git
cd vcard-qr-mac

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install "qrcode[pil]" Pillow py2app

python vcard_qr_app.py
```

The Tkinter window opens. Iterate on the UI here — bundling is slow, running directly is instant.

## Build the macOS .app

From inside the activated venv:

```bash
rm -rf build dist
python setup.py py2app
```

Produces a fully self-contained `dist/vCard QR Generator.app` (~52 MB) with the Python runtime, qrcode, and Pillow embedded. Drag it to `/Applications` (or anywhere else).

The app icon is already bundled — `setup.py` references `icon.icns`, which is committed at the repo root.

### Strip Gatekeeper quarantine on first launch

The app isn't code-signed (no Apple Developer account needed for personal use). Do this once after copying to /Applications:

```bash
xattr -cr "/Applications/vCard QR Generator.app"
```

If macOS still refuses to open it, right-click the app in Finder → **Open** → confirm. macOS remembers the trust decision.

## Regenerating the icon

The repo ships with a pre-built `icon.icns` and `icon_1024.png`. To regenerate them (e.g., after tweaking colors in `make_icon.py`):

```bash
source venv/bin/activate
python make_icon.py
```

Re-run the py2app build to embed the new icon.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: No module named '_tkinter'` (Homebrew Python on macOS) | Install the matching Tk: `brew install python-tk@3.14` (use the major.minor that matches your Python) |
| Built app launches then crashes silently | Run from Terminal: `./dist/vCard\ QR\ Generator.app/Contents/MacOS/vCard\ QR\ Generator` to see the error |
| `ModuleNotFoundError` after build | Add the missing module to `OPTIONS['packages']` in `setup.py`, rebuild |
| Apple Silicon issues | Some Pillow/py2app combos need `arch -arm64 python setup.py py2app` |
| Icon doesn't refresh in Dock/Finder after rebuild | `killall Dock` (and/or `killall Finder`) — macOS caches icons aggressively |

## Customizing

- **Icon**: edit colors and corner radius in `make_icon.py`, then rerun `python make_icon.py` and rebuild.
- **More fields**: extend the `FIELDS` list at the top of `vcard_qr_app.py`. The form rebuilds automatically.
- **Logo in QR center**: paste the QR image onto a white square, blit a small logo in the middle. Error correction H tolerates ~30% damage so the logo can be sizable.
- **vCard 4.0**: change the `VERSION:3.0` line in `build_vcard()`. iOS handles it; some Android scanners are still picky.

## Project layout

```
.
├── vcard_qr_app.py   # Tkinter UI + vCard/QR logic
├── setup.py          # py2app build config
├── make_icon.py      # generates icon.icns from a styled QR code
├── icon.icns         # bundled by py2app
├── icon_1024.png     # 1024×1024 preview, used in this README
├── LICENSE
└── README.md
```

## License

[MIT](LICENSE)
