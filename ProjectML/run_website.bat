@echo off
title CardioPredict - Heart Disease Prediction System
echo ==============================================================
echo CardioPredict: Heart Disease Prediction Decision Support System
echo KL University - Department of Computer Science and Engineering
echo ==============================================================
echo.
echo Starting Flask web server on http://127.0.0.1:5000 ...
echo Press Ctrl+C in this terminal window to stop the server.
echo.

cd /d "%~dp0"
call .venv\Scripts\python.exe app.py
pause
