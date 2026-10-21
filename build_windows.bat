@echo off
setlocal
cd /d "%~dp0"
py -3.13 -c "import sys" >nul 2>&1
if not errorlevel 1 (
    py -3.13 build_windows.py %*
    if errorlevel 1 (
        pause
        exit /b 1
    )
    exit /b 0
)
echo Building requires reviewed 64-bit Python 3.13.17 with Tkinter and venv support.
echo Or run build_windows.py using the full path to the reviewed 64-bit Python 3.13.17 executable.
pause
exit /b 1
