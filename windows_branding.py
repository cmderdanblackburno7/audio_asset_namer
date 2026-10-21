"""Optional Windows shell/non-client branding; standard library only."""
import ctypes
from ctypes import wintypes
from pathlib import Path
import sys
from tkinter import TclError

APP_ID = "BinauraWave.AudioAssetNamer"
DWMWA_USE_IMMERSIVE_DARK_MODE = 20
GA_ROOT = 2


def asset_path(name):
    # __file__ is bundle-relative in modern PyInstaller, including one-file
    # extraction. Never rely on cwd or the executable's external directory.
    return Path(__file__).resolve().parent / name


def set_app_id():
    """Give Windows its own taskbar group, rather than the Python launcher."""
    if sys.platform != "win32":
        return False
    try:
        function = ctypes.WinDLL("shell32").SetCurrentProcessExplicitAppUserModelID
        function.argtypes = [wintypes.LPCWSTR]
        function.restype = wintypes.LONG
        return function(APP_ID) == 0
    except (AttributeError, OSError, ctypes.ArgumentError):
        return False


def native_handle(root):
    """Tk's winfo_id is the child HWND; DWM needs its native root wrapper."""
    function = ctypes.WinDLL("user32").GetAncestor
    function.argtypes = [wintypes.HWND, wintypes.UINT]
    function.restype = wintypes.HWND
    return function(root.winfo_id(), GA_ROOT)


def apply_window_branding(root):
    """Run after Tk initialization; unsupported features are cosmetic no-ops."""
    result = {"icon": False, "dark_title_bar": False}
    if sys.platform != "win32":
        return result
    try:
        icon = str(asset_path("favicon.ico"))
        root.iconbitmap(default=icon)  # Defaults for future Tk toplevels.
        root.iconbitmap(icon)  # Explicitly set this window's small/large icons.
        result["icon"] = True
    except (OSError, TclError):
        pass
    try:
        root.update_idletasks()
        hwnd = native_handle(root)
        if hwnd:
            function = ctypes.WinDLL("dwmapi").DwmSetWindowAttribute
            function.argtypes = [wintypes.HWND, wintypes.DWORD, ctypes.c_void_p, wintypes.DWORD]
            function.restype = wintypes.LONG
            enabled = wintypes.BOOL(True)
            result["dark_title_bar"] = function(hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                                                ctypes.byref(enabled), ctypes.sizeof(enabled)) == 0
    except (AttributeError, OSError, TclError, ctypes.ArgumentError):
        pass
    return result
