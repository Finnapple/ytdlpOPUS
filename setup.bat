@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

:: Get the current folder path of the script
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo.
echo ==================================================
echo    YouTube Music Downloader - Portable Setup
echo ==================================================
echo.

echo [*] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in your system PATH.
    echo Please install Python and try again.
    pause
    exit /b 1
)

:: Create virtual environment
echo [*] Creating Python virtual environment in: %SCRIPT_DIR%venv
if exist "%SCRIPT_DIR%venv" (
    echo [*] Virtual environment already exists. Updating...
) else (
    python -m venv venv --clear
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo [*] Activating virtual environment...
call "%SCRIPT_DIR%venv\Scripts\activate.bat"

echo [*] Upgrading pip...
python -m pip install --upgrade pip

echo [*] Installing yt-dlp in virtual environment...
python -m pip install yt-dlp

:: Check if ffmpeg exists, if not, show instructions
echo.
echo [*] Checking for ffmpeg...
if not exist "%SCRIPT_DIR%ffmpeg.exe" (
    echo [*] ffmpeg.exe not found in script folder.
    echo [*] For best results, please download ffmpeg:
    echo     https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip
    echo     Extract ffmpeg.exe and place it in this folder.
) else (
    echo [✓] ffmpeg.exe found in script folder
)

:: Create run.bat for easy execution
echo [*] Creating run.bat...
(
echo @echo off
echo setlocal enabledelayedexpansion
echo chcp 65001 ^>nul
echo.
echo :: Get the current folder path
echo set "SCRIPT_DIR=%%~dp0"
echo cd /d "%%SCRIPT_DIR%%"
echo.
echo :: Check if virtual environment exists
echo if not exist "%%SCRIPT_DIR%%venv\Scripts\activate.bat" (
echo     echo [ERROR] Virtual environment not found!
echo     echo Please run setup.bat first to install required dependencies.
echo     pause
echo     exit /b 1
echo )
echo.
echo :: Activate virtual environment
echo call "%%SCRIPT_DIR%%venv\Scripts\activate.bat"
echo.
echo :: Run the Python script
echo python youtube_music_downloader.py %%*
echo.
echo :: Deactivate virtual environment
echo deactivate
echo.
echo pause
) > run.bat

:: Create a simple launcher for drag-and-drop
echo [*] Creating drag-drop-launcher.bat...
(
echo @echo off
echo setlocal enabledelayedexpansion
echo chcp 65001 ^>nul
echo.
echo :: Get the current folder path
echo set "SCRIPT_DIR=%%~dp0"
echo cd /d "%%SCRIPT_DIR%%"
echo.
echo :: Check if URL was provided
echo if "%%1"=="" (
echo     echo [ERROR] No URL provided.
echo     echo Drag and drop a YouTube Music URL onto this file.
echo     pause
echo     exit /b 1
echo )
echo.
echo :: Check if virtual environment exists
echo if not exist "%%SCRIPT_DIR%%venv\Scripts\activate.bat" (
echo     echo [ERROR] Virtual environment not found!
echo     echo Please run setup.bat first to install required dependencies.
echo     pause
echo     exit /b 1
echo )
echo.
echo :: Activate virtual environment
echo call "%%SCRIPT_DIR%%venv\Scripts\activate.bat"
echo.
echo :: Run the Python script with the URL
echo python youtube_music_downloader.py "%%1"
echo.
echo :: Deactivate virtual environment
echo deactivate
echo.
echo pause
) > drag-drop-launcher.bat

echo.
echo ==================================================
echo [SUCCESS] Setup completed!
echo ==================================================
echo.
echo Status: Portable Environment Ready
echo Location: %SCRIPT_DIR%
echo Virtual Environment: %SCRIPT_DIR%venv
echo.
echo How to use:
echo   [1] Double-click run.bat for interactive mode
echo   [2] Drag and drop a URL onto drag-drop-launcher.bat
echo   [3] Command line: run.bat "URL"
echo   [4] Multiple URLs: run.bat --file urls.txt
echo.
echo Files in this folder:
echo   - youtube_music_downloader.py (main script)
echo   - venv\ (virtual environment)
echo   - run.bat (interactive launcher)
echo   - drag-drop-launcher.bat (drag & drop launcher)
echo   - ffmpeg.exe (optional, place here if needed)
echo.
echo The entire folder is portable - copy to USB or another PC!
echo.
pause
