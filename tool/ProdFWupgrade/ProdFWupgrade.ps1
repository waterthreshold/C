<#
.SYNOPSIS
    Automated device communication and flashing script.
.DESCRIPTION
    1. Checks if port 80 is open on the target IP.
    2. Sends an HTTP GET request to trigger the upload service CGI endpoint.
    3. Validates that the response contains "code=0".
    4. Checks if TCP port 4999 is listening.
    5. Executes the specified tool with the required arguments.
#>

param(
    [string]$ip = "" ,
    [string]$fw_path ,
    [switch]$httpsupport ,
    [string]$model,
    [string]$config_path = "DeviceDeploy.json",
    [string]$username = "admin",
    [string]$password = "password",
    [string]$executablePath =  "PartitionUploadClt.exe",
	[switch]$listdevice ,
	[switch]$ssh
)

# Helper function to check TCP port 4999
function Test-DutPort4999 {
    param([string]$TargetIp)
    Write-Host "[+] Response received containing 'code=0'." -ForegroundColor Green
    Write-Host "[*] Checking port 4999 on $TargetIp..." -ForegroundColor Cyan
    
    $port4999Check = Test-NetConnection -ComputerName $TargetIp -Port 4999 -InformationLevel Quiet

    if ($port4999Check) {
        Write-Host "[+] Port 4999 is listening." -ForegroundColor Green
        return $true
    } else {
        Write-Warning "[-] Port 4999 is not listening on $TargetIp."
        return $false
    }
}

function Test-DutPort80(){
	param([string]$TargetIp)

	Write-Host "[*] Checking port 80 on $ip..." -ForegroundColor Cyan
    $port80Check = Test-NetConnection -ComputerName $TargetIp -Port 80 -InformationLevel Quiet

    if ($port80Check) {
        Write-Host "[+] Port 80 is listening." -ForegroundColor Green

        # Step 2: Send HTTP GET request
        $url = "http://$ip/cgi-bin/SetUploadSrv.cgi?Action=start"
        Write-Host "[*] Sending HTTP GET request to: $url" -ForegroundColor Cyan

        try {
            $pair = "${username}:${password}"
            $bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
            $base64 = [System.Convert]::ToBase64String($bytes)
            $headers = @{ Authorization = "Basic $base64" }

            $response = Invoke-WebRequest -Uri $url -Method Get -Headers$headers -UseBasicParsing -TimeoutSec 10
            $content =$response.Content

            if ($content -match "code=0") {
               return $true
            } else {
                Write-Warning "[-] Response did not contain 'code=0'. Response content: $content"
				return $false
            }
        }
        catch {
            Write-Error "[-] Failed to complete HTTP request: $_"
            return $false
        }
    } else {
        Write-Warning "[-] Port 80 is not listening on $ip."
		return $false
    }
}

function Invoke-RemotePartitionUploadSrv {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$ComputerName,

        [Parameter(Mandatory = $false)]
        [int]$Port = 22
    )

    process {
        try {
            Write-Host "Connecting to $ComputerName on port $Port..." -ForegroundColor Cyan

            # For passwordless root login, we can use an empty PSCredential or pass username only depending on Posh-SSH version,
            # or use a safe null/empty handling for PSCredential:
            $username = "root"
            
            # Alternative: Create credential using a non-empty placeholder if the module strictly requires it, 
            # or pass credentials explicitly. If password is truly blank, we construct the secure string safely:
            $securePassword = (New-Object System.Security.SecureString) # Creates an empty secure string safely
            $cred = New-Object System.Management.Automation.PSCredential ($username, $securePassword)

            # Establish SSH connection session
            $session = New-SSHSession -ComputerName $ComputerName -Credential $cred -Port $Port -AcceptKey -ErrorAction Stop

            if ($session -and $session.SessionId) {
                $sessionId = $session.SessionId
                Write-Host "Successfully connected. Launching background service..." -ForegroundColor Green

                $remoteCommand = "killall PartitionUploadSrv;/root/PartitionUploadSrv &"
                $result = Invoke-SSHCommand -SessionId $sessionId -Command $remoteCommand -TimeOut 5

                if ($result -and $result.ExitStatus -eq 0) {
                    Write-Host "Command sent successfully:" -ForegroundColor Green
                    if ($result.Output) { $result.Output }
                } else {
                    Write-Warning "Command returned exit status $($result.ExitStatus):"
                    if ($result.Output) { $result.Output }
                }

                Remove-SSHSession -SessionId $sessionId | Out-Null
            }
        }
        catch {
            if ($_.Exception.Message -match "timeout|timed out") {
                Write-Host "Service initiated successfully (background process reached timeout threshold as expected)." -ForegroundColor Green
            } else {
                Write-Error "Failed to connect or execute command: $_"
				exit 1
            }
        }
}
}


# 1. Check if config file exists
$fallbackConfigPath = Join-Path $env:USERPROFILE "configs" "DeviceDeploy.json"
if (-not (Test-Path  $config_path)) {
    if (Test-Path -Path $fallbackConfigPath) {
        Write-Host "[*] Local config not found. Using fallback profile config: $fallbackConfigPath" -ForegroundColor Cyan
        $config_path = $fallbackConfigPath
    } else {
        Write-Error "[-] Configuration file not found at path: $config_path or fallback path: $fallbackConfigPath"
        exit 1
    }
} 
    
	$jsonContent = Get-Content -Path $config_path -Raw | ConvertFrom-Json
	Write-Host "[+] Configuration Extract Successfully!" -ForegroundColor Green


if ($listdevice ) {
	foreach ($projectName in $jsonContent.projects.PSObject.Properties.Name) {
		$projectData = $jsonContent.projects.$projectName
		# Write-Host "-------------------------------------------------------" -ForegroundColor Green
		Write-Host "Project Name: $projectName" -ForegroundColor Cyan
		Write-Host "Default IP: $($projectData.default_ip)" -ForegroundColor Green
		Write-Host "Path: $($projectData.path)" -ForegroundColor Yellow
			if ($projectData.parameter) {
			foreach ($paramKey in $projectData.parameter.PSObject.Properties.Name) {
				$paramVal = $projectData.parameter.$paramKey
				Write-Host "  Parameter -> $paramKey : $paramVal"
			}
		}
		Write-Host "----------------------------------------"
		# Write-Host "-------------------------------------------------------" -ForegroundColor Green
	}
	exit 0 
}

if ([string]::IsNullOrEmpty($model)) {
    Write-Error "[-] Error: The -model parameter is required unless -listdevice is specified."
    Write-Host "Usage: ./DeviceDeploy.ps1 -model <model_name> OR ./DeviceDeploy.ps1 -listdevice" -ForegroundColor Yellow
    exit 1
}
# Resolve IP from JSON if not provided
if ([string]::IsNullOrEmpty($ip)) {
    if ($model -and $jsonContent.projects.$model) {
		$ip = $jsonContent.projects.$model.default_ip
		 Write-Host "[+] IP is $ip." -ForegroundColor Green
    } else {
        Write-Error "[-] IP address is not provided and could not be resolved from model: $model"
        exit 1
    }
}

