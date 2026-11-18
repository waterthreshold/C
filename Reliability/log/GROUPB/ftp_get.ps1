$ftpServer = "172.16.7.37"
$username  = "root"
$password  = ""
$localPath = "C:\Users\10008847\Desktop\20250909_115504_GROUPA"

# Create WebClient object
$webclient = New-Object System.Net.WebClient
$webclient.Credentials = New-Object System.Net.NetworkCredential($username, $password)

# Get file list from FTP
$uri = [System.Uri]$ftpServer
$request = [System.Net.FtpWebRequest]::Create($uri)
$request.Method = [System.Net.WebRequestMethods+Ftp]::ListDirectory
$request.Credentials = New-Object System.Net.NetworkCredential($username, $password)
$response = $request.GetResponse()
$reader = New-Object IO.StreamReader $response.GetResponseStream()
$files = @()
while(-not $reader.EndOfStream) {
    $files += $reader.ReadLine()
}
$response.Close()

# Filter only files like sd_loop_test_result_X
$files | Where-Object { $_ -like "sd_loop_test_result_*" } | ForEach-Object {
    $remoteFile = "$ftpServer$_"
    $localFile  = Join-Path $localPath $_
    Write-Host "Downloading: $remoteFile -> $localFile" -ForegroundColor Cyan
    $webclient.DownloadFile($remoteFile, $localFile)
}
