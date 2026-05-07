<p align="center">
  <img src="icon_1024.png" width="180" alt="vCard QR Generator icon"/>
</p>

<h1 align="center">vCard QR Generator</h1>

<p align="center">
  A tiny Tkinter app that turns contact details into a scannable vCard QR code.
  Cross-platform: <strong>macOS</strong>, <strong>Linux</strong>, <strong>Windows</strong>.
</p>

---

## What it does

Fill in name, phone, email, etc., click **Generate**, see the QR preview, click **Save as PNG…** to export. The QR encodes a vCard 3.0 string with high error correction (≈30%), so it scans reliably even on a slightly worn business card.

## Run from source (any OS)

```bash
git clone https://github.com/<your-username>/vcard-qr-generator.git
cd vcard-qr-generator

python3 -m venv venv
source venv/bin/activate          # on Windows: venv\Scripts\activate

pip install --upgrade pip
pip install "qrcode[pil]" Pillow

python vcard_qr_app.py
```

The Tkinter window opens. Iterate on the UI here — bundling is slow, running directly is instant.

## Build a standalone app

PyInstaller (Linux + Windows) and py2app (macOS) **cannot cross-compile** — you need to build on the OS you're targeting.

### macOS — py2app → `.app` bundle

```bash
source venv/bin/activate
pip install py2app
rm -rf build dist
python setup.py py2app
```

Output: `dist/vCard QR Generator.app` (~52 MB). Move it to `/Applications` and strip Gatekeeper quarantine on first launch:

```bash
mv "dist/vCard QR Generator.app" /Applications/
xattr -cr "/Applications/vCard QR Generator.app"
```

If macOS still refuses to open it: right-click → **Open** → confirm. macOS remembers the trust decision.

### Linux — PyInstaller → single executable

Prerequisites (Debian/Ubuntu — adjust for your distro):

```bash
sudo apt install python3-tk
```

Then from the activated venv:

```bash
pip install pyinstaller
python build.py
```

Output: `dist/vCard QR Generator` (single binary, ~50 MB). Drop it anywhere and run it. To wire it into your desktop menu, create a `.desktop` entry pointing at the binary and `icon.png`.

### Windows — PyInstaller → `.exe`

The Python.org installer for Windows ships Tk by default. From the activated venv:

```cmd
pip install pyinstaller
python build.py
```

Output: `dist\vCard QR Generator.exe`.

## Regenerating the icon

The repo ships with pre-built icon files for all three platforms:

| File | Used by |
|---|---|
| `icon.icns` | macOS / py2app |
| `icon.ico`  | Windows / PyInstaller |
| `icon.png`  | Linux / PyInstaller (and any 512×512 use) |
| `icon_1024.png` | this README, master preview |

To regenerate after tweaking colors in `make_icon.py`:

```bash
python make_icon.py
```

`icon.icns` is only emitted on macOS (it requires Apple's `iconutil`); the `.ico` and `.png` outputs work on every OS.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `ModuleNotFoundError: No module named '_tkinter'` (Homebrew Python on macOS) | `brew install python-tk@3.14` (match your Python's major.minor) |
| Same error on Linux | `sudo apt install python3-tk` (or your distro's equivalent) |
| Built Mac app launches then crashes silently | `./dist/vCard\ QR\ Generator.app/Contents/MacOS/vCard\ QR\ Generator` to see the error |
| `ModuleNotFoundError` after py2app build | Add the missing module to `OPTIONS['packages']` in `setup.py`, rebuild |
| Apple Silicon issues | Some Pillow/py2app combos need `arch -arm64 python setup.py py2app` |
| Icon doesn't refresh in Dock/Finder after rebuild | `killall Dock` (and/or `killall Finder`) — macOS caches icons aggressively |
| PyInstaller binary is huge / slow to start | `--onefile` extracts to /tmp on each launch. Switch to `--onedir` in `build.py` for faster startup at the cost of a folder instead of one file. |

## Customizing

- **Icon**: edit colors and corner radius in `make_icon.py`, rerun it, rebuild.
- **More fields**: extend the `FIELDS` list at the top of `vcard_qr_app.py`. The form rebuilds automatically.
- **Logo in QR center**: paste the QR onto a white square, blit a small logo in the middle. Error correction H tolerates ~30% damage so the logo can be sizable.
- **vCard 4.0**: change the `VERSION:3.0` line in `build_vcard()`. iOS handles it; some Android scanners are still picky.

## Project layout

```
.
├── vcard_qr_app.py   # Tkinter UI + vCard/QR logic (cross-platform)
├── make_icon.py      # generates icon.icns / icon.ico / icon.png from a styled QR
├── setup.py          # py2app config (macOS bundle)
├── build.py          # PyInstaller wrapper (Linux + Windows)
├── icon.icns         # macOS icon
├── icon.ico          # Windows icon
├── icon.png          # Linux icon (512×512)
├── icon_1024.png     # master preview, used in this README
├── LICENSE
└── README.md
```

## License

[MIT](LICENSE)
