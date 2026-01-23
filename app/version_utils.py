# app/version_utils.py
import importlib
import importlib.util
import os
import sys

from app.functions import resource_path

def get_version() -> str:
    """
    Resolve the application version using multiple fallbacks:
      1) app.version.__version__ if available
      2) importlib.metadata (if packaged)
      3) top-level VERSION file (bundled via PyInstaller)
      4) fallback "0.0.0"
    """
    # 1) try module variable
    try:
        # import the module without importing whole package if possible
        spec = importlib.util.find_spec("app.version")
        if spec is not None:
            mod = importlib.import_module("app.version")
            v = getattr(mod, "__version__", None)
            if v:
                return str(v)
    except Exception:
        pass

    # 2) try package metadata (works if installed with pip / setuptools)
    try:
        # Python 3.8+: importlib.metadata
        try:
            from importlib.metadata import version, PackageNotFoundError
        except Exception:
            from importlib_metadata import version, PackageNotFoundError  # type: ignore
        # Replace 'your-package-name' with actual package name if used
        pkg_name = "IonGunDataConverter"  # when installed via pip/setuptools
        try:
            return version(pkg_name)
        except PackageNotFoundError:
            pass
    except Exception:
        pass

    # 3) try VERSION file (works for PyInstaller if you include it)
    try:
        p = resource_path("VERSION")
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as fh:
                txt = fh.read().strip()
                if txt:
                    return txt
    except Exception:
        pass

    # Finally fallback
    return "0.0.0"
