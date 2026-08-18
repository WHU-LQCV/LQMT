@echo off
setlocal
cd /d "%~dp0\.."
python pack\build_windows.py
if errorlevel 1 exit /b 1
echo.
echo Full zip: dist\LQCV-LQMT-v1.0.0-windows-x64.zip
echo Gitee parts: dist\LQCV-LQMT-v1.0.0-windows-x64.zip.00* and dist\合并解压.bat
echo Run LQCV-LQMT.exe inside the unzipped LQCV-LQMT folder.
endlocal
