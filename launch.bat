@echo off
setlocal
cd /d "%~dp0"
py -3 -c "import sys, tkinter; assert sys.version_info >= (3, 10)" >nul 2>&1
if not errorlevel 1 (
    py -3 app.py
    if errorlevel 1 pause
    exit /b
)
python -c "import sys, tkinter; assert sys.version_info >= (3, 10)" >nul 2>&1
if not errorlevel 1 (
    python app.py
    if errorlevel 1 pause
    exit /b
)
echo Python 3.10 or newer with Tkinter is required.
echo Install Python with Tcl/Tk support and the Python launcher or PATH option.
echo Alternatively run app.py using the full path to your Python executable.
pause
