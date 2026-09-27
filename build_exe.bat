@echo off
setlocal
chcp 65001 >nul
set PYTHONUTF8=1
pushd "%~dp0"
python --version >nul 2>&1
if errorlevel 1 goto try_py
python "%~dp0setup_and_run.py" --build-exe
set "result=%errorlevel%"
goto done
:try_py
py --version >nul 2>&1
if errorlevel 1 goto missing
py "%~dp0setup_and_run.py" --build-exe
set "result=%errorlevel%"
goto done
:missing
echo Python is required. Install Python and enable "Add python.exe to PATH".
set "result=1"
:done
if "%result%"=="0" (echo Build complete: dist\Mask-Human.exe) else (echo Build failed. See the error above.)
popd
pause
exit /b %result%
