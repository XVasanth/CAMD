# ===== run.bat (Windows) =====
@echo off
echo.
echo ===============================================
echo   CAD Educational Assessment System
echo ===============================================
echo.

REM Check if venv exists
if not exist "venv\" (
    echo Virtual environment not found. Running setup...
    python setup.py
    if errorlevel 1 (
        echo Setup failed. Please check error messages.
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Streamlit not found. Installing dependencies...
    pip install -r requirements.txt
)

REM Run the application
echo.
echo Starting CAD Assessment System...
echo Opening in browser: http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.
streamlit run app.py

REM Deactivate on exit
deactivate
pause

# ===== run.sh (Linux/macOS) =====
#!/bin/bash

echo ""
echo "==============================================="
echo "   CAD Educational Assessment System"
echo "==============================================="
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    python3 setup.py
    if [ $? -ne 0 ]; then
        echo "Setup failed. Please check error messages."
        exit 1
    fi
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if streamlit is installed
python -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Streamlit not found. Installing dependencies..."
    pip install -r requirements.txt
fi

# Run the application
echo ""
echo "Starting CAD Assessment System..."
echo "Opening in browser: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
streamlit run app.py

# Deactivate on exit
deactivate
