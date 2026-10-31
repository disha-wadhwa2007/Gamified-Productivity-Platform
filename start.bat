@echo off
title ChoreQuest Gamified Productivity Engine
echo ============================================================
echo   CHOREQUEST: THE GAMIFIED PRODUCTIVITY PLATFORM
echo   Transforming Boring Digital Chores into Fast-Paced Games
echo ============================================================
echo.
echo Starting ChoreQuest server on http://127.0.0.1:8765...
start "" "http://127.0.0.1:8765"
python server.py
pause
