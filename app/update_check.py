import urllib.request
from tkinter import messagebox
from app.version_utils import get_version

LATEST_URL = "https://raw.githubusercontent.com/jozef-srogon/IonGunReport/main/app/version.py"

def check_latest(parent=None):
    """
    Check if a newer version exists.
    Safe to call from a background thread.
    """
    try:
        with urllib.request.urlopen(LATEST_URL, timeout=5) as r:
            latest = r.read().decode().strip()

        current = get_version()

        if latest and latest != current:
            if parent:
                messagebox.showinfo(
                    "Update available",
                    f"A newer version is available.\n\n"
                    f"Current version: {current}\n"
                    f"Latest version: {latest}",
                    parent=parent
                )
    except Exception:
        # silently ignore network errors
        pass
