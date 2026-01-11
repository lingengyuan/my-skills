@echo off
REM Activate virtual environment for Windows

call .venv\Scripts\activate.bat

echo Virtual environment activated.
echo Python: $(python --version)
echo.
echo To deactivate, run: deactivate
