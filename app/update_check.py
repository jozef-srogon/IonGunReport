import re
import urllib.request
from typing import Optional
from tkinter import messagebox
from app.version_utils import get_version

LATEST_URL = "https://raw.githubusercontent.com/jozef-srogon/IonGunReport/main/app/version.py"

_VERSION_RE = re.compile(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]')

def fetch_latest_version(timeout: float = 5.0) -> Optional[str]:
    try:
        with urllib.request.urlopen(LATEST_URL, timeout=timeout) as r:
            text = r.read().decode("utf-8", errors="replace")
    except Exception:
        return None

    m = _VERSION_RE.search(text)
    if m:
        return m.group(1).strip()
    text_stripped = text.strip()
    if re.fullmatch(r'\d+\.\d+(?:\.\d+)?', text_stripped):
        return text_stripped
    return None

def check_latest(parent=None, show_if_same: bool = False):
    latest = fetch_latest_version()
    if not latest:
        return

    current = get_version()

    if latest == current:
        if show_if_same and parent:
            parent.after(0, lambda: __show_msg(parent, "Up to date",
                f"You have the latest version: {current}"))
        return

    if parent:
        parent.after(0, lambda: __show_msg(parent, "Update available",
            f"A newer version is available.\n\nCurrent: {current}\nLatest:  {latest}"))
    else:
        try:
            messagebox.showinfo("Update available",
                f"A newer version is available.\n\nCurrent: {current}\nLatest:  {latest}")
        except Exception:
            pass

def __show_msg(parent, title: str, message: str):
    try:
        messagebox.showinfo(title, message, parent=parent)
    except Exception:
        try:
            messagebox.showinfo(title, message)
        except Exception:
            pass
