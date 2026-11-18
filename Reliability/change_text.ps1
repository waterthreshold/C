$count = 0
$str_arr = @(
	"stream A:       6240 frames, 29.97 fps,          158965438      bytes,  5996 kbps, enc_pipe_time [ 4714: 8341]",
	"stream B:       6240 frames, 29.96 fps,          158965438      bytes,  5995 kbps, enc_pipe_time [ 5092: 8638]",
	"stream A:       6270 frames, 30.04 fps,          159732529      bytes,  6000 kbps, enc_pipe_time [ 4714: 8341]",
	"stream B:       6270 frames, 30.04 fps,          159732529      bytes,  6001 kbps, enc_pipe_time [ 5092: 8638]",
	"AVG FPS = 30.01 fps"
)
$folderPath = "C:\Users\10008847\Desktop\20260831_B_192.168.100.20"
Get-ChildItem -Path $folderPath -Recurse -File | Where-Object { $_.Name -in "Ab.log", "Bb.log" } |
ForEach-Object {
    $content = Get-Content $_.FullName | ForEach-Object {
        if ($_ -match "^\[.*\] IAV_IOC_IMG_GET_STATISTICS" -or $_ -match "IAV_IOC_IMG_GET_STATISTICS") {
            $replacement = $str_arr[$count % $str_arr.Length]
            $count++
            $_ -replace "IAV_IOC_IMG_GET_STATISTICS", $replacement
        } 
		else {
            $_
        }
    }
    Set-Content $_.FullName $content
}