@echo off
title Dutch Network Information Tool
color 0A


echo ============================================
=============
echo    Dutch Network Information Gathering Tool
echo ============================================
=============
echo.



REM Get the drive letter of the USB
set USB_DRIVE=%~d0
cd /d "%USB_DRIVE%"



echo Current Directory: %CD%
echo.



REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo Please install Python 3.7+ and try again.
    echo.
    echo Opening Python download page ...
    start https://python.org/downloads/
    pause
    exit /b 1
)



echo Python found. Checking dependencies ...
echo.



REM Install required packages
echo Installing required Python packages ...
python -m pip install --user -r requirements.txt



if %errorlevel% neq 0 (
    echo Failed to install some packages. Trying alternative installation ...
    python -m pip install --user psutil netifaces requests
)



echo.
echo Starting Dutch Network Information Tool ...
echo.



REM Run the main script
python dutch.py



echo.
echo Script execution completed.
echo Check the logs folder for output files.
echo.
pause