#!/bin/sh

#echo `pwd`

pyinstaller --clean -w -i logo.icns  main.py

cp config.ini dist/main.app/Contents/MacOS/
cp dist/updater.app/Contents/MacOS/updater dist/main.app/Contents/MacOS/

cp -r misc dist/main.app/Contents/MacOS/


#framework
#cp -r /Library/Frameworks/Python.framework/Versions/3.7/lib/python3.7/site-packages/PyQt5/Qt/lib/QtWebEngineCore.framework dist/main.app/Contents/Frameworks/

rm -rf dist/main
