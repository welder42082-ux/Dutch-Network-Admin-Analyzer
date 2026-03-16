@echo off
title Python Auto-Installer
echo Downloading and Installing Python ...



REM Download Python Installer
powershell -Command "& {Invoke-Webrequest -Uri 'https://www.python.org/ftp/python/3.11.0/python-3.11.0-amd.exe' -OutFile 'python_installer.exe']"



REM Install Python silently
echo Installing Python ...
python_installer.exe /quiet
InstallAllUsers=1 PrependPath=1
Include_test=0



echo Python installation completed.
del python_installer.exe



echo Refreshing environment variables ...
call refreshenv



pause