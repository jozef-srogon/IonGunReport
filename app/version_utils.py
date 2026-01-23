import importlib
import importlib.util
import os

from app.functions import resource_path

def get_version() -> str:
    try:
        spec = importlib.util.find_spec("app.version")
        if spec is not None:
            mod = importlib.import_module("app.version")
            v = getattr(mod, "__version__", None)
            if v:
                return str(v)
    except Exception:
        pass

    try:
        try:
            from importlib.metadata import version, PackageNotFoundError
        except Exception:
            from importlib_metadata import version, PackageNotFoundError  # type: ignore
        pkg_name = "IonGunDataConverter"
        try:
            return version(pkg_name)
        except PackageNotFoundError:
            pass
    except Exception:
        pass

    try:
        p = resource_path("VERSION")
        if os.path.isfile(p):
            with open(p, "r", encoding="utf-8") as fh:
                txt = fh.read().strip()
                if txt:
                    return txt
    except Exception:
        pass

    return "0.0.0"
