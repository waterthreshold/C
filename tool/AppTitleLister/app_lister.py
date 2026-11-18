import tkinter as tk
from tkinter import messagebox
import pygetwindow as gw
import base64
import threading
import pystray
from PIL import Image
import io
import keyboard  # Global hotkey listener
import sys
import win32event
import winerror
import win32api
import time
MUTEX_NAME = "RunningAppsLister_SingleInstance_Mutex"
mutex = win32event.CreateMutex(None, False, MUTEX_NAME)
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    root = tk.Tk()
    root.withdraw()
    messagebox.showwarning("Already Running", "An instance of Running Apps Lister is already running!")
    sys.exit(0)

APPLISTER_VERSION="1.1"
DOUBLE_CLICK_THRESHOLD = 0.4  # Maximum time (in seconds) between presses for a double-click
last_press_time = 0
class AppTitleListerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Running Apps Lister & Switcher")
        self.root.geometry("550x480")
        
        # Raw icon binary data used for both Tkinter and System Tray
        self.raw_icon_data = base64.b64decode(
            b"R0lGODlhEAAQAPcfAAAAACQAAEgAAGwAAJAAALQAANgAAPwAAAAkACQkAEgkAGwkAJAkALQkANgkAPwkAABIACRIAEhIAGxIAJBIALRIANhIAPxIAABsACRsAEhsAGxsAJBsALRsANhsAPxsAACQACSQAEiQAGyQAJCQALSQANiQAPyQAAC0ACS0AEi0AGy0AJC0ALS0ANi0APy0AADYACTYAEjYAGzYAJDYALTYANjYAPzYAAD8ACT8AEj8AGz8AJD8ALT8ANj8APz8AAAAVSQAVUgAVWwAVZAAVbQAVdgAVfwAVQAkVSQkVUgkVWwkVZAkVbQkVdgkVfwkVQBIVSRIVUhIVWxIVZBIVbRIVdhIVfxIVQBsVSRsVUhsVWxsVZBsVbRsVdhsVfxsVQCQVSSQVUiQVWyQVZCQVbSQVdiQVfyQVQC0VSS0VUi0VWy0VZC0VbS0Vdi0Vfy0VQDYVSTYVUjYVWzYVZDYVbTYVdjYVfzYVQD8VST8VUj8VWz8VZD8VbT8Vdj8Vfz8VQAAqiQAqkgAqmwAqpAAqrQAqtgAqvwAqgAkqiQkqkgkqmwkqpAkqrQkqtgkqvwkqgBIqiRIqkhIqmxIqpBIqrRIqthIqvxIqgBsqiRsqkhsqmxsqpBsqrRsqthsqvxsqgCQqiSQqkiQqmyQqpCQqrSQqtiQqvyQqgC0qiS0qki0qmy0qpC0qrS0qti0qvy0qgDYqiTYqkjYqmzYqpDYqrTYqtjYqvzYqgD8qiT8qkj8qmz8qpD8qrT8qtj8qvz8qgAA/yQA/0gA/2wA/5AA/7QA/9gA//wA/wAk/yQk/0gk/2wk/5Ak/7Qk/9gk//wk/wBI/yRI/0hI/2xI/5BI/7RI/9hI//xI/wBs/yRs/0hs/2xs/5Bs/7Rs/9hs//xs/wCQ/ySQ/0iQ/2yQ/5CQ/7SQ/9iQ//yQ/wC0/yS0/0i0/2y0/5C0/7S0/9i0//y0/wDY/yTY/0jY/2zY/5DY/7TY/9jY//zY/wD8/yT8/0j8/2z8/5D8/7T8/9j8//z8/yH/C05FVFNDQVBFMi4wAwEAAAAh+QQEAAAfACwAAAAAEAAQAAAIpQBZlRJIcKDBgqRakSKYkJTDhQ0LslpIZhSrUaPITNxYik3CUaTq+fNXD+NAhQxH1fs3khW7MQ9RloI5slW9m6IWCmQzkNQokqvY9Ss5plREh2Ju1qNXj5UmnQ0ValJZr5/TMQoVtnE4ZpQWTaI0aQEpcGEpjF59jtlkdqLCUV3HZm1FkAzKLaOkjDJIkaHCLJIsQtwq0y0puwl7Zj1KN6JiiK0CAgA7"
        )
        
        try:
            self.app_icon = tk.PhotoImage(data=self.raw_icon_data)
            self.root.iconphoto(True, self.app_icon)
        except Exception as e:
            print(f"--- PARSE ERROR ---{e}")
            
        # Intercept window close button ('X') to minimize to tray instead of exiting
        self.root.protocol('WM_DELETE_WINDOW', self.hide_to_tray)
        
        # Disable both horizontal and vertical resizing (disables the maximize button)
        self.root.resizable(False, False)
        
        self.tray_icon = None

        self.all_windows = []
            
        # --- Search Input Box (Top) ---
        search_frame = tk.Frame(root, pady=5, padx=5)
        search_frame.pack(fill=tk.X)
        
        tk.Label(search_frame, text="Search:", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace("w", self.filter_apps)
        
        self.txt_search = tk.Entry(search_frame, textvariable=self.search_var, font=("Segoe UI", 10))
        self.txt_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # --- ListBox & Scrollbar (Middle) ---
        list_frame = tk.Frame(root, padx=5)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.listbox_apps = tk.Listbox(list_frame, font=("Segoe UI", 10))
        self.listbox_apps.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.listbox_apps.bind("<Double-Button-1>", self.activate_app)
        # self.listbox_apps.bind("<Return>", self.activate_app)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox_apps.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox_apps.config(yscrollcommand=scrollbar.set)

        # --- Button Frame (Bottom) ---
        button_frame = tk.Frame(root, padx=5, pady=5)
        button_frame.pack(fill=tk.X)

        self.btn_refresh = tk.Button(button_frame, text="List Running Apps", font=("Segoe UI", 10, "bold"), height=2, command=self.load_running_apps)
        self.btn_refresh.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))

        self.btn_about = tk.Button(button_frame, text="About", font=("Segoe UI", 10, "bold"), height=2, width=10, command=self.show_about_dialog)
        self.btn_about.pack(side=tk.RIGHT, padx=(3, 0))
        
        # --- Keyboard Shortcuts Binding ---
        self.root.bind("<Control-Return>", lambda event: self.load_running_apps())
        self.root.bind("<Control-f>", self.focus_search_box)
        self.root.bind("<Control-F>", self.focus_search_box)
        self.root.bind("<Control-n>", self.focus_first_list_item)
        self.root.bind("<Control-N>", self.focus_first_list_item)
        self.root.bind("<Return>", self.Process_enter_key)
        self.root.bind("<Escape>",  self.check_minimize)
        # self.root.bind("<Control-m>", self.check_minimize)
        # self.root.bind("<Control-M>", self.check_minimize)
        self.root.bind("<F1>", lambda event: self.show_about_dialog())
        
        self.root.bind("<Unmap>", self.check_minimize)
        # Register global hotkey (Ctrl + Shift + A) to summon app from tray
        # keyboard.add_hotkey('ctrl+shift+a', self.global_show_window)
        keyboard.add_hotkey('caps lock', self.on_caps_lock_press)
        # Automatically load on start
        self.load_running_apps()
        self.focus_search_box()
        
    def hide_to_tray(self):
        self.root.withdraw()
        if not self.tray_icon:
            image = Image.open(io.BytesIO(self.raw_icon_data))
            menu = pystray.Menu(
                pystray.MenuItem("Show", self.show_window),
                pystray.MenuItem("Quit", self.quit_app)
            )
            self.tray_icon = pystray.Icon("AppTitleLister", image, "Running Apps Lister", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
            
    def check_minimize(self, event):
        # 1. Ensure the event belongs to the main root window, not a child widget
        if event.widget == self.root or event.keysym == "Escape":
            # 2. Check if the current state is minimized ('iconic')
            
            self.hide_to_tray()
                
    def show_window(self, icon=None, item=None):
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None
            
        self.root.after(0, self.root.deiconify)
    
    
    def _focus_and_select(self):
        # Bring window to the front and force focus onto the text box
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.attributes('-topmost', False)  # Toggle topmost to pop it above other windows
        self.focus_search_box()
        
    def global_show_window(self):
        # Triggered safely by global hotkey thread
        self.load_running_apps()
        self.show_window()
        self.root.after(50, self._focus_and_select)
        
    def on_caps_lock_press(self):
        global last_press_time
        current_time = time.time()
        
        # Calculate elapsed time since the last press
        elapsed = current_time - last_press_time
        
        if elapsed < DOUBLE_CLICK_THRESHOLD:
            # print("Double Caps Lock detected! Launching app...")
            
            # Replace this with the command to launch your application
            # try:
                # subprocess.Popen(["python", "C:/path/to/your_script.py"])
            # except Exception as ex:
                # print(f"Failed to launch app: {ex}")
            if self.tray_icon:  
                self.global_show_window()
                
            else:
                self.hide_to_tray()
            # Reset to prevent triggering again immediately on a third tap
            last_press_time = 0
        else:
            last_press_time = current_time
        
    def quit_app(self, icon=None, item=None):
        keyboard.unhook_all() # Clean up global hotkeys
        if self.tray_icon:
            self.tray_icon.stop()
        self.root.after(0, self.root.destroy)

    def load_running_apps(self):
        self.all_windows = []
        windows = gw.getAllWindows()
        
        for win in windows:
            if win.title.strip() != "":
                self.all_windows.append(win)

        self.filter_apps()

    def filter_apps(self, *args):
        self.listbox_apps.delete(0, tk.END)
        keyword = self.search_var.get().strip().lower()

        count = 0
        for win in self.all_windows:
            if not keyword or keyword in win.title.lower():
                self.listbox_apps.insert(tk.END, win.title)
                count += 1

        self.root.title(f"Running Apps Found: {count}")
    
    def focus_search_box(self, event=None):
        self.txt_search.focus_set()
        self.txt_search.select_range(0, tk.END)
        return "break" 
    
    def focus_first_list_item(self, event=None):
        if self.root.focus_get() == self.txt_search and event.keysym == "Down":
            return
            
        self.listbox_apps.focus_set()
        if self.listbox_apps.size() > 0:
            self.listbox_apps.selection_clear(0, tk.END)
            self.listbox_apps.selection_set(0)
            self.listbox_apps.activate(0)
        return "break"
        
    def Process_enter_key(self, event=None):
        if self.root.focus_get() == self.txt_search:
            
            
            self.listbox_apps.focus_set()
            if self.listbox_apps.size() == 1:
                self.listbox_apps.selection_clear(0, tk.END)
                self.listbox_apps.selection_set(0)
                # self.listbox_apps.activate(0)
                self.activate_app(event=None)
                return "break"
            elif self.listbox_apps.size() > 0:
                self.listbox_apps.selection_clear(0, tk.END)
                self.listbox_apps.selection_set(0)
                self.listbox_apps.activate(0)
                return "break"    
            else:
                messagebox.showinfo("Warning App Lister", "Could not found any app name")
                return "break"
                
        if self.root.focus_get() == self.listbox_apps:
                self.activate_app(event=None)
                return "break"
        else:
            return
    
    def show_about_dialog(self, event=None):
        about_text = (
            "Running Apps Lister & Switcher\n"
            f"Version: v{APPLISTER_VERSION}\n\n"
            "Shortcut Keys:\n"
            "• Ctrl + F  -> Focus Search Box\n"
            "• Ctrl + Enter -> List / Refresh Running Apps\n"
            "• Ctrl + N / Down -> Focus First List Item\n"
            "• Double-Click / Enter -> Activate Selected App\n"
            "• F1 -> Open About Dialog\n"
            "• caps lock (double-click) -> Global Hotkey (Restore from Tray)\n\n"
            "Note: Closing the window minimizes it to the system tray."
        )
        messagebox.showinfo("About App Lister", about_text)
    
    def activate_app(self, event):
        try:
            selection = self.listbox_apps.curselection()
            if selection:
                index = selection[0]
                selected_title = self.listbox_apps.get(index)

                for win in self.all_windows:
                    if win.title == selected_title:
                        if win.isMinimized:
                            win.restore()
                        win.activate()
                        self.hide_to_tray()
                        break
        except Exception as e:
            messagebox.showerror("Error", f"Could not activate application: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppTitleListerApp(root)
    root.mainloop()