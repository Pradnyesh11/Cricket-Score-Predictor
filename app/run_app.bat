@echo off
cd /d "%~dp0.."
python -m streamlit run "app\app.py" --server.headless true
if errorlevel 1 echo Streamlit exited with an error. Check the message above.
echo.
echo Streamlit has stopped. Press any key to close this window.
pause >nul
