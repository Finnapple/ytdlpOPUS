@echo off
:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python is not installed or not in PATH.
    pause
    exit /b 1
)

:: Create virtual environment
echo [*] Creating virtual environment "venv"...
python -m venv venv

:: Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

:: Upgrade pip
echo [*] Upgrading pip...
python -m pip install --upgrade pip

:: Install required packages for both scripts
echo [*] Installing required packages...
pip install yt-dlp ffmpeg-python mutagen Pillow

echo [*] Installation complete!
echo [*] To activate the virtual environment later, run:
echo call venv\Scripts\activate.bat
pause
