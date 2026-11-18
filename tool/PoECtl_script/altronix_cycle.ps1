param(
    [string]$HostIP,
    [int]$CONTROL_PORT,
    [string]$Username = "admin",
    [string]$Password = "admin"
)

$url = "http://${HostIP}/ATX/hardware/poe/ports/${CONTROL_PORT}/pulse"

# Create credential
$securePassword = ConvertTo-SecureString $Password -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($Username, $securePassword)

try {

    $response = Invoke-WebRequest `
        -Uri $url `
        -Method POST `
        -Credential $credential `
        -AllowUnencryptedAuthentication `
        -UseBasicParsing

    Write-Host "Pulse command sent successfully"
    Write-Host "HTTP Status:" $response.StatusCode
}
catch {
    Write-Host "Request failed:"
    Write-Host $_
}