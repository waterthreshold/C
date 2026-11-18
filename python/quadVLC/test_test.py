#!/usr/bin/env python3
"""
Quad VLC RTSP Player (Python + Tkinter + python-vlc)

- 2x2 layout (four panels)
- Supports RTSP over TCP (low-latency)
- Accepts IP addresses from CLI (IP only)
- Respects ffplay low-latency flags
"""

import sys, os
import tkinter as tk
import argparse
# import vlc
import time
from tkinter import messagebox
import configparser

# import ctypes
win_id = None
def build_rtsp_urls(ip, stream_num, template="rtsp://{ip}/stream{ch}"):
    urls = [template.format(ip=ip,ch=ch) for ch in range (1, stream_num + 1)]
    while len(urls) < 4:
        urls.append("about:blank")  # fill empty panels
    return urls[:4]

class VLCPanel:
    def __init__(self, parent, vlc_instance, mrl):
        self.mrl = mrl
        self.frame = tk.Frame(parent, bg="black")
        self.instance = vlc_instance
        self.player = self.instance.media_player_new()
        self.overlay = tk.Label(self.frame, text="", bg="black", fg="white", anchor="nw", justify="left")
        self.overlay.place(relx=0.01, rely=0.01)
        self.button_frame = tk.Frame(self.frame, bg="gray")
        self.button_frame.pack(side="bottom", fill="x")
        self.start_btn = tk.Button(self.button_frame, text="Start", command=self.play)
        self.stop_btn = tk.Button(self.button_frame, text="Stop", command=self.stop)
        self.start_btn.pack(side="left", expand=True, fill="x")
        self.stop_btn.pack(side="right", expand=True, fill="x")

        global win_id
        self.player.set_hwnd(win_id)
        # Hide buttons initially
        #self.button_frame.pack_forget()

        self.frame.bind("<Motion>", self.check_mouse_position)
        self.frame.bind("<Double-Button-1>", self.on_toggle_fullscreen)
        
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
        
        
    def set_window_handle(self):
        handle = self.frame.winfo_id()
        if sys.platform.startswith("win"):
            self.player.set_hwnd(handle)
        elif sys.platform.startswith("linux"):
            self.player.set_xwindow(handle)
        elif sys.platform == "darwin":
            self.player.set_nsobject(handle)
            
    def check_mouse_position(self,event):
        y = event.y 
        height = self.frame.winfo_height()
        if event.y > height - 50:   # 50px from bottom
            # print('show')
            self.show_buttons()
        else:
            # print('hide')
            self.hide_buttons()
            
    def show_buttons(self):
        self.button_frame.pack(side="bottom", fill="x")

    def hide_buttons(self):
        self.button_frame.pack_forget()

    def play(self, tcp=True, caching=1000):
        options = []
        if tcp:
            options.append("--rtsp-tcp")
        options.append(f"--network-caching={caching}")
        media = self.instance.media_new(self.mrl, *options)
        self.player.set_media(media)
        self.player.play()
    
    def stop(self):
        self.player.stop()
        
    def release(self):
        self.player.release()
    
    def on_toggle_fullscreen(self,event):
        if self.player.get_fullscreen() == False:
            print('Enable FullScreen')
            # parent.attributes("-fullscreen", True)
            self.player.set_fullscreen(True)
        else:
            print('Disable FullScreen')
            # parent.attributes("-fullscreen", False)
            self.player.set_fullscreen(False)
            
class QuadVLCApp(tk.Tk):
    def __init__(self, urls, caching=1000, tcp=True):
        super().__init__()
        self.title("Larnaca2 Quad VLC RTSP Player")
        self.geometry("1280x720")
        # small_icon = tk.PhotoImage(file="icon-16.png")
        # large_icon = tk.PhotoImage(file="icon-32.png")
        # self.iconphoto(True, large_icon, small_icon)
        # self.iconbitmap('icon.ico')  
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        # self.attributes("-fullscreen", True)
        global win_id
        win_id = self.winfo_id()
        print (win_id)
        # Grid 2x2
        for r in range(2):
            self.rowconfigure(r, weight=1)
        for c in range(2):
            self.columnconfigure(c, weight=1)

        self.instance = vlc.Instance()
        self.panels = []
        for i in range(4):
            frame = tk.Frame(self, bd=1, relief=tk.SUNKEN)
            frame.grid(row=i//2, column=i%2, sticky="nsew", padx=2, pady=2)
            panel = VLCPanel(frame, self.instance, urls[i])
            panel.frame.pack(fill="both", expand=True)
            self.panels.append(panel)

        # Delay to ensure window IDs exist
        self.after(150, self._init_players, tcp, caching)

        # Monitor loop to restart dead streams
        self._monitoring = True
        self.after(1500, self._monitor_loop, tcp, caching)

    def _init_players(self, tcp, caching):
        self.update_idletasks()
        for p in self.panels:
            p.set_window_handle()
            p.play(tcp=tcp, caching=caching)

    def _monitor_loop(self, tcp, caching):
        for p in self.panels:
            state = p.player.get_state()
            if state in (vlc.State.Ended, vlc.State.Error, vlc.State.Stopped):
                if p.mrl != "about:blank":
                    p.stop()
                    p.play(tcp=tcp, caching=caching)
        if self._monitoring:
            self.after(1500, self._monitor_loop, tcp, caching)

    def on_close(self):
        self._monitoring = False
        for p in self.panels:
            p.stop()
            p.release()
        try:
            self.instance.release()
        except Exception:
            pass
        self.destroy()

def parse_args(argv):
    parser = argparse.ArgumentParser(description="Larnaca2 Quad RTSP Player")
    parser.add_argument("ip", nargs="*", help="IP addresses (positional)")
    parser.add_argument("--template", type=str, default="rtsp://{ip}/stream{ch}", help="RTSP template with {ip}")
    parser.add_argument("--caching", type=int, default=1000, help="network-caching in ms")
    parser.add_argument("--no-tcp", action="store_true", help="disable RTSP TCP")
    parser.add_argument("--stream", type=int, default=4, help="Total RTSP stream channel")
    return parser.parse_args(argv)

def main(argv=None):
    args = parse_args(argv or sys.argv[1:])
    # if not args.ips:
        # print("Provide at least one IP address, e.g.:")
        # print("  python quad_vlc_player.py 192.168.100.20 192.168.100.21")
        # sys.exit(1)
    
    urls = build_rtsp_urls(args.ip[0], args.stream, args.template)
    
    print (urls)
    app = QuadVLCApp(urls, caching=args.caching, tcp=(not args.no_tcp))
    app.mainloop()

if __name__ == "__main__":
    if not os.path.exists('config.ini'):
        messagebox.showwarning("Error", "Cannot not find the config.ini configuration file")
        os.exit()
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    vlc_lib_path = r"{}".format(config['VLC']['path'])  # adjust your install path
    print (vlc_lib_path)
    os.environ["PATH"] = vlc_lib_path + ";" + os.environ["PATH"]
    import vlc
    args = [] 
    ip = config ['DUT']['host']
    caching = config ['VLC']['caching']
    template = "rtsp://{}/{}".format(ip,config ['DUT']['rtsp_path'])
    stream = config ['DUT']['stream']
    args.append("--stream") 
    args.append(stream)
    # args.append("--caching")
    # args.append(caching)
    args.append("--template")
    args.append(template)
    args.append(ip)
    main(args)