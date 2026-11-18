# Setup paths anchored to the script's actual directory
$defaultconfigpath = Join-Path $env:USERPROFILE "configs" "DeviceDeploy.json"
$defaultbinpath = Join-Path $env:USERPROFILE "bin"

# Ensure target directories exist
if (!(Test-Path (Split-Path $defaultconfigpath))) {
    New-Item -ItemType Directory -Force -Path (Split-Path $defaultconfigpath) | Out-Null
}
if (!(Test-Path $defaultbinpath)) {
    New-Item -ItemType Directory -Force -Path $defaultbinpath | Out-Null
}

# 1. Check and install Posh-SSH module
if (Get-Module -Name "Posh-SSH" -ListAvailable) {
    Write-Host "Posh-SSH is installed." -ForegroundColor Green
} else {
    Write-Warning "Posh-SSH is NOT installed. Installing..."
    Install-Module -Name Posh-SSH -Force -Scope CurrentUser
}

# 2. Backup and copy configuration file with Checksum check
$sourceConfig = Join-Path $PSScriptRoot "DeviceDeploy.json"
if (Test-Path $sourceConfig) {
    $needsCopy = $false
    if (!(Test-Path $defaultconfigpath)) {
        $needsCopy = $true
    } else {
        $srcHash = (Get-FileHash -Path $sourceConfig -Algorithm SHA256).Hash
        $destHash = (Get-FileHash -Path $defaultconfigpath -Algorithm SHA256).Hash
        if ($srcHash -ne $destHash) {
            $needsCopy = $true
            $bakconfg = "${defaultconfigpath}.bak"
            Copy-Item -Path $defaultconfigpath -Destination $bakconfg -Force
            Write-Host "[+] Config checksum mismatch. Backed up existing config to $bakconfg" -ForegroundColor Cyan
        }
    }

    if ($needsCopy) {
        Copy-Item -Path $sourceConfig -Destination $defaultconfigpath -Force
        Write-Host "[+] Updated DeviceDeploy.json successfully" -ForegroundColor Green
    } else {
        Write-Host "[+] DeviceDeploy.json is already up to date (checksum matches)" -ForegroundColor Gray
    }
} else {
    Write-Warning "Source DeviceDeploy.json not found at $sourceConfig"
	Write-Warning "Please  fillin remote target server in DeviceDeploy_.json and save as DeviceDeploy.json"
	exit 1
}

# Helper function to check checksum and force copy binaries/scripts
function Update-FileWithChecksum {
    param (
        [string]$SourcePath,
        [string]$DestinationPath,
        [string]$ItemName
    )

    $needsCopy = $false
    if (!(Test-Path $DestinationPath)) {
        $needsCopy = $true
        Write-Host "[+] $ItemName not found at destination. Installing..." -ForegroundColor Cyan
    } else {
        $srcHash = (Get-FileHash -Path $SourcePath -Algorithm SHA256).Hash
        $destHash = (Get-FileHash -Path $DestinationPath -Algorithm SHA256).Hash
        if ($srcHash -ne $destHash) {
            $needsCopy = $true
            Write-Host "[+] Checksum mismatch for $ItemName. Forcing update..." -ForegroundColor Yellow
        }
    }

    if ($needsCopy) {
        Copy-Item -Path $SourcePath -Destination $DestinationPath -Force
        Write-Host "[+] Successfully installed/updated $ItemName" -ForegroundColor Green
    } else {
        Write-Host "[+] $ItemName is already up to date (checksum matches)" -ForegroundColor Gray
    }
}

# 3. Check and install PartitionUploadClt.exe
$sourcePart = Join-Path $PSScriptRoot "Part.exe"
$destPart = Join-Path $defaultbinpath "PartitionUploadClt.exe"
if (Test-Path $sourcePart) {
    Update-FileWithChecksum -SourcePath $sourcePart -DestinationPath $destPart -ItemName "PartitionUploadClt.exe"
} else {
    Write-Error "Source Part.exe not found at $sourcePart"
}

# 4. Check and install ProdFWupgrade.ps1
$sourceScript = Join-Path $PSScriptRoot "ProdFWupgrade.ps1"
$destScript = Join-Path $defaultbinpath "ProdFWupgrade.ps1"
if (Test-Path $sourceScript) {
    Update-FileWithChecksum -SourcePath $sourceScript -DestinationPath $destScript -ItemName "ProdFWupgrade.ps1"
} else {
    Write-Error "Source ProdFWupgrade.ps1 not found at $sourceScript"
}