@echo off
setlocal enabledelayedexpansion

echo ========================================
echo  World of Tanks Source Extractor Tool
echo ========================================
echo.

REM Check if Python 3 is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3 is not installed or not in PATH!
    echo Please install Python 3 from https://www.python.org/
    echo.
    pause
    exit /b 1
)

REM Show Python version
echo [INFO] Found Python:
python --version
echo.

REM Check if Python 2.7 exists for decompilation
if not exist "tools\python2\python.exe" (
    echo [ERROR] Python 2.7 not found at tools\python2\python.exe
    echo Please ensure Python 2.7 is installed in tools\python2\
    echo.
    pause
    exit /b 1
)

REM Ask for game path
echo Please enter the path to your World of Tanks game directory
echo Example: D:\Games\Tanki
echo.
set /p GAME_PATH="Game path: "

REM Remove quotes if present
set GAME_PATH=%GAME_PATH:"=%

REM Check if game path exists
if not exist "%GAME_PATH%" (
    echo [ERROR] Game path does not exist: %GAME_PATH%
    echo.
    pause
    exit /b 1
)

REM Check if it's a valid WoT directory
if not exist "%GAME_PATH%\res\packages" (
    echo [ERROR] Not a valid World of Tanks directory!
    echo Could not find res\packages folder in: %GAME_PATH%
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Step 1: Extracting .pyc files
echo ========================================
echo.
echo Extracting from: %GAME_PATH%
echo Output to: %cd%\res
echo.

REM Run the extractor
python tools\src_extractor\extract_pyc.py "%GAME_PATH%"
if errorlevel 1 (
    echo.
    echo [ERROR] Extraction failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Step 2: Decompiling .pyc to .py
echo ========================================
echo.
echo This may take a while...
echo.

REM Run the decompiler
python tools\pyc_decompiler\decompile_pyc.py res -r
if errorlevel 1 (
    echo.
    echo [ERROR] Decompilation failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo  COMPLETE!
echo ========================================
echo.
echo Source files have been extracted and decompiled to: %cd%\res
echo.
pause