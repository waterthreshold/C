Get-ChildItem -Recurse -File $args[0] |
Select-String -Pattern "fail","error" -SimpleMatch -CaseSensitive:$false |
 ForEach-Object {
     Write-Host "`nFILE: " -NoNewline -ForegroundColor Cyan
     Write-Host "$($_.Path)" -ForegroundColor White
     Write-Host "LINE: " -NoNewline -ForegroundColor Yellow
     Write-Host "$($_.LineNumber)" -ForegroundColor White
     Write-Host "TEXT: " -NoNewline -ForegroundColor Red
     Write-Host "$($_.Line)" -ForegroundColor White
 }