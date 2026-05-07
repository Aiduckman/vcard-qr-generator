"""
setup.py for py2app — bundles vCard QR Generator as a macOS .app

Quick reference:

    # one-time install (in a venv, see README)
    pip install py2app

    # alias build (fast, dev only — links to source files)
    python setup.py py2app -A

    # full standalone build (slower, redistributable)
    python setup.py py2app

Output appears in ./dist/
"""

from setuptools import setup

APP = ['vcard_qr_app.py']
APP_NAME = "vCard QR Generator"

OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'icon.icns',
    'plist': {
        'CFBundleName': APP_NAME,
        'CFBundleDisplayName': APP_NAME,
        'CFBundleIdentifier': "local.geev.vcardqr",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHighResolutionCapable': True,  # crisp on Retina
    },
    # py2app sometimes misses these — be explicit
    'packages': ['PIL', 'qrcode'],
    'includes': ['tkinter'],
}

setup(
    app=APP,
    name=APP_NAME,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
