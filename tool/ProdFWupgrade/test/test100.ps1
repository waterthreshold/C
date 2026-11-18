param(
    [int]$count = 100,
    
    [Parameter(Mandatory = $true)]
    [string]$model
)

$timestamp = Get-Date -Format "yyyy-MM-dd-HH-mm-ss"
$logname = "$model-${count}TimeTest_${timestamp}.txt"  

1..$count | ForEach-Object {
    $i = $_
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    
    # Execute your firmware upgrade script
    ..\ProdFWupgrade.ps1 -model $model -ssh
    
    $sw.Stop()
    
    # Fix: Use sub-expressions $(...) so properties resolve correctly inside strings
    "$LASTEXITCODE, $($sw.Elapsed.TotalSeconds)" | Out-File -FilePath "$logname" -Append
    
    Write-Host "Iteration $i/$count - Elapsed Time: $($sw.ElapsedMilliseconds) ms ($($sw.Elapsed.TotalSeconds) seconds)" -ForegroundColor Green
    
    Start-Sleep -Seconds 1
}
