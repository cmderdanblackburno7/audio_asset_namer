"""Build the standalone Windows executable and release ZIP in this tool's dist/."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import struct
import subprocess
import sys
import venv
import zipfile

from core import VERSION

TOOL = Path(__file__).resolve().parent
BUILD = TOOL / "build"
DIST = TOOL / "dist"
ENVIRONMENT = TOOL / ".build-venv"
EXE_NAME = "BinauraWave-Audio-Asset-Namer.exe"


def run(*arguments, env=None):
    subprocess.run([str(arg) for arg in arguments], cwd=TOOL, env=env, check=True)


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()



def source_state():
    """Record local provenance without fetching or changing Git state."""
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=TOOL, text=True, stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=TOOL, text=True).strip())
        return {"commit": commit, "dirty": dirty}
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}


def verify_checksums(checksum_file):
    for line in checksum_file.read_text(encoding="ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        expected, name = line.split("  ", 1)
        if Path(name).name != name or sha256(checksum_file.parent / name) != expected:
            raise ValueError(f"Release checksum mismatch: {name}")


def write_checksums(paths, checksum_file):
    lines = ["# SHA-256 checksums for the final release files.",
             "# In PowerShell: Get-FileHash .\\<filename> -Algorithm SHA256",
             "# Compare all 64 hexadecimal characters with the matching line below."]
    lines.extend(f"{sha256(path)}  {path.name}" for path in paths)
    checksum_file.write_text("\n".join(lines) + "\n", encoding="ascii")
    verify_checksums(checksum_file)


def verify_executable(executable, python):
    # IMAGE_SUBSYSTEM_WINDOWS_GUI = 2: no console window for normal startup.
    with executable.open("rb") as stream:
        if stream.read(2) != b"MZ":
            raise ValueError("Build output is not a Windows executable")
        stream.seek(0x3C)
        pe_offset = struct.unpack("<I", stream.read(4))[0]
        stream.seek(pe_offset)
        if stream.read(4) != b"PE\0\0":
            raise ValueError("Invalid PE signature")
        machine = struct.unpack("<H", stream.read(2))[0]
        stream.seek(pe_offset + 24 + 68)
        if machine != 0x8664 or struct.unpack("<H", stream.read(2))[0] != 2:
            raise ValueError("Expected an x64 Windows GUI executable")
    # Check the actual one-file archive, not just the spec's declared data.
    code = ("import sys; from PyInstaller.archive.readers import CArchiveReader; "
            "r=CArchiveReader(sys.argv[1]); names={n.replace(chr(92),'/') for n in r.toc}; "
            "assert {'favicon.ico','assets/logo.png'} <= names, 'Missing branding assets'; "
            "assert any(n.endswith('python312.dll') or n.startswith('python3') and n.endswith('.dll') for n in names), 'Missing Python'; "
            "assert any('_tkinter' in n for n in names), 'Missing Tkinter'; "
            "assert not any(n.startswith(('tests/','screenshots/','.git/','wordpress/','prepared-audio/')) for n in names), 'Development files bundled'; "
            "print('Verified GUI subsystem and bundled Python/Tk/branding; no project test/data folders.')")
    run(python, "-c", code, executable)


def build(skip_install=False, gui_smoke=False):
    if sys.platform != "win32" or struct.calcsize("P") != 8:
        raise ValueError("Build on 64-bit Windows with a 64-bit Python interpreter (3.12 recommended).")
    if sys.version_info < (3, 11):
        raise ValueError("The build script needs Python 3.11+ (3.12 recommended); the source app supports 3.10+.")
    provenance = source_state()
    BUILD.mkdir(exist_ok=True)
    DIST.mkdir(exist_ok=True)
    python = ENVIRONMENT / "Scripts" / "python.exe"
    if not python.exists():
        venv.EnvBuilder(with_pip=True).create(ENVIRONMENT)
    if not skip_install:
        run(python, "-m", "pip", "install", "--disable-pip-version-check", "--no-cache-dir",
            "-r", TOOL / "requirements-build.txt")
    # Assert build tooling even when installation is explicitly skipped.
    run(python, "-c", "import PyInstaller, tkinter; assert PyInstaller.__version__ == '6.22.3'; tkinter.Tcl()")
    test = TOOL / "tests" / "audio_asset_namer_regression.py"
    if not test.is_file():
        raise ValueError(f"Regression suite is required before building: {test}")
    run(python, test, *(["--gui-smoke"] if gui_smoke else []))
    run(python, TOOL / "tests" / "release_packaging_regression.py")
    environment = os.environ.copy()
    environment["PYINSTALLER_CONFIG_DIR"] = str(BUILD / "pyinstaller-cache")
    run(python, "-m", "PyInstaller", "--clean", "--noconfirm", "--distpath", DIST,
        "--workpath", BUILD, TOOL / "audio_asset_namer.spec", env=environment)
    executable = DIST / EXE_NAME
    verify_executable(executable, python)
    readme = DIST / "README.txt"
    readme.write_text((TOOL / "RELEASE_README.txt").read_text(encoding="utf-8").replace("@VERSION@", VERSION), encoding="utf-8")
    notice_dir = BUILD / "release-notices"
    run(python, TOOL / "release_notices.py", "--output", notice_dir)
    notices = sorted(path for path in notice_dir.rglob("*") if path.is_file())
    archive = DIST / f"BinauraWave-Audio-Asset-Namer-{VERSION}-Windows-x64.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as release:
        release.write(executable, EXE_NAME)
        release.write(readme, "README.txt")
        for path in notices:
            release.write(path, path.relative_to(notice_dir).as_posix())
    with zipfile.ZipFile(archive) as release:
        expected = {EXE_NAME, "README.txt"} | {p.relative_to(notice_dir).as_posix() for p in notices}
        if release.testzip() or set(release.namelist()) != expected:
            raise ValueError("Release ZIP validation failed")
        if hashlib.sha256(release.read(EXE_NAME)).hexdigest() != sha256(executable):
            raise ValueError("Release ZIP executable checksum mismatch")
    write_checksums((executable, archive), DIST / "SHA256SUMS.txt")
    packages = subprocess.check_output([str(python), "-m", "pip", "freeze"], text=True).splitlines()
    report = {"version": VERSION, "python": sys.version, "build_packages": packages, "source": provenance,
              "artifacts": [{"filename": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
                            for path in (executable, archive)],
              "automated_checks": "source regressions, PE x64 GUI subsystem, archive contents, release ZIP integrity",
              "release_note": "Packaged GUI acceptance must be recorded separately; no publication; source MIT terms, reserved branding and third-party notices included."}
    (DIST / "build-info.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    print(f"Release ZIP: {archive}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-install", action="store_true", help="Reuse already installed pinned build dependencies")
    parser.add_argument("--gui-smoke", action="store_true", help="Also run desktop GUI source checks before building")
    args = parser.parse_args()
    try:
        build(args.skip_install, args.gui_smoke)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        sys.exit(1)
