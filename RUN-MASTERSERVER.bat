@echo off
title Revelade Revolution MasterServer
cd /d %~dp0
echo ============================================================
echo  Revelade Revolution MasterServer
echo  Leave this window open while testing. Close it to stop.
echo ============================================================
echo.
echo Same PC test:   in the game console type  mastername 127.0.0.1
echo Other PCs:      use this PC's network IP instead of 127.0.0.1
echo.
echo If Windows Firewall asks about python.exe, click Allow.
echo.
python\python.exe run.py
echo.
echo Server stopped.
pause
