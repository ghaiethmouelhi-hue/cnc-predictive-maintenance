@echo off
setlocal
cd /d "%~dp0"

set "APP_URL=http://127.0.0.1:8502"
set "PYTHON=%~dp0.venv\Scripts\python.exe"
if not exist "%PYTHON%" set "PYTHON=%~dp0venv\Scripts\python.exe"

curl.exe --fail --silent --max-time 2 "%APP_URL%/_stcore/health" >nul 2>nul
if not errorlevel 1 (
    start "" "%APP_URL%"
    exit /b 0
)

if not exist "%PYTHON%" (
    echo Python environment not found.
    echo Create .venv or venv and install requirements.txt first.
    pause
    exit /b 1
)

if not exist "%~dp0models\xgboost_model.pkl" (
    echo Trained model not found: models\xgboost_model.pkl
    echo Run the project training pipeline first.
    pause
    exit /b 1
)

if not exist "%~dp0data\processed\scaler.pkl" (
    echo Feature scaler not found: data\processed\scaler.pkl
    echo Run the feature engineering pipeline first.
    pause
    exit /b 1
)

"%PYTHON%" -m streamlit run "%~dp0app\streamlit_app.py" --server.headless false --server.address 127.0.0.1 --server.port 8502
if errorlevel 1 (
    echo.
    echo The app stopped with an error. Read the message above.
    pause
)
