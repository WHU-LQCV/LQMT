@echo off
setlocal
cd /d "%~dp0\.."
python pack\build_windows.py
if errorlevel 1 exit /b 1
echo.
echo Output: dist\LQCV-LQMT-v1.0.0-windows-x64.zip
echo Run LQCV-LQMT.exe inside the unzipped LQCV-LQMT folder.
endlocal
