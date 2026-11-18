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

rem encoding test
"!TTPATH!\TTPMACRO.exe" /I /V .\ttl\GROUPBb.ttl "%DUT_IP%"

rem bandwith test
"!TTPATH!\TTPMACRO.exe" /I /V .\ttl\GROUPBc.ttl "%DUT_IP%"

rem d Memtest
"!TTPATH!\TTPMACRO.exe" /I /V .\ttl\GROUPBd.ttl "%DUT_IP%"

REM wait 5 seconds
@ping %DUT_IP% -n 5 -w 1000 > nul

REM item D JPEG encoding&SD card R/W test
"!TTPATH!\TTPMACRO.exe" /I /V .\ttl\GROUPBe.ttl "%DUT_IP%"

rem f show memory info repeatly
REM "!TTPATH!\TTPMACRO.exe" /I /V .\ttl\GROUPBf.ttl "%DUT_IP%"

rem Vector process
"!TTPATH!\TTPMACRO.exe" /I /V .\ttl\GROUPBg.ttl "%DUT_IP%"

REM temprature info 
"!TTPATH!\TTPMACRO.exe" /I /V .\ttl\GROUPBh.ttl "%DUT_IP%"
REM ping 192.168.100.20 -t 