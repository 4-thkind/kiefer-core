@echo off
echo ========================================================
echo   Fibonacci Search One-Dimensional Optimization System
echo   NOAA Mauna Loa CO2 Keeling Curve Growth Rate Fitting
echo ========================================================
echo.

echo [1/3] Compiling C++17 Core Codebase...
g++ -O2 -std=c++14 -o fibonacci_search.exe fibonacci_search.cpp
if %ERRORLEVEL% EQU 0 (
    echo     [OK] Compiled fibonacci_search.exe successfully!
) else (
    echo     [WARN] C++ compilation failed or g++ not found. You can still use the Python engine!
)

echo.
echo [2/3] Running Native C++ Optimization Binary...
if exist fibonacci_search.exe (
    fibonacci_search.exe
) else (
    python fibonacci_search.py
)

echo.
echo [3/3] Starting Interactive Web Frontend & API Server...
echo     Opening browser at: http://127.0.0.1:8000
start http://127.0.0.1:8000
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
pause