if ( $httpsupport ) {
		if ( -not  (Test-DutPort80 -TargetIp $ip )) {
				Write-Error "[-] Port 80 check failed. Handling failure..."
				exit 1
		} 
}
if ($ssh) {
	Write-Host "SSH $ip" -ForegroundColor Green
	Invoke-RemotePartitionUploadSrv -ComputerName $ip -Port 22
}
# Step 1: Check if target port 80 is listening (Branch where local fw_path is provided)

    # Branch where $fw_path is empty: Download configuration and firmware from FTP server
    $protocol =$jsonContent.server.protocol
    $serverUrlBase =$jsonContent.server.url
    $srvUsername =$jsonContent.server.username
    $srvPassword =$jsonContent.server.password
    
    Write-Host "[*] Connecting to $protocol $serverUrlBase..." -ForegroundColor Cyan

    $webClient =$null
    try {
        $webClient = New-Object System.Net.WebClient
        $webClient.Credentials = New-Object System.Net.NetworkCredential($srvUsername,$srvPassword)
        Write-Host "[+] Credential!" -ForegroundColor Green
        $localDestinationPath = Get-Location 
		$projectPath = $jsonContent.projects.$model.path
        $serverFolderUrl = "$protocol`://$serverUrlBase$projectPath"
        $fwConfigRemotePath = "$serverFolderUrl/ProdFW.json"
        $localConfigPath = Join-Path $localDestinationPath "ProdFW.json"

        Write-Host "[*] Downloading config to: $localConfigPath from $fwConfigRemotePath" -ForegroundColor Cyan
        $webClient.DownloadFile($fwConfigRemotePath, $localConfigPath)
        Write-Host "[+] Download config completed successfully!" -ForegroundColor Green

        $fwConfigContent = Get-Content -Path $localConfigPath -Raw | ConvertFrom-Json
        
        # Adjust property lookup based on JSON schema structure
        $fwName = $fwConfigContent.fw_name
		$expeced_clt_ver = $fwConfigContent.clt_ver
        if (-not $fwName) { 
			Write-Error "[-] Failed to fetch $fwName"		
			exit 1
		}
		if ([string]::IsNullOrEmpty($fw_path)) {
			$fwRemotePath = "$serverFolderUrl/$fwName"
			$localFwPath = Join-Path $localDestinationPath $fwName
			if ( -not (Test-Path -Path $localFwPath)) {
				Write-Host "[*] Downloading firmware from $fwRemotePath..." -ForegroundColor Cyan
				$webClient.DownloadFile($fwRemotePath, $localFwPath)
				Write-Host "[+] Download firmware completed successfully!" -ForegroundColor Green
			} else {
				Write-Host "[+] $localFwPath Found!" -ForegroundColor Green
			}
		} elseif (Test-Path -Path "$fw_path" ) {
			$localFwPath = $fw_path
			Write-Host "[+] $localFwPath found!" -ForegroundColor Green
		} else {
			Write-Error "[-] $fw_path not exist!" 
			exit 1 
		}
        # if (Test-DutPort4999 -TargetIp $ip) {
			$isdownloadclienttool = $false
			
			$executablePath= Join-Path $localDestinationPath $executablePath
			Write-Host "[*] Executing: $executablePath $arguments" -ForegroundColor Yellow 
			if (Get-Command "PartitionUploadClt.exe" -ErrorAction SilentlyContinue) {
				$executablePath = (Get-Command "PartitionUploadClt.exe").Source
				 Write-Host "[+] Found command $executablePath." -ForegroundColor Green
			}
			elseif ( -not (Test-Path -Path  $executablePath)) {
				 $remoteclienttool= "$serverFolderUrl/PartitionUploadClt.exe"
				 $webClient.DownloadFile($remoteclienttool, $executablePath)
				 Write-Host "[+] Download to $executablePath from $remoteclienttool successfully." -ForegroundColor Green
				 $isdownloadclienttool = $true
			} else {
				Write-Host "[+] PartitionUploadClt.exe exist in current directory!" 
			}
			
			
            $arguments = "-i $ip --verbose --zip `"$localFwPath`""  # Dynamically append parameters defined in the JSON project profile
			$parameters = $jsonContent.projects.$model.parameter 
			if ($parameters) { 
				foreach ($key in $parameters.PSObject.Properties.Name) 
				{
					$val = $parameters.$key
					switch ($key) 
					{ 
						"identification" 
							{ $arguments += " -I $val" } 
						"sap" { $arguments += " --sap $val" }
						"crc" { if ($val -eq $true) { $arguments += " --crc" } }
						"erase_partition" { foreach ($item in $val) { $arguments += " --erase-partition $item" } }
					}
				} 
			} 
			
			$partitionclt_version = (& $executablePath --version)
			# $partitionclt_version.Split()[-1].Trim()
			write-host "PartitionUploadClt Expected version: $expeced_clt_ver"  -ForegroundColor Cyan
			write-host "Current Use version: $partitionclt_version"  -ForegroundColor Cyan
			# (& "$executablePath" --version).Split()[-1].Trim()
			Start-Process -FilePath $executablePath -ArgumentList $arguments -NoNewWindow -Wait 
			Write-Host "[+] Process execution completed successfully." -ForegroundColor Green 
		# }
		# else { Write-Error "[-] Port 4999 check failed. Exiting program." exit 1 
		# } 
} 
		catch { 
			Write-Error "[-] Failed to download file from FTP: $_" 
			exit 1
		}
		finally { 
			if ($webClient) { $webClient.Dispose() }
			if (Test-Path -Path "$localConfigPath") {
				Remove-Item -Path "ProdFW.json"
				Write-Host "[+]  Remove Config Successfully!" -ForegroundColor Green 
			}
			
			if ($isdownloadclienttool -eq $true) {
				Remove-Item -Path "$executablePath"
				Write-Host "[+]  Remove Cliet tool Successfully!" -ForegroundColor Green 
			}
		} 
		