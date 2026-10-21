# One-file/windowed Windows release recipe; run through build_windows.py.
from pathlib import Path

tool_dir = Path(SPECPATH)
a = Analysis(
    [str(tool_dir / "app.py")], pathex=[str(tool_dir)], binaries=[],
    datas=[(str(tool_dir / "favicon.ico"), "."),
           (str(tool_dir / "assets" / "logo.png"), "assets")],
    hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[],
    # The utility never decodes archives; omit unused liblzma/XZ decoder code.
    excludes=["pip", "setuptools", "wheel", "pytest", "unittest", "lzma", "_lzma"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name="BinauraWave-Audio-Asset-Namer", icon=str(tool_dir / "favicon.ico"),
    console=False, debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
)
