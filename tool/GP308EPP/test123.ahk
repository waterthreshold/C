#Requires AutoHotkey v2.0
#SingleInstance Force

; 1. 設定你的目標程式與元件名稱
TargetExe := "ahk_exe GS308EPP.exe"
TargetControl := "Button2"

; 2. 檢查程式是否正在運行
if !WinExist(TargetExe) {
    MsgBox("找不到目標程式 (" TargetExe ")，請先開啟程式！", "錯誤", 48)
    ExitApp() ; 找不到就直接關閉腳本
}

; 3. 找到目標元件並直接點擊
try {
    ; 直接對該視窗的 ClassNN 元件發送點擊指令（視窗在背景也能運作）
    ControlClick(TargetControl, TargetExe)
    
    ; 顯示一個短暫的提示，告訴你點擊成功了
    ToolTip("已成功點擊 " TargetControl)
    SetTimer(() => ToolTip(), -2000) ; 2 秒後自動隱藏提示
} 
catch Error as err {
    MsgBox("點擊失敗！錯誤訊息: " err.Message, "錯誤", 16)
}

; 執行完畢後自動結束腳本，不留在後台佔用資源
Sleep(2000)
ExitApp()
