import tkinter as tk
from tkinter import ttk, messagebox
import socket
import threading
import ipaddress
import struct
import base64
class IPScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("IPyscanner V1.00 - Jeff Edition")
        self.root.geometry("820x560")
        self.root.minsize(780, 520)
        try:
            icon_data = base64.b64decode(
                b"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"
            )
            self.app_icon = tk.PhotoImage(data=icon_data)
            self.root.iconphoto(True, self.app_icon)
        except Exception as e:
            import traceback
            print(f"--- PARSE ERROR ---")
            print(f"Exception: {e}")
            print(f"Packet length received: {len(raw_packet) if 'raw_packet' in locals() else 'N/A'} bytes")
            traceback.print_exc()
            print("-------------------")
            # pass
        
        self.device_packets = {}
        # Use modern styling configuration via ttk Style
        self.style = ttk.Style()
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        # Custom UI styling tweaks
        self.style.configure(".", font=("Segoe UI", 10))
        self.style.configure("TButton", padding=6, relief="flat", background="#e1e1e1")
        self.style.configure("Heading.TLabel", font=("Segoe UI", 11, "bold"))

        self.create_widgets()
        self.load_network_interfaces()
        
        self.changedbutton = False
    def sort_column(self, col, reverse):
        try:
            data_list = [(self.tree.set(child, col), child) for child in self.tree.get_children('')]
        except Exception:
            return

        # Sort logically (handles IP addresses/numbers numerically if possible, otherwise alphabetically)
        try:
            data_list.sort(key=lambda x: [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', x[0])], reverse=reverse)
        except Exception:
            data_list.sort(key=lambda x: x[0].lower(), reverse=reverse)

        # Rearrange items in treeview
        for index, (val, child) in enumerate(data_list):
            self.tree.move(child, '', index)

        # Toggle sort direction on next header click
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))
        
    def create_widgets(self):
        # --- Top Control Bar (Interface selector & DHCP mode radios) ---
        top_frame = ttk.LabelFrame(self.root, text=" Network Interface & Configuration ", padding=12)
        top_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(top_frame, text="Active Interface IP:").grid(row=0, column=0, sticky="w", padx=5)
        
        self.interface_cb = ttk.Combobox(top_frame, state="readonly", width=22)
        self.interface_cb.grid(row=0, column=1, padx=5, sticky="w")
        self.interface_cb.bind("<<ComboboxSelected>>", self.on_interface_selected)

        # IP mode variables
        self.ip_mode_var = tk.StringVar(value="dhcp")
        self.radio_static = ttk.Radiobutton(top_frame, text="固定 IP (Static)", variable=self.ip_mode_var, value="static", command=self.toggle_ip_mode)
        self.radio_static.grid(row=0, column=2, padx=15)
        
        self.radio_dhcp = ttk.Radiobutton(top_frame, text="自動取得 (DHCP)", variable=self.ip_mode_var, value="dhcp", command=self.toggle_ip_mode)
        self.radio_dhcp.grid(row=0, column=3, padx=5)

        # --- Main Content Split (Left: Table/Search, Right: Device Properties Form) ---
        content_frame = ttk.Frame(self.root)
        content_frame.pack(fill="both", expand=True, padx=15, pady=5)

        # Left Side: Treeview Table & Search Button
        left_pane = ttk.Frame(content_frame)
        left_pane.pack(side="left", fill="both", expand=True, padx=(0, 10))

        table_frame = ttk.Frame(left_pane)
        table_frame.pack(fill="both", expand=True, pady=(0, 10))

        # Scrollbars for treeview
        tree_scroll = ttk.Scrollbar(table_frame)
        tree_scroll.pack(side="right", fill="y")

        # Table columns setup
        self.tree = ttk.Treeview(table_frame, columns=("hostname", "ip"), show="headings", yscrollcommand=tree_scroll.set, selectmode="browse")
        self.tree.heading("hostname", text="主機名稱 (Hostname)", command=lambda: self.sort_column("hostname", False))
        self.tree.heading("ip", text="IP 位址 (IP Address)", command=lambda: self.sort_column("ip", False))
        self.tree.column("hostname", width=170, anchor="w")
        self.tree.column("ip", width=140, anchor="w")
        self.tree.pack(fill="both", expand=True)
        tree_scroll.config(command=self.tree.yview)

        # Bind row selection to load details
        self.tree.bind("<<TreeviewSelect>>", self.on_device_select)

        # Search / Broadcast Action Button
        self.search_btn = ttk.Button(left_pane, text="搜尋設備 (Scan / Broadcast)", command=self.start_broadcast_scan)
        self.search_btn.pack(fill="x", ipady=4)

        # Right Side: Detailed Properties Form
        right_pane = ttk.LabelFrame(content_frame, text=" 設備詳細參數 (Device Properties) ", padding=12)
        right_pane.pack(side="right", fill="y", padx=(5, 0))

        fields = [
            ("設備名稱 (Name):", "ent_name"),
            ("IP 位址 (IP):", "ent_ip"),
            ("遮罩位置 (Netmask):", "ent_mask"),
            ("閘道位置 (Gateway):", "ent_gateway"),
            ("DNS 伺服 (DNS 1):", "ent_dns1"),
            ("DNS 伺服 (DNS 2):", "ent_dns2"),
            ("埠位置 (Port):", "ent_port"),
            ("硬體位置 (MAC):", "ent_mac")
        ]

        self.form_entries = {}
        for idx, (label_text, key) in enumerate(fields):
            lbl = ttk.Label(right_pane, text=label_text)
            lbl.grid(row=idx, column=0, sticky="w", pady=4)
            ent = ttk.Entry(right_pane, width=24)
            ent.grid(row=idx, column=1, padx=8, pady=4, sticky="ew")
            self.form_entries[key] = ent

        # --- Bottom Control Action Bar ---
        bottom_frame = ttk.Frame(self.root)
        bottom_frame.pack(fill="x", padx=15, pady=12)

        self.modify_btn = ttk.Button(bottom_frame, text="修改 (Modify Settings)", command=self.on_modify_click)
        self.modify_btn.pack(side="left", ipadx=10)

        self.exit_btn = ttk.Button(bottom_frame, text="離開 (Exit)", command=self.root.quit)
        self.exit_btn.pack(side="right", ipadx=10)

    def load_network_interfaces(self):
        """Fetch local machine IP addresses to populate the interface dropdown"""
        try:
            hostname = socket.gethostname()
            ip_list = socket.gethostbyname_ex(hostname)[2]
            # Include localhost loopback or filter valid local IPs
            active_ips = [ip for ip in ip_list if not ip.startswith("127.")]
            if not active_ips:
                active_ips = ["127.0.0.1"]
            
            self.interface_cb['values'] = active_ips
            self.interface_cb.current(0)
        except Exception as e:
            self.interface_cb['values'] = ["127.0.0.1"]
            self.interface_cb.current(0)

    def toggle_ip_mode(self):
        mode = self.ip_mode_var.get()
        if mode == "dhcp":
            # Clear or disable manual fields if automatic DHCP is selected
            for entry in self.form_entries.values():
                entry.config(state="disabled")
        elif mode == "static":
            for entry in self.form_entries.values():
                entry.config(state="")
        else:
            pass

    def on_interface_selected(self, event):
        # Handle interface selection logic here if needed
        pass

    def start_broadcast_scan(self):
        """Trigger UDP broadcast network packet search (matches backend listener concept)"""
        selected_ip = self.interface_cb.get()
        if not selected_ip:
            messagebox.showerror("錯誤", "請先選擇有效的網路介面 IP")
            return

        # Clear previous table items
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.search_btn.config(state="disabled", text="搜尋中 (Scanning)...")
        # Run socket broadcast in a background thread to keep GUI responsive
        threading.Thread(target=self._run_broadcast_socket, args=(selected_ip,), daemon=True).start()

    def _run_broadcast_socket(self, local_ip):
        MCTESTPORT = 4022
        IPEDITFLAG = b"PCEdit"
        packet = (IPEDITFLAG + b"\x02").ljust(51, b'\x00')
        try:
            # Create UDP socket for broadcasting
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock2.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            try:
                sock.bind((local_ip, 0))
            except Exception as bind_err:
                print(f"Warning: Could not bind to local IP {local_ip}: {bind_err}")
                
            sock.settimeout(2.0) # 2 second timeout window

            # Broadcast message package request
            broadcast_addr = '<broadcast>'
            sock.sendto(packet, (broadcast_addr, MCTESTPORT))

            # Listen for responding devices
            try:
                sock2.bind(('', MCTESTPORT))
            except Exception as bind_err:
                print(f"Warning: Could not bind sock2 to port {MCTESTPORT}: {bind_err}")
            sock2.settimeout(2.0)   
            while True:
                try:
                    data, addr = sock2.recvfrom(220)
                    # Check if response matches criteria (e.g., matching IPCAM header length or content)
                    # print (data)
                    if len(data) >= 5 and data[:5] == b"IPCam":
                        
                        # Parse sample fields based on struct structure layout
                        # Name is typically located starting at offset 47 for 18 bytes
                        try:
                            dev_name = data[32:32+18].decode('utf-8', errors='ignore').strip('\x00')
                            if not dev_name:
                                dev_name = "IP_Camera"
                        except Exception:
                            dev_name = "IP_Camera"

                        dev_ip = addr[0]
                        
                        # Insert safely into GUI tree view from main thread context using root.after
                        self.root.after(0, lambda n=dev_name, i=dev_ip, d=data: self.add_device_row(n, i, d))
                except socket.timeout:
                    break
            sock.close()
            sock2.close()
        except Exception as ex:
            self.root.after(0, lambda: messagebox.showwarning("網路通知", f"廣播查詢完畢或發生異常: {ex}"))

        # Re-enable button state
        self.root.after(0, lambda: self.search_btn.config(state="normal", text="搜尋設備 (Scan / Broadcast)"))

    def add_device_row(self, hostname, ip, raw_packet):
        for item in self.tree.get_children():
            if self.tree.item(item, "values")[1] == ip:
                return

        item_id = self.tree.insert("", "end", values=(hostname, ip))
        # Save raw packet bytes in our dictionary indexed by tree item_id
        self.device_packets[item_id] = raw_packet
        # Prevent duplicates
        # existing = [self.tree.item(item)['values'] for item in self.tree.get_children()]
        # for row in existing:
            # if row[1] == ip:
                # return
        
        # item_id = self.tree.insert("", "end", values=(hostname, ip))
        # Store raw packet data inside item tags/dictionary for form retrieval if needed
        # self.tree.item(item_id, tags=(raw_packet,))

    def on_device_select(self, event):
        # selected_items = self.tree.selection()
        # if not selected_items:
            # return
        
        # item = selected_items[0]
        # values = self.tree.item(item, "values")
        # hostname, ip = values[0], values[1]

        # Populate form entries with sample/parsed data
        # self.form_entries["ent_name"].delete(0, tk.END)
        # self.form_entries["ent_name"].insert(0, hostname)

        # self.form_entries["ent_ip"].delete(0, tk.END)
        # self.form_entries["ent_ip"].insert(0, ip)

        # self.form_entries["ent_mask"].delete(0, tk.END)
        # self.form_entries["ent_mask"].insert(0, "255.255.255.0")

        # self.form_entries["ent_gateway"].delete(0, tk.END)
        # self.form_entries["ent_gateway"].insert(0, "192.168.7.1")

        # self.form_entries["ent_dns1"].delete(0, tk.END)
        # self.form_entries["ent_dns1"].insert(0, "8.8.8.8")

        # self.form_entries["ent_dns2"].delete(0, tk.END)
        # self.form_entries["ent_dns2"].insert(0, "8.8.8.8")

        # self.form_entries["ent_port"].delete(0, tk.END)
        # self.form_entries["ent_port"].insert(0, "80")

        # self.form_entries["ent_mac"].delete(0, tk.END)
        # self.form_entries["ent_mac"].insert(0, "12:34:56:67:89:12")
        selected_items = self.tree.selection()
        if not selected_items:
            return

        item = selected_items[0]

        # Retrieve raw packet bytes safely from our dictionary
        raw_packet = self.device_packets.get(item)
        if not raw_packet or len(raw_packet) < 71:
            return

        try:
            fmt = "<5s B 4s 4s 6s 4s B 2s 4s b 18s 5s 5s b 4s 4s b b"
            unpacked = struct.unpack(fmt, raw_packet[:struct.calcsize(fmt)])

            # Extract fields
            ip_bytes       = unpacked[3]
            mac_bytes      = unpacked[4]
            netmask_bytes  = unpacked[5]
            gateway_bytes  = unpacked[8]
            name_str       = unpacked[10].decode('utf-8', errors='ignore').strip('\x00')
            port1_str      = unpacked[11].decode('utf-8', errors='ignore').strip('\x00')
            dhcp_flag      = unpacked[13] # 0: static, 1: dhcp
            dns1_bytes     = unpacked[14]
            dns2_bytes     = unpacked[15]

            # Format fields into readable strings
            ip_str = socket.inet_ntoa(ip_bytes)
            mask_str = socket.inet_ntoa(netmask_bytes)
            gw_str = socket.inet_ntoa(gateway_bytes)
            dns1_str = socket.inet_ntoa(dns1_bytes)
            dns2_str = socket.inet_ntoa(dns2_bytes)
            mac_str = ":".join(f"{b:02x}" for b in mac_bytes)

            # Populate GUI entries
            self.form_entries["ent_name"].delete(0, tk.END)
            self.form_entries["ent_name"].insert(0, name_str)

            self.form_entries["ent_ip"].delete(0, tk.END)
            self.form_entries["ent_ip"].insert(0, ip_str)

            self.form_entries["ent_mask"].delete(0, tk.END)
            self.form_entries["ent_mask"].insert(0, mask_str)

            self.form_entries["ent_gateway"].delete(0, tk.END)
            self.form_entries["ent_gateway"].insert(0, gw_str)

            self.form_entries["ent_dns1"].delete(0, tk.END)
            self.form_entries["ent_dns1"].insert(0, dns1_str)

            self.form_entries["ent_dns2"].delete(0, tk.END)
            self.form_entries["ent_dns2"].insert(0, dns2_str)

            self.form_entries["ent_port"].delete(0, tk.END)
            self.form_entries["ent_port"].insert(0, port1_str)

            self.form_entries["ent_mac"].delete(0, tk.END)
            self.form_entries["ent_mac"].insert(0, mac_str)

            if dhcp_flag == 1:
                self.ip_mode_var.set("dhcp")
            else:
                self.ip_mode_var.set("static")
            self.toggle_ip_mode()

        except Exception as e:
            print(f"Error parsing device packet structure: {e}")
    def on_modify_click(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("提示", "請先從設備列表中選擇要修改設定的目標設備！")
            return
        self.send_request(self.form_entries )
        # Read form parameters to package and push configuration back
        # target_ip = self.form_entries["ent_ip"].get()
        # mode = self.ip_mode_var.get()
        # if mode == "dhcp":
            # target_iProtoe = 1
        # else
            # target_iProtoe = 0
        # target_netmask = self.form_entries["ent_mask"].get()
        # new_name = self.form_entries["ent_name"].get()
        
        # messagebox.showinfo("成功", f"成功向設備 ({target_ip}) 發送網路參數修改指令！\n新設備名稱: {new_name}")
        
    def send_request(self, entry):
    # 1. Read values from form entries
        target_ip = self.form_entries["ent_ip"].get().strip()
        target_netmask = self.form_entries["ent_mask"].get().strip()
        target_gateway = self.form_entries.get("ent_gw", tk.Entry()).get().strip() or "0.0.0.0"
        new_name = self.form_entries["ent_name"].get().strip()
        etheraddr_str = self.form_entries["ent_mac"].get().strip()
        
        # Determine DHCP (1) or Static (0) mode
        mode = self.ip_mode_var.get()
        dhcp_flag = 1 if mode == "dhcp" else 0
        
        try:
            # 2. Convert and validate network fields
            # IP, Netmask, and Gateway packed to 4 bytes each
            ip_bytes = socket.inet_aton(target_ip)
            mask_bytes = socket.inet_aton(target_netmask)
            gw_bytes = socket.inet_aton(target_gateway)
            
            # Parse MAC address (remove separators like ':' or '-' and convert to 6 bytes)
            clean_mac = etheraddr_str.replace(":", "").replace("-", "")
            mac_bytes = bytes.fromhex(clean_mac)
            if len(mac_bytes) != 6:
                raise ValueError("MAC address must be 6 bytes.")
                
            # 3. Format Camera Name (Max 17 chars + null terminator = 18 bytes)
            name_bytes = new_name.encode('utf-8')[:17].ljust(18, b'\x00')
            
            # 4. Construct the configuration buffer matching the hardware struct protocol
            # Layout breakdown based on your specification:
            # - "PCEdit" (6 bytes)
            # - \x01 command byte (1 byte)
            # - "eth0" interface name (4 bytes)
            # - IP address (4 bytes)
            # - MAC address (6 bytes)
            # - Netmask (4 bytes)
            # - \x00 + "GW" (3 bytes marker)
            # - Gateway IP (4 bytes)
            # - Camera Name (18 bytes)
            # - Fulfill / padding bytes if needed
            # - DHCP/Static mode flag (1 byte)
            
            packet = bytearray()
            packet.extend(b"PCEdit")                # 6 bytes: Static header            
            packet.extend(b"\x01")                       # 1 byte: Change IP / config command    
            packet.extend(b"eth0")                  # 4 bytes: Interface name
            packet.extend(ip_bytes)                 # 4 bytes: Target IP
            packet.extend(mac_bytes)                # 6 bytes: Hardware MAC address
            packet.extend(mask_bytes)               # 4 bytes: Subnet Mask
            packet.extend(b"\x00" + b"GW")          # 3 bytes: Gateway marker (\x00GW)
            packet.extend(gw_bytes)                 # 4 bytes: Gateway IP
            packet.extend(b"\x01")                  # 1 byte: enable change Camera name 
            packet.extend(name_bytes)               # 18 bytes: Camera name 
            packet.extend(b"\x00" * 21)             # 21 bytes: Fulfill 21 bytes padding
            packet.extend(b"\x01")                  # 1 byte: enable DHCP byte   
            packet.append(dhcp_flag)                # 1 byte: DHCP or Static flag (0 or 1)
            # totally 74 bytes
            # 5. Send via UDP broadcast (using your socket configuration, e.g., port 4022)
            broadcast_addr = "255.255.255.255"
            MCTESTPORT = 4022
            selected_ip = self.interface_cb.get()
            # Assuming self.sock_broadcast is your initialized broadcasting socket
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind((selected_ip, 0))
                broadcast_addr = '<broadcast>'
                sock.sendto(packet, (broadcast_addr, MCTESTPORT))
                sock.close()
            except Exception as e:
                print(f"Socket initialization error: {e}")
                
            messagebox.showinfo("成功", f"成功向設備發送網路參數修改指令！\n新名稱: {new_name}\nIP: {target_ip}")

        except Exception as e:
            messagebox.showerror("錯誤", f"打包或發送設定失敗:\n{str(e)}")
            
if __name__ == "__main__":
    root = tk.Tk()
    app = IPScannerApp(root)
    root.mainloop()