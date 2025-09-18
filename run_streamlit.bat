@echo off
REM run_streamlit.bat - Windows batch script to run Streamlit app

echo Starting Financial Statement Automation System...

REM Check if required directories exist
echo Checking system directories...

set DIRS=temp output sample_data audit templates .streamlit

for %%d in (%DIRS%) do (
    if not exist "%%d" (
        echo Creating directory: %%d
        mkdir "%%d" 2>nul
    ) else (
        echo ✓ Directory exists: %%d
    )
)

REM Create Streamlit configuration if it doesn't exist
if not exist ".streamlit\config.toml" (
    echo Creating Streamlit configuration...
    (
    echo [server]
    echo maxUploadSize = 200
    echo maxMessageSize = 200
    echo enableCORS = false
    echo enableXsrfProtection = false
    echo port = 8501
    echo address = "localhost"
    echo enableStaticServing = true
    echo.
    echo [browser]
    echo gatherUsageStats = false
    echo.
    echo [client]
    echo showErrorDetails = true
    echo.
    echo [global]
    echo developmentMode = false
    echo.
    echo [logger]
    echo level = "info"
    ) > ".streamlit\config.toml"
    echo ✓ Configuration created
)

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking Python dependencies...
python -c "import streamlit, pandas, plotly, numpy" >nul 2>&1
if errorlevel 1 (
    echo Installing required packages...
    pip install streamlit pandas plotly numpy psutil
    if errorlevel 1 (
        echo ERROR: Failed to install packages
        pause
        exit /b 1
    )
)

REM Set environment variables
set STREAMLIT_SERVER_ENABLE_CORS=false
set STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
set STREAMLIT_SERVER_MAX_UPLOAD_SIZE=200
set STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

REM Check if port 8501 is available, otherwise use 8502
netstat -an | find "8501" >nul
if not errorlevel 1 (
    echo Port 8501 is busy, trying port 8502...
    set PORT=8502
) else (
    set PORT=8501
)

echo Starting Streamlit application...
echo Access the application at: http://localhost:%PORT%
echo Press Ctrl+C to stop the application

REM Run Streamlit with configuration
streamlit run streamlit_app.py ^
    --server.port %PORT% ^
    --server.address localhost ^
    --server.enableCORS false ^
    --server.enableXsrfProtection false ^
    --server.maxUploadSize 200 ^
    --browser.gatherUsageStats false ^
    --client.showErrorDetails true

pause