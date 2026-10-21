"""Build-only collection of retained licence texts. Never imported by the app."""
import argparse
from importlib.metadata import distribution
from pathlib import Path
import shutil
import sys
import tkinter

PACKAGES = ("pyinstaller", "pyinstaller-hooks-contrib", "altgraph", "packaging",
            "pefile", "pywin32-ctypes", "setuptools")


def collect_notices(output):
    root = Path(__file__).resolve().parent
    output = Path(output).resolve()
    expected = (root / "build" / "release-notices").resolve()
    if output != expected or root not in output.parents:
        raise ValueError("Notice output must be this checkout's build/release-notices directory")
    if not tkinter.Tcl().eval("info patchlevel").startswith("8.6.") or tkinter.TkVersion != 8.6:
        raise ValueError("Review and update Tcl/Tk notice versions before building with this runtime")
    python_license = Path(sys.base_prefix) / "LICENSE.txt"
    if not python_license.is_file():
        raise ValueError("The build interpreter's complete LICENSE.txt is required")
    if output.exists():
        shutil.rmtree(output)  # Resolved target checked above; generated notices only.
    output.mkdir(parents=True)
    for name in ("LICENSE", "BRANDING.md", "THIRD_PARTY_NOTICES.md"):
        shutil.copyfile(root / name, output / name)
    shutil.copytree(root / "licenses", output / "licenses")
    shutil.copyfile(python_license, output / "licenses" / "PYTHON.txt")
    for package in PACKAGES:
        info = distribution(package)
        notices = [p for p in info.files or [] if
                   any(part.endswith(".dist-info") for part in p.parts) and
                   p.name.upper().startswith(("LICENSE", "COPYING", "NOTICE")) and
                   p.suffix.lower() not in (".py", ".pyc")]
        if not notices:
            raise ValueError(f"Missing installed licence notices for {package}")
        for relative in notices:
            target = output / "licenses" / "build-tools" / package / str(relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(info.locate_file(relative), target)
    print("Collected project, Python, Tcl/Tk and installed build-package notices.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    collect_notices(parser.parse_args().output)
