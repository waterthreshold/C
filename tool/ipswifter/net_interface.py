import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import json
import os
import base64

CONFIG_FILE = "net_config_setting.json"
APP_VERSION="1.0"
def load_last_interface():
    """讀取上次記憶的網卡名稱"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("last_interface", "")
        except Exception:
            pass
    return ""

def save_last_interface(iface_name):
    """儲存選取的網卡名稱"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"last_interface": iface_name}, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"儲存設定失敗: {e}")

def get_physical_wired_adapters():
    """透過 PowerShell 徹底重新查詢所有實體有線網卡及其最新 IP 與 DHCP 狀態"""
    cmd = 'powershell -NoProfile -Command "Get-NetAdapter | ForEach-Object { $config = Get-NetIPConfiguration -InterfaceIndex $_.ifIndex -ErrorAction SilentlyContinue; $ip = if ($config.IPv4Address.IPAddress) { $config.IPv4Address.IPAddress } else { \'DHCP/無IP\' }; $dhcpIf = Get-NetIPInterface -InterfaceIndex $_.ifIndex -AddressFamily IPv4 -ErrorAction SilentlyContinue; $isDhcp = if ($dhcpIf) { $dhcpIf.Dhcp -eq \'Enabled\' } else { $true }; [PSCustomObject]@{ Name = $_.Name; Description = $_.InterfaceDescription; Virtual = $_.Virtual; IP = $ip; IsDhcp = $isDhcp } } | ConvertTo-Json -Compress"'
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True, encoding='cp950', errors='ignore')
        
        if result.returncode != 0 or not result.stdout or not result.stdout.strip():
            return []
            
        adapters = json.loads(result.stdout.strip())
        if isinstance(adapters, dict):
            adapters = [adapters]
            
        valid_adapters = []
        for ad in adapters:
            name = ad.get('Name', '')
            desc = ad.get('Description', '')
            is_virtual = ad.get('Virtual', False)
            ip = ad.get('IP', 'DHCP/無IP')
            is_dhcp = ad.get('IsDhcp', True)
            combined = (name + " " + desc).lower()
            
            # 1. 排除虛擬網卡
            if is_virtual:
                continue
                
            # 2. 排除無線網卡與藍牙
            if any(k in combined for k in ['wi-fi', 'wireless', '802.11', 'wlan', 'bluetooth']):
                continue
                
            display_str = f"[{name}]-{ip}"
            valid_adapters.append({
                "display": display_str,
                "name": name,
                "ip": ip,
                "is_dhcp": is_dhcp
            })
            
        return valid_adapters
    except Exception as e:
        print(f"取得網卡失敗: {e}")
        return []

class NetworkConfigApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Windows 網路快速設定工具")
        self.root.geometry("640x380")
        self.root.resizable(False, False)
        self.raw_icon_data = base64.b64decode(
            b"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"
        )
        
        try:
            # self.app_icon = 
            self.root.iconphoto(True, tk.PhotoImage(data=self.raw_icon_data))
        except Exception as e:
            print(f"--- PARSE ERROR ---{e}")
            
        # 設定整體風格
        style = ttk.Style()
        style.theme_use('clam')
        
        # 標題
        title_label = tk.Label(root, text="網卡與 IP 快速設定精靈", font=("Arial", 14, "bold"), fg="#333333")
        title_label.pack(pady=15)
        
        # 主框架
        main_frame = ttk.LabelFrame(root, text=" 網路設定參數 ", padding=15)
        main_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        # 1. 網卡選擇
        ttk.Label(main_frame, text="選擇有線實體網卡:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        
        self.interface_combo = ttk.Combobox(main_frame, state="readonly", width=30, font=("Arial", 10))
        self.interface_combo.grid(row=0, column=1, sticky="w", pady=5, padx=5)
        # 繫結選擇事件：當切換網卡時自動同步該網卡的 IP 狀態
        self.interface_combo.bind("<<ComboboxSelected>>", self.on_interface_selected)
        
        refresh_btn = ttk.Button(main_frame, text="重新整理", command=self.refresh_adapters_action)
        refresh_btn.grid(row=0, column=2, padx=5)
        
        # 2. IP 模式選擇
        ttk.Label(main_frame, text="IP 取得方式:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=15)
        
        self.ip_mode = tk.StringVar(value="dhcp")
        dhcp_radio = ttk.Radiobutton(main_frame, text="DHCP (自動取得)", variable=self.ip_mode, value="dhcp", command=self.toggle_mode)
        dhcp_radio.grid(row=1, column=1, sticky="w", pady=5)
        
        static_radio = ttk.Radiobutton(main_frame, text="Static (固定 IP)", variable=self.ip_mode, value="static", command=self.toggle_mode)
        static_radio.grid(row=2, column=1, sticky="w", pady=5)
        
        # 3. 完整 IP 地址輸入
        ttk.Label(main_frame, text="固定 IP 地址:", font=("Arial", 10)).grid(row=3, column=0, sticky="w", pady=5)
        
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=3, column=1, sticky="w", pady=5)
        
        self.ip_entry_var = tk.StringVar(value="192.168.1.100")
        self.ip_entry = ttk.Entry(input_frame, textvariable=self.ip_entry_var, width=20, font=("Arial", 10))
        self.ip_entry.pack(side="left")
        
        # 4. 套用按鈕
        apply_btn = tk.Button(root, text="立即套用設定", bg="#007ACC", fg="white", font=("Arial", 11, "bold"), padx=10, pady=5, command=self.apply_settings)
        apply_btn.pack(pady=15)
        
        # 儲存網卡的對應對照清單
        self.adapters_list = []
        
        # 初始化載入網卡與記憶選擇
        self.refresh_adapters(silent=True)
        self.toggle_mode()

    def refresh_adapters(self, silent=False):
        """重新向系統查詢並 renew 網卡清單與狀態"""
        self.adapters_list = get_physical_wired_adapters()
        display_values = [ad["display"] for ad in self.adapters_list]
        self.interface_combo['values'] = display_values
        
        if self.adapters_list:
            last_iface = load_last_interface()
            match_index = 0
            for idx, ad in enumerate(self.adapters_list):
                if ad["name"] == last_iface:
                    match_index = idx
                    break
            self.interface_combo.current(match_index)
            self.on_interface_selected()
        else:
            self.interface_combo['values'] = ["未偵測到有線實體網卡"]
            self.interface_combo.set("未偵測到有線實體網卡")
            
        if not silent:
            messagebox.showinfo("提示", "已成功重新整理並更新所有網卡狀態！")

    def refresh_adapters_action(self):
        """點擊重新整理按鈕時觸發"""
        self.refresh_adapters(silent=False)

    def on_interface_selected(self, event=None):
        """當切換下拉選單網卡時，自動套用該網卡的目前設定狀態"""
        selected_idx = self.interface_combo.current()
        if selected_idx < 0 or not self.adapters_list:
            return
            
        ad = self.adapters_list[selected_idx]
        
        # 根據系統的 DHCP 狀態切換 Radiobutton
        if ad.get("is_dhcp", True):
            self.ip_mode.set("dhcp")
        else:
            self.ip_mode.set("static")
           
        ip = ad.get("ip", "")
        if ip:
            self.ip_entry_var.set(ip)
            
        self.toggle_mode()

    def toggle_mode(self):
        if self.ip_mode.get() == "static":
            self.ip_entry.config(state="normal")
        else:
            self.ip_entry.config(state="disabled")

    def apply_settings(self):
        selected_idx = self.interface_combo.current()
        if selected_idx < 0 or not self.adapters_list or self.interface_combo.get() == "未偵測到有線實體網卡":
            messagebox.showerror("錯誤", "請先選擇有效的網路介面卡！")
            return
            
        selected_iface = self.adapters_list[selected_idx]["name"]
        save_last_interface(selected_iface)
        
        mode = self.ip_mode.get()
        
        if mode == "dhcp":
            cmd = f'powershell -Command "Start-Process netsh -ArgumentList \'interface ip set address \\\"{selected_iface}\\\" source=dhcp\' -Verb RunAs -Wait"'
            msg = f"已成功將網卡 [{selected_iface}] 設定為 DHCP 自動取得 IP！"
        else:
            ip_address = self.ip_entry_var.get().strip()
            if not ip_address:
                messagebox.showerror("格式錯誤", "請輸入合法的 IP 地址！")
                return
                
            subnet_mask = "255.255.255.0"
            
            cmd = f'powershell -Command "Start-Process netsh -ArgumentList \'interface ip set address \\\"{selected_iface}\\\" static {ip_address} {subnet_mask}\' -Verb RunAs -Wait"'
            msg = f"已成功將網卡 [{selected_iface}] 設定為固定 IP:\nIP: {ip_address}\n遮罩: {subnet_mask}"

        try:
            subprocess.run(cmd, shell=True, check=True)
            messagebox.showinfo("完成", msg)
            self.refresh_adapters(silent=True)
        except Exception as e:
            messagebox.showerror("執行失敗", f"設定網路時發生錯誤：\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = NetworkConfigApp(root)
    root.mainloop()