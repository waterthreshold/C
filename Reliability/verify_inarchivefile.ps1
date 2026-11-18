param(
    [Parameter(Mandatory=$true)]
    [string]$ZipFile,

    [string]$Pattern = "fail|error"
)

Add-Type -AssemblyName System.IO.Compression.FileSystem

try {
    $zipArchive = [System.IO.Compression.ZipFile]::OpenRead($ZipFile)
}
catch {
    Write-Error "❌ Cannot open '$ZipFile'"
    exit 1
}

foreach ($entry in $zipArchive.Entries) {
    # Only check .log files (remove this if you want to search all files)
    if ($entry.Length -gt 0 -and $entry.FullName -match '\.log$') {
        $reader = New-Object IO.StreamReader($entry.Open())
        $lineNumber = 0
        while (($line = $reader.ReadLine()) -ne $null) {
            $lineNumber++
            if ($line -match $Pattern) {
                Write-Host "[$($entry.FullName):$lineNumber] $line"
            }
        }
        $reader.Close()
    }
}

$zipArchive.Dispose()
