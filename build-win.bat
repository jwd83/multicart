@echo off
echo Building JackGamesMulticart release
REM make a release build using pyinstaller and copying the assets folder
REM to the dist folder. clean up the junk after it is made.
REM
REM Usage: build-release.bat

REM make sure we are in the right directory
cd %~dp0

echo ------------------------------------------------------
echo Cleaning up old files
echo ------------------------------------------------------

REM remove the old build, dist and JackGamesMulticart folders if they are still around
rmdir /s /q dist
rmdir /s /q build
rmdir /s /q JackGamesMulticart

REM wait for a second to let the user see the message



echo ------------------------------------------------------
echo preparing settings.py for win build
echo ------------------------------------------------------
timeout /t 1 /nobreak
del settings.py
timeout /t 1 /nobreak
copy settings-win.py settings.py
timeout /t 1 /nobreak


echo ------------------------------------------------------
echo Cleaning up complete, building new release
echo ------------------------------------------------------
timeout /t 1 /nobreak

REM make the new dist folder
pyinstaller --onefile --noconsole --name=JackGamesMulticart main.py

echo ------------------------------------------------------
echo Build complete, packaging up assets
echo ------------------------------------------------------
timeout /t 1 /nobreak


REM copy the assets folder to the dist folder
xcopy /E assets dist\assets\

echo ------------------------------------------------------
echo Asset packaging complete, renaming the dist folder
echo ------------------------------------------------------
timeout /t 1 /nobreak


REM rename the dist folder to JackGamesMulticart
ren dist JackGamesMulticart


echo ------------------------------------------------------
echo Rename complete
echo ------------------------------------------------------
timeout /t 1 /nobreak


REM compress the JackGamesMulticart folder into a zip file using 7z
REM include the current timestamp in the zip file name

REM This script taken from the following URL:
REM http://www.winnetmag.com/windowsscripting/article/articleid/9177/windowsscripting_9177.html

REM Create the date and time elements.
for /f "tokens=1-7 delims=:/-, " %%i in ('echo exit^|cmd /q /k"prompt $d $t"') do (
   for /f "tokens=2-4 delims=/-,() skip=1" %%a in ('echo.^|date') do (
      set dow=%%i
      set %%a=%%j
      set %%b=%%k
      set %%c=%%l
      set hh=%%m
      set min=%%n
      set ss=%%o
   )
)

REM make hour 2 digits
if %hh%==0 set hh=00
if %hh%==1 set hh=01
if %hh%==2 set hh=02
if %hh%==3 set hh=03
if %hh%==4 set hh=04
if %hh%==5 set hh=05
if %hh%==6 set hh=06
if %hh%==7 set hh=07
if %hh%==8 set hh=08
if %hh%==9 set hh=09

REM Let's see the result.
echo ------------------------------------------------------
echo Packing zip at %dow% %yy%-%mm%-%dd% @ %hh%:%min%:%ss%
echo ------------------------------------------------------
timeout /t 1 /nobreak

7z a -tzip JackGamesMulticart-%yy%-%mm%-%dd%-at-%hh%-%min%-%ss%.zip JackGamesMulticart

echo ------------------------------------------------------
echo Cleanup
echo ------------------------------------------------------
timeout /t 1 /nobreak

REM remove the old build, dist and JackGamesMulticart folders if they are still around
rmdir /s /q dist
rmdir /s /q build
rmdir /s /q JackGamesMulticart
del *.spec
