# attendance.py
from datetime import datetime
import json
import os
import platform


class Attendance:
    """Base class for managing attendance authentication, queries, and parsing."""

    def __init__(self, config_path=None):
        self.system_name = platform.system()

        if config_path:
            self.config_path = config_path
        else:
            if self.system_name == "Windows":
                self.config_path = "sensitivity.json"
            elif self.system_name == "Linux":
                self.config_path = "config.json"
            else:
                self.config_path = "config.json"  # 預設防呆

        self.cookies_path = os.path.join(
            os.path.dirname(os.path.abspath(self.config_path)), "cookie.txt"
        )
        self.username = ""
        self.password = ""
        self.url = ""
        self.endworktime = None
        self.startworktime =  None
        self.config = self._load_config()
        self.lastLeaveTime =None
    def _load_config(self):
        """Loads and parses the JSON configuration file."""
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                j = json.loads(f.read())
                self.url = j.get("url", "")
                self.password = j.get("password", "")
                self.username = j.get("username", "")  # 修正 slef 拼字錯誤
                return j
        except FileNotFoundError:
            print(f"Warning: Configuration file not found at '{self.config_path}'.")
            return {}
        except json.JSONDecodeError:
            print(f"Error: Failed to parse JSON from '{self.config_path}'.")
            return {}

    def _get_token(self):
        if os.path.exists(self.cookies_path):
            with open(self.cookies_path, "r", encoding="utf-8") as f:
                return f.readline().strip()
        return ""

    def _save_token(self, token):
        with open(self.cookies_path, "w", encoding="utf-8") as f:
            f.write(token)
    
    def _set_lastLeaveTime(self, strp,formatp="%H:%M"):
        self.lastLeaveTime = datetime.strptime(strp,formatp)
        
    def _set_endworktime(self, strp,formatp="%H:%M"):     
        self.endworktime = datetime.strptime(strp,formatp)
        
    def _set_startworktime(self, strp,formatp="%H:%M"):
        self.startworktime = datetime.strptime(strp,formatp)
        
    def _get_countdown_time(self):
        if not self.endworktime:
            print("End work time is not set.")
            return 0
        curr = datetime.now()
        difference = self.endworktime - curr
        seconds = difference.total_seconds()
        # print("Difference in seconds is:", seconds)
        return seconds