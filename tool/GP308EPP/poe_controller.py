import json
import hashlib
import os
import requests
import tkinter as tk
from tkinter import messagebox
from bs4 import BeautifulSoup

# --- MOCK HTML RESPONSE (Simulating what http://<ip>/getPoePortStatus.cgi returns) ---
# In your real code, replace this with: requests.get("http://<ip>/getPoePortStatus.cgi").text
SAMPLE_CGI_HTML = """
<div id="poe_port_status_details" class="box_flex">
<ul class="list_css">
<li class="poe_port_list_item poePortStatusListItem index_li">
<div name="isShowPot1" class="poe_li_header_content">
<span class="pull-right poe-power-mode"><span>Searching</span></span>
<span class="pull-right poe-portPwr-width"><span class="powClassShow">Unknown</span></span>
<span class="poe_index_li_title poe-port-index">
<input type="hidden" class="port" value="1">
<span>1 - VOIP-Bridge</span></span></div>
<div class="poe_port_status">
<div class="hid_info_cell">Output Voltage (V): <span>0</span></div>
<div class="hid_info_cell">Output Current (mA): <span>0</span></div>
<div class="hid_info_cell">Output Power (W): <span>0.0</span></div>
<div class="hid_info_cell">Temperature (C): <span>39</span></div>
<div class="hid_info_cell">Fault Status: <span>No Error</span></div>
</div>
</li>
<li class="poe_port_list_item poePortStatusListItem index_li">
<div name="isShowPot2" class="poe_li_header_content">
<span class="pull-right poe-power-mode"><span>Searching</span></span>
<span class="pull-right poe-portPwr-width"><span class="powClassShow">Unknown</span></span>
<span class="poe_index_li_title poe-port-index">
<input type="hidden" class="port" value="2">
<span>2 - DHCP-Router</span></span></div>
<div class="poe_port_status">
<div class="hid_info_cell">Output Voltage (V): <span>0</span></div>
<div class="hid_info_cell">Output Current (mA): <span>0</span></div>
<div class="hid_info_cell">Output Power (W): <span>0.0</span></div>
<div class="hid_info_cell">Temperature (C): <span>37</span></div>
<div class="hid_info_cell">Fault Status: <span>No Error</span></div>
</div>
</li>
<li class="poe_port_list_item poePortStatusListItem index_li">
<div name="isShowPot3" class="poe_li_header_content">
<span class="pull-right poe-power-mode"><span>Searching</span></span>
<span class="pull-right poe-portPwr-width"><span class="powClassShow">Unknown</span></span>
<span class="poe_index_li_title poe-port-index">
<input type="hidden" class="port" value="3">
<span>3 - POE1</span></span></div>
<div class="poe_port_status">
<div class="hid_info_cell">Output Voltage (V): <span>0</span></div>
<div class="hid_info_cell">Output Current (mA): <span>0</span></div>
<div class="hid_info_cell">Output Power (W): <span>0.0</span></div>
<div class="hid_info_cell">Temperature (C): <span>38</span></div>
<div class="hid_info_cell">Fault Status: <span>No Error</span></div>
</div>
</li>
<li class="poe_port_list_item poePortStatusListItem index_li">
<div name="isShowPot4" class="poe_li_header_content">
<span class="pull-right poe-power-mode"><span>Searching</span></span>
<span class="pull-right poe-portPwr-width"><span class="powClassShow">Unknown</span></span>
<span class="poe_index_li_title poe-port-index">
<input type="hidden" class="port" value="4">
<span>4 - POE2</span></span></div>
<div class="poe_port_status">
<div class="hid_info_cell">Output Voltage (V): <span>0</span></div>
<div class="hid_info_cell">Output Current (mA): <span>0</span></div>
<div class="hid_info_cell">Output Power (W): <span>0.0</span></div>
<div class="hid_info_cell">Temperature (C): <span>37</span></div>
<div class="hid_info_cell">Fault Status: <span>No Error</span></div>
</div>
</li>
<li class="poe_port_list_item poePortStatusListItem index_li">
<div name="isShowPot5" class="poe_li_header_content">
<span class="pull-right poe-power-mode"><span>Searching</span></span>
<span class="pull-right poe-portPwr-width"><span class="powClassShow">Unknown</span></span>
<span class="poe_index_li_title poe-port-index">
<input type="hidden" class="port" value="5">
<span>5 - POE3</span></span></div>
<div class="poe_port_status">
<div class="hid_info_cell">Output Voltage (V): <span>0</span></div>
<div class="hid_info_cell">Output Current (mA): <span>0</span></div>
<div class="hid_info_cell">Output Power (W): <span>0.0</span></div>
<div class="hid_info_cell">Temperature (C): <span>38</span></div>
<div class="hid_info_cell">Fault Status: <span>No Error</span></div>
</div>
</li>
<li class="poe_port_list_item poePortStatusListItem index_li">
<div name="isShowPot6" class="poe_li_header_content">
<span class="pull-right poe-power-mode"><span>Searching</span></span>
<span class="pull-right poe-portPwr-width"><span class="powClassShow">Unknown</span></span>
<span class="poe_index_li_title poe-port-index">
<input type="hidden" class="port" value="6">
<span>6 - POE4</span></span></div>
<div class="poe_port_status">
<div class="hid_info_cell">Output Voltage (V): <span>0</span></div>
<div class="hid_info_cell">Output Current (mA): <span>0</span></div>
<div class="hid_info_cell">Output Power (W): <span>0.0</span></div>
<div class="hid_info_cell">Temperature (C): <span>37</span></div>
<div class="hid_info_cell">Fault Status: <span>No Error</span></div>
</div>
</li>
<li class="poe_port_list_item poePortStatusListItem index_li">
<div name="isShowPot7" class="poe_li_header_content">
<span class="pull-right poe-power-mode"><span>Searching</span></span>
<span class="pull-right poe-portPwr-width"><span class="powClassShow">Unknown</span></span>
<span class="poe_index_li_title poe-port-index">
<input type="hidden" class="port" value="7">
<span>7 - POE5</span></span></div>
<div class="poe_port_status">
<div class="hid_info_cell">Output Voltage (V): <span>0</span></div>
<div class="hid_info_cell">Output Current (mA): <span>0</span></div>
<div class="hid_info_cell">Output Power (W): <span>0.0</span></div>
<div class="hid_info_cell">Temperature (C): <span>37</span></div>
<div class="hid_info_cell">Fault Status: <span>No Error</span></div>
</div>
</li>
<li class="poe_port_list_item poePortStatusListItem index_li">
<div name="isShowPot8" class="poe_li_header_content">
<span class="pull-right poe-power-mode"><span>Delivering Power</span></span>
<span class="pull-right poe-portPwr-width"><span class="powClassShow">Class2</span></span>
<span class="poe_index_li_title poe-port-index">
<input type="hidden" class="port" value="8">
<span>8 - VOIP</span></span></div>
<div class="poe_port_status">
<div class="hid_info_cell">Output Voltage (V): <span>53</span></div>
<div class="hid_info_cell">Output Current (mA): <span>60</span></div>
<div class="hid_info_cell">Output Power (W): <span>3.2</span></div>
<div class="hid_info_cell">Temperature (C): <span>38</span></div>
<div class="hid_info_cell">Fault Status: <span>No Error</span></div>
</div>
</li>
</ul>
</div>
"""
# POE_IP=192.168.7.200
# POE_PASSWORD=Password123
# COOKIES=
# HASH=

class PoEswitchRequest:
    def __init__(self, config_path="config.json"):
        self.ip = "192.168.137.2"       # Default fallback
        self.password = "12345678"     # Default fallback
        self.cookies = ""
        self.hashval = ""
        
        # Load configuration on init
        self.config(config_path)

    def config(self, config_path="config.json"):
        """Parses config.json for IP and password, then fetches auth tokens."""
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    cfg = json.load(f)
                    self.ip = cfg.get("ip", self.ip)
                    self.password = cfg.get("password", self.password)
                    print(f"Loaded configuration from {config_path} for IP: {self.ip}")
            except Exception as e:
                print(f"Error reading {config_path}: {e}. Using defaults.")
        else:
            # Create a sample config file if it doesn't exist yet
            sample_cfg = {"ip": self.ip, "password": self.password}
            with open(config_path, "w") as f:
                json.dump(sample_cfg, f, indent=4)
            print(f"Created template {config_path}. Please update credentials if needed.")

        # Automatically execute authentication sequence
        self.cookies = self.get_cookie()
        if self.cookies:
            self.hashval = self.get_hashval()
            print(f"Authentication successful! Hash: {self.hashval}")
        else:
            print("Authentication failed: Could not retrieve session cookies.")

    def get_cookie(self):
        """Translates the bash login/merge/md5 script into Python requests."""
        login_url = f"http://{self.ip}/login.cgi"
        
        try:
            # 1. Fetch the login page to extract the random dynamic salt ('rand')
            resp = requests.get(login_url, timeout=3)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            rand_input = soup.find('input', id='rand')
            if not rand_input:
                # Fallback regex extraction if input tag varies slightly
                import re
                match = re.search(r"id=['\"]rand['\"].*?value=['\"]([0-9]+)['\"]", resp.text)
                rand_num = match.group(1) if match else ""
            else:
                rand_num = rand_input.get('value', '')

            if not rand_num:
                print("Error: Could not find 'rand' token on login page.")
                return ""

            # 2. Implement the bash 'merge' function logic (interleave password chars with rand_num chars)
            pwd = self.password
            merged_str = ""
            max_len = max(len(pwd), len(rand_num))
            for i in range(max_len):
                if i < len(pwd):
                    merged_str += pwd[i]
                if i < len(rand_num):
                    merged_str += rand_num[i]

            # 3. Compute MD5 checksum of the merged string
            passwd_md5 = hashlib.md5(merged_str.encode('utf-8')).hexdigest()

            # 4. POST the md5 password to login.cgi and extract Set-Cookie header
            post_resp = requests.post(login_url, data={"password": passwd_md5}, allow_redirects=False, timeout=3)
            
            # Extract session cookie (e.g., sessionid=xyz)
            set_cookie_header = post_resp.headers.get("Set-Cookie", "")
            if set_cookie_header:
                # Split by semicolon to grab the primary cookie directive
                cookie_token = set_cookie_header.split(";")[0].strip()
                return cookie_token

        except Exception as e:
            print(f"Exception during cookie generation: {e}")
            
        return ""

    def get_hashval(self):
        """Translates the bash curl/sed script to fetch the page security hash token."""
        config_url = f"http://{self.ip}/PoEPortConfig.cgi"
        headers = {"Cookie": self.cookies}
        
        try:
            resp = requests.get(config_url, headers=headers, timeout=3)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # Look for input or hidden field with id='hash'
            hash_input = soup.find('input', id='hash')
            if hash_input:
                return hash_input.get('value', '')
            
            # Fallback regex search if formatted differently in HTML script block
            import re
            match = re.search(r"id=['\"]hash['\"].*?value=['\"]([0-9a-z]+)['\"]", resp.text, re.IGNORECASE)
            if match:
                return match.group(1)
                
        except Exception as e:
            print(f"Exception during hash retrieval: {e}")
            
        return ""

    def get_status(self):
        """Fetches live PoE port status using the established cookies."""
        status_url = f"http://{self.ip}/getPoePortStatus.cgi"
        headers = {"Cookie": self.cookies}
        
        try:
            resp = requests.get(status_url, headers=headers, timeout=3)
            if resp.status_code == 200:
                # print(resp.text)
                return resp.text
            else:
                print(f"Failed to fetch status. HTTP Status Code: {resp.status_code}")
        except Exception as e:
            print(f"Error fetching PoE status: {e}")
            
        return None
        
    def set_port_status(self, port_id, admin_mode):
        """Translates your curl POST command to control port state (1=ON, 0=OFF)."""
        config_url = f"http://{self.ip}/PoEPortConfig.cgi"
        headers = {"Cookie": self.cookies}
        payload = {
            "hash": self.hashval,
            "ACTION": "Apply",
            "portID": port_id,
            "ADMIN_MODE": str(admin_mode)
        }
        try:
            resp = requests.post(config_url, headers=headers, data=payload, timeout=3)
            return resp.status_code == 200
        except Exception as e:
            print(f"Error updating port {port_id}: {e}")
            return False
            
    def logout(self):
        """Sends a logout request to terminate the session on the switch cleanly."""
        if not self.cookies:
            return
            
        logout_url = f"http://{self.ip}/logout.cgi" # Or whatever your switch's logout endpoint is
        headers = {"Cookie": self.cookies}
        try:
            # Send logout request with a short timeout so it doesn't hang the closing window
            requests.post(logout_url, headers=headers, timeout=1)
            print("Successfully logged out from PoE switch.")
        except Exception:
            # Fail silently on exit if switch is already unreachable
            pass        
            
class PoESwitchDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("PoE Switch Dynamic Port Controller")
        self.root.geometry("1000x650")
        self.root.config(bg="#1e1e1e")
        self.client = PoEswitchRequest()
        self.timer_id = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Header Title
        title_lbl = tk.Label(root, text="PoE Switch Live Port Status", 
                             fg="#ffffff", bg="#1e1e1e", font=("Arial", 14, "bold"))
        title_lbl.pack(pady=10)

        # Main Scrollable Frame Container for Ports
        self.create_port_grid_area()

        # Fetch & Parse Button
            # refresh_btn = tk.Button(root, text="REFRESH STATUS FROM CGI", bg="#007acc", fg="white",
                                    # font=("Arial", 10, "bold"), command=self.load_and_parse_data)
            # refresh_btn.pack(pady=10)

        # Initial load using sample HTML
        # self.parse_html_and_render(SAMPLE_CGI_HTML)
        self.poll_switch_data() 
    def on_closing(self):
        """Triggered explicitly when the user closes the Tkinter window."""
        print("Closing application, executing logout...")
        self.client.logout()   # Run your logout/cleanup code
        self.root.destroy()
        print("close")
        
    def poll_switch_data(self):
        """Fetches live data from switch CGI and updates UI, then schedules next run in 10s."""
        # 1. Fetch HTML from switch (or handle if offline/testing)
        
            
        html_content = self.client.get_status()
        
        if html_content:
            self.parse_html_and_render(html_content)
        else:
            print("Warning: Could not fetch live data from switch. Retrying in 10s...")

        # 2. Schedule this function to run again in exactly 10,000 milliseconds (10 seconds)
        self.timer_id= self.root.after(10000, self.poll_switch_data)
        
    def create_port_grid_area(self):
        # Frame holding all dynamic port cards
        self.container_frame = tk.Frame(self.root, bg="#2d2d2d", bd=2, relief="groove")
        self.container_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    def parse_html_and_render(self, html_content):
        # Clear existing cards if refreshing
        for widget in self.container_frame.winfo_children():
            widget.destroy()

        # --- BEAUTIFULSOUP PARSING LOGIC ---
        soup = BeautifulSoup(html_content, 'html.parser')
        details_div = soup.find('div', id='poe_port_status_details')

        # Safety check: If container is missing, stop here to avoid NameError
        if not details_div:
            messagebox.showerror("Parsing Error", "Could not find 'poe_port_status_details' in HTML response.")
            return

        # Find all port list items dynamically
        port_items = details_div.find_all('li', class_='poe_port_list_item')
        
        if not port_items:
            messagebox.showwarning("Warning", "Found the container, but no port items inside!")
            return

        total_ports = len(port_items)
        self.root.title(f"PoE Switch Port Controller - Total Ports Detected: {total_ports}")

        max_columns = 4

        # Now this loop is 100% safe because port_items is guaranteed to exist
        for index, item in enumerate(port_items):
            port_input = item.find('input', class_='port')
            port_id = port_input['value'] if port_input else str(index + 1)
            
            port_title_elem = item.find('span', class_='poe-port-index')
            port_name = port_title_elem.get_text(strip=True) if port_title_elem else f"Port {port_id}"

            power_mode_elem = item.find('span', class_='poe-power-mode')
            power_mode = power_mode_elem.get_text(strip=True) if power_mode_elem else "Unknown"

            pow_class_elem = item.find('span', class_='powClassShow')
            pow_class_text = pow_class_elem.get_text(strip=True) if pow_class_elem else "Unknown"
            if pow_class_text  != "Unknown":
                pow_class = pow_class_text.split("@")[1]
                # print(pow_class)
            else:
                pow_class = pow_class_text
            text_block = item.get_text()
            voltage = self.extract_metric(text_block, "ml570")
            current = self.extract_metric(text_block, "ml572")
            power = self.extract_metric(text_block, "ml574")
            temp = self.extract_metric(text_block, "ml575")
            fault = self.extract_metric(text_block, "ml581")
            
            
            row = index // max_columns
            col = index % max_columns
            
            card = tk.Frame(self.container_frame, bg="#ffffff", bd=2, relief="ridge", width=220, height=180)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            card.pack_propagate(False)

            header_bg = "#2ecc71" if "Delivering" in power_mode else "#e67e22"
            hdr_lbl = tk.Label(card, text=port_name, bg=header_bg, fg="white", font=("Arial", 9, "bold"))
            hdr_lbl.pack(fill=tk.X, pady=(0, 5))

            info_str = (
                f"Mode: {power_mode}\n"
                f"Class: {pow_class}\n"
                f"Volt: {voltage}V | Curr: {current}mA\n"
                f"Power: {power}W | Temp: {temp}°C\n"
                f"Fault: {fault}"
            )
            info_lbl = tk.Label(card, text=info_str, bg="#f9f9f9", fg="#333333", 
                                font=("Consolas", 8), justify="left", anchor="w")
            info_lbl.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)

            btn_text = "Turn OFF" if "Delivering" in power_mode else "Turn ON"
            btn_bg = "#e74c3c" if "Delivering" in power_mode else "#2ecc71"
            port_id_num = int(port_id) - 1
            btn = tk.Button(card, text=btn_text, font=("Arial", 8, "bold"),bg=btn_bg, fg="white",
                            command=lambda pid=str(port_id_num) , mode=power_mode: self.handle_port_toggle(pid, mode))
            btn.pack(fill=tk.X, padx=5, pady=5)
            
    def handle_port_toggle(self, port_id, current_power_mode):
        """Sends the appropriate ADMIN_MODE command and immediately forces a status refresh."""
        # If currently delivering power, toggle off (0); otherwise toggle on (1)
        target_mode = "0" if "Delivering" in current_power_mode else "1"
        response = messagebox.askyesno("Confirmation", "Are you sure you want to do this?")
        if not response:
            return
            
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None  # Reset the variable
            print("Timer has been stopped!")
        print(f"Sending request to switch Port {port_id} -> ADMIN_MODE={target_mode}")
        success = self.client.set_port_status(port_id, target_mode)
        
        if success:
            # Immediately pull new status so UI reflects change without waiting 10s
            self.poll_switch_data()
        else:
            messagebox.showerror("Command Failed", f"Could not change state for Port {port_id}")
            
    def extract_metric(self, full_text, label_name):
        """Helper to pull numeric data points out of the HTML text block safely."""
        try:
            if label_name in full_text:
                parts = full_text.split(label_name)
                # Grab numbers immediately following the label text
                sub = parts[1].strip()
                return sub.split()[0]
        except Exception:
            pass
        return "0"

    def load_and_parse_data(self):
        """Placeholder function where you would execute requests.get('http://<ip>/getPoePortStatus.cgi')"""
        # Example live integration code:
        # try:
        #     response = requests.get("http://192.168.1.100/getPoePortStatus.cgi", timeout=3)
        #     self.parse_html_and_render(response.text)
        # except Exception as e:
        #     messagebox.showerror("Connection Error", f"Failed to fetch CGI: {e}")
        
        # For demonstration, we reload the sample data successfully:
        self.parse_html_and_render(SAMPLE_CGI_HTML)
        messagebox.showinfo("Success", "Successfully re-parsed CGI HTML layout!")

if __name__ == "__main__":
    # poe = PoEswitchRequest()
    # SAMPLE_CGI_HTML = poe.get_status()
    # print(SAMPLE_CGI_HTML)
    root = tk.Tk()
    root.iconbitmap("icon.ico")
    app = PoESwitchDashboard(root)
    root.mainloop()