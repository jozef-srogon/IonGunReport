# app/update_check.py
import re
import urllib.request
from typing import Optional
from app.version_utils import get_version

# Raw URL to the file on GitHub that contains the __version__ string.
# You can also host a simple "latest.txt" that contains only "1.2.3" which is simpler to parse.
LATEST_URL = "https://raw.githubusercontent.com/jozef-srogon/IonGunReport/main/app/version.py"

_VERSION_RE = re.compile(r'__version__\s*=\s*[\'"]([^\'"]+)[\'"]')

def fetch_latest_version(timeout: float = 5.0) -> Optional[str]:
    """
    Fetch the remote version string. Returns the parsed version (e.g. "1.0.0")
    or None if it couldn't be determined.
    """
    try:
        with urllib.request.urlopen(LATEST_URL, timeout=timeout) as r:
            text = r.read().decode("utf-8", errors="replace")
    except Exception:
        return None

    m = _VERSION_RE.search(text)
    if m:
        return m.group(1).strip()
    # If the remote file is a plain text with just the version, try that
    text_stripped = text.strip()
    if re.fullmatch(r'\d+\.\d+(?:\.\d+)?', text_stripped):
        return text_stripped
    return None

def check_latest(parent=None, show_if_same: bool = False):
    """
    Check for a newer version and notify the user.
    Safe to call from a background thread.

    - parent: optional Tkinter parent window (used to schedule messagebox on UI thread)
    - show_if_same: if True, still notify the user that they are on latest
    """
    latest = fetch_latest_version()
    if not latest:
        return  # couldn't fetch / parse

    current = get_version()

    # quick equality check (string equality). For semver-aware comparison,
    # implement proper version parsing (packaging.version or distutils.version).
    if latest == current:
        if show_if_same and parent:
            parent.after(0, lambda: __show_msg(parent, "Up to date",
                f"You have the latest version: {current}"))
        return

    # schedule showing the dialog on the main thread if parent provided
    if parent:
        parent.after(0, lambda: __show_msg(parent, "Update available",
            f"A newer version is available.\n\nCurrent: {current}\nLatest:  {latest}"))
    else:
        # No parent UI to schedule on; best-effort show (may be unsafe if called from a thread).
        try:
            from tkinter import messagebox
            messagebox.showinfo("Update available",
                f"A newer version is available.\n\nCurrent: {current}\nLatest:  {latest}")
        except Exception:
            # ignore if not safe to show
            pass

def __show_msg(parent, title: str, message: str):
    """Helper to show a messagebox with the parent (runs on main thread)."""
    from tkinter import messagebox
    try:
        messagebox.showinfo(title, message, parent=parent)
    except Exception:
        # fallback to a bare messagebox without parent if something odd happens
        try:
            messagebox.showinfo(title, message)
        except Exception:
            pass
