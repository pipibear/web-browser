@echo off
rem pyinstaller -F -w -c -i logo.ico  main.py

rd /S /q dist\main

pyinstaller --clean -w -i logo.ico  main.py
xcopy config.ini dist\main\
xcopy dist\updater\updater.exe dist\main\
robocopy dll\ dist/main/dll/ /s *.*
robocopy misc\ dist/main/misc/ /s *.*

robocopy fix\win32 dist/main/ /s *.*


rem rd /S /q dist\main\PyQt5\Qt\qml

pause