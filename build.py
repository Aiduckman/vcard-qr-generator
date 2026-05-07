"""Cross-platform PyInstaller build script for vCard QR Generator.

Run on Linux or Windows to produce a standalone executable.
On macOS, prefer `python setup.py py2app` (see README) — py2app produces a
proper .app bundle with native integration. This script also works on macOS
but the output is a single binary, not a bundle.

Usage:
    python build.py
"""
from __future__ import annotations

import platform
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
APP_NAME = "vCard QR Generator"
ENTRY = "vcard_qr_app.py"


def main() -> int:
    system = platform.system()
    icon = {
        "Darwin": HERE / "icon.icns",
        "Linux":  HERE / "icon.png",
        "Windows": HERE / "icon.ico",
    }.get(system, HERE / "icon.png")

    if not icon.exists():
        print(f"Missing icon for {system}: {icon}", file=sys.stderr)
        print("Run `python make_icon.py` first.", file=sys.stderr)
        return 1

    # Clean previous artifacts
    for d in ("build", "dist"):
        p = HERE / d
        if p.exists():
            shutil.rmtree(p)
    spec = HERE / f"{APP_NAME}.spec"
    if spec.exists():
        spec.unlink()

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", APP_NAME,
        "--icon", str(icon),
        str(HERE / ENTRY),
    ]
    print("$", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode == 0:
        out = HERE / "dist"
        print(f"\nDone. Output in: {out}")
        for f in sorted(out.iterdir()):
            print(f"  {f.name}")
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
