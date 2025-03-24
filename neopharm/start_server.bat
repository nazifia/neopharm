@echo off
cd /d %~dp0
call python manage.py runserver 127.0.0.1:80
pause