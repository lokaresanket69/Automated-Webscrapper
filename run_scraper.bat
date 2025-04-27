@echo off
set PATH=%PATH%;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\;C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python39\Scripts\
cd /d "%~dp0"
python automated_scraper.py
exit
