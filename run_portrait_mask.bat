@echo off
setlocal
chcp 65001 >nul
set PYTHONUTF8=1
pushd "%~dp0"
python --version >nul 2>&1
if errorlevel 1 goto try_py
python "%~dp0setup_and_run.py" %*
goto done
:try_py
py --version >nul 2>&1
if errorlevel 1 goto missing
py "%~dp0setup_and_run.py" %*
goto done
:missing
echo Python is required. Install Python from https://www.python.org/downloads/
echo Enable "Add python.exe to PATH", then run this file again.
:done
popd
echo.
pause
