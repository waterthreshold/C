param(
    [string]$TargetIP = "192.168.100.20", # 目標設備 IP
    [int]$Port = 23,                   # Telnet 預設埠口
    [string]$Username = "root",        # 帳號
    [string]$Password = ""             # 密碼（若有需要請填入）
)

# 1. 確認 IP 設備是否在線 (Ping 測試)
Write-Host "正在檢查設備 $TargetIP 是否在線..." -ForegroundColor Cyan
if (-not (Test-Connection -ComputerName $TargetIP -Count 1 -Quiet)) {
    Write-Host "錯誤：無法 Ping 到 $TargetIP，設備可能離線或禁用了 ICMP。" -ForegroundColor Red
    exit
}
Write-Host "設備在線，正在透過 TCP Socket 建立 Telnet 互動..." -ForegroundColor Green

try {
    # 2. 建立 TCP 連線模擬 Telnet 終端
    $client = New-Object System.Net.Sockets.TcpClient($TargetIP, $Port)
    $stream = $client.GetStream()
    $reader = New-Object System.IO.StreamReader($stream)
    $writer = New-Object System.IO.StreamWriter($stream)
    $writer.AutoFlush = $true

    # 讀取輸出訊息的輔助函式
    function Read-Output {
        param($StreamReader, $DelayMs = 1000)
        Start-Sleep -Milliseconds $DelayMs
        $output = ""
		# $output += [char]$StreamReader.Read()
        while ($StreamReader.Peek() -gt -1) {
            $output += [char]$StreamReader.Read()
        }
        return $output
    }

    # 接收初始歡迎畫面或登入提示
    $initialResponse = Read-Output $reader 1000
    Write-Host $initialResponse

    # 3. 輸入帳號 (root)
    $writer.WriteLine($Username)
    $loginPrompt = Read-Output $reader 1000
    Write-Host $loginPrompt

    # 4. 若需要輸入密碼（解開下方註解）
    # if ($Password -ne "") {
        # $writer.WriteLine($Password)
        # $passResponse = Read-Output $reader 1000
        # Write-Host $passResponse
    # }

    # 5. 執行 cat /proc/uptime 指令
    $writer.WriteLine("cat /proc/uptime")
    $result = Read-Output $reader 1500

    # 6. 打印結果
    Write-Host "=== 執行結果 ===" -ForegroundColor Yellow
    Write-Host $result

    # 7. 關閉連線
    $reader.Close()
    $writer.Close()
    $client.Close()
}
catch {
    Write-Host "執行過程中發生錯誤: $_" -ForegroundColor Red
}