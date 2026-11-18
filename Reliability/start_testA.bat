@echo off
setlocal EnableDelayedExpansion
set FILE=ttpath.txt

if exist "%FILE%" (
    for /f "delims=" %%x in (%FILE%) do set TTPATH=%%x
    echo TTPATH variable is: !TTPATH!
) else (
    echo File not found
)
if  "%~1"=="" (
	set /p DUT_IP=Please enter the IP address: 
) else (
   set "DUT_IP=%~1"
    REM Add your fallback code here
)
echo main PATH: !TTPATH!\TTPMACRO.exe
echo IP=%DUT_IP% 
"!TTPATH!\TTPMACRO.exe" /I /V .\ttl\GROUPAb.ttl "%DUT_IP%"
"!TTPATH!\TTPMACRO.exe" /I /V .\ttl\GROUPAc.ttl "%DUT_IP%"
rem d Memtest
"!TTPATH!\TTPMACRO.exe" /I /V .\ttl\GROUPAd.ttl "%DUT_IP%"

Rem wait for 5 secs
@ping %DUT_IP% -n 5 -w 1000 > nul

REM item D JPEG encoding&SD card R/W test
"!TTPATH!\TTPMACRO.exe" /I /V .\ttl\GROUPAe.ttl "%DUT_IP%"
rem f show memory info repeatly
REM "!TTPATH!\TTPMACRO.exe" /I /V .\ttl\GROUPAf.ttl "%DUT_IP%"
"!TTPATH!\TTPMACRO.exe" /I /V .\ttl\GROUPAg.ttl "%DUT_IP%"
"!TTPATH!\TTPMACRO.exe" /I /V .\ttl\GROUPAh.ttl "%DUT_IP%"
REM ping 192.168.100.20 -t 