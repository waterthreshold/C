@echo off
setlocal enabledelayedexpansion

REM Check if iplist.txt exists
if not exist iplist.txt (
    echo iplist.txt not found!
    exit /b 1
)

REM Loop through each line in iplist.txt
for /f "tokens=*" %%i in (iplist.txt) do (
    set "target_ip=%%i"
    
    REM Ping the IP address once (-n 1) with a timeout (-w 1000 ms)
    ping -n 1 -w 1000 !target_ip! >nul 2>&1
    
    if !errorlevel! equ 0 (
        echo [SUCCESS] !target_ip! is reachable. Calling xxx.bat...
        if exist start_testA.bat (
            call start_testB.bat !target_ip!
        ) else (
            echo start.bat not found in the current directory!
        )
    ) else (
        echo [FAILED] !target_ip! did not respond.
    )
)

endlocal