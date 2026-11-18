@echo off 
REM cmd /c "C:\Users\10008847\scoop\apps\teraterm\5.4.0\ttermpro.exe /M=C:\Users\10008847\Desktop\Reliability\ttl\GROUPC.ttl"
REM ping 192.168.100.20 -t 
@echo off
setlocal EnableDelayedExpansion
set FILE=ttpath.txt

if exist "%FILE%" (
    for /f "delims=" %%x in (%FILE%) do set TTPATH=%%x
    echo TTPATH variable is: !TTPATH!
) else (
    echo File not found
)

REM set /p DUT_IP=Please enter the IP address: 
echo main PATH: !TTPATH!\TTPMACRO.exe
REM echo IP=%DUT_IP% 
"!TTPATH!\ttermpro.exe" /F=C:\Users\10008847\Desktop\Reliability\GC_setting.INI /M=C:\Users\10008847\Desktop\Reliability\ttl\GROUPC.ttl

REM ping 192.168.100.20 -t 