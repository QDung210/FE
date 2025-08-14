@echo off
echo ========================================
echo       Quiz Application Launcher
echo ========================================
echo.

echo Changing to project directory...
cd /d "C:\Users\dung\OneDrive\Desktop\FE"

echo Activating conda environment 'FE'...
call conda activate FE

echo.
echo Starting Streamlit Quiz Application...
echo.
echo The app will open in your browser at: http://localhost:8502
echo.

streamlit run quiz_new.py

echo.
echo Application has stopped. Press any key to close this window.
pause
