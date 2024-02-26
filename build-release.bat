@echo off
echo Building JackGamesMulticart release
REM make a release build using pyinstaller and copying the assets folder
REM to the dist folder. clean up the junk after it is made.
REM
REM Usage: build-release.bat

REM make sure we are in the right directory
cd %~dp0

REM remove the old build, dist and JackGamesMulticart folders if they are still around
rmdir /s /q dist
rmdir /s /q build
rmdir /s /q JackGamesMulticart

REM make the new dist folder
pyinstaller --onefile --noconsole --name=JackGamesMulticart main.py

REM post build cleanup
REM remove the build folder
rmdir /s /q build

REM remove the .spec file
del *.spec

REM copy the assets folder to the dist folder
xcopy /E assets dist\assets\

REM rename the dist folder to JackGamesMulticart
ren dist JackGamesMulticart

REM compress the JackGamesMulticart folder into a zip file using 7z
REM include the date and time in the zip file name
7z a -tzip JackGamesMulticart.zip JackGamesMulticart

REM remove the JackGamesMulticart folder
rmdir /s /q JackGamesMulticart