#!/usr/bin/env python3
"""
Fullscreen Tkinter slideshow (kiosk style).

Features:
 - Start fullscreen (F11 to toggle)
 - Borderless / always-on-top
 - Auto-hide mouse cursor (shows on movement)
 - Keyboard controls: Right/Left/Space/O/Esc/Up/Down/F11/D
 - Small overlay control bar toggle (D)
 - Images scale to screen keeping aspect ratio
 - Supports PNG/JPG/GIF/BMP/WEBP
"""

import os
import glob
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from datetime import datetime

IMAGE_EXTS = ("*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.webp")

class FullScreenSlideShow(tk.Tk):
    def __init__(self, start_fullscreen=True):
        super().__init__()
        self.title("Fullscreen Slideshow")
        self.configure(bg="black")

        # state
        folder=self.getNewsClipPath()
        print (folder)
        paths = []
        for ext in IMAGE_EXTS:
            paths.extend(glob.glob(os.path.join(folder, ext)))
        # print (paths)
        paths.sort()
        self.image_paths = paths
        
        if not paths:
            messagebox.showinfo("No images", "No supported images found in the selected folder.")
            return
        self.image_paths = paths
        self.index = 0
        self.interval_ms = 3000
        self._after_id = None
        self.current_photo = None
        self.fullscreen = start_fullscreen
        self.overlay_visible = False
        self.cursor_hidden = False
        self._hide_cursor_after_ms = 1500
        self._hide_after_id = None
        self.last_mouse_move = time.time()

        # window flags
        self.attributes("-topmost", True)  # stay on top
        # self.overrideredirect(False)  # allow F11/escape to work reliably
        self._apply_fullscreen()

        # UI
        self.canvas = tk.Canvas(self, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas_image_id = None

        # small overlay controls (hidden by default)
        self._build_overlay_controls()

        # status label (hidden by default, overlay)
        self.status_var = tk.StringVar(value="No images loaded")
        self.status_label = tk.Label(self, textvariable=self.status_var, bg="#000000", fg="white", padx=8, pady=4)
        # place later when needed

        # bindings
        self.bind_keys()
        self.bind("<Configure>", self._on_resize)
        self.bind("<Motion>", self._on_mouse_move)
        self.bind("<Button>", lambda e: self.show_overlay(4000))  # show overlay on click

        # start cursor hide timer
        self._schedule_cursor_hide()
        self.index = 0
        self.show_image()
        self.update_status()
        self.show_overlay(3000)
        self.start_play()
    def _apply_fullscreen(self):
        # Use attributes depending on platform; use wm_attributes("-fullscreen", True) for true fullscreen
        try:
            self.attributes("-fullscreen", self.fullscreen)
        except Exception:
            self.geometry("{0}x{1}+0+0".format(self.winfo_screenwidth(), self.winfo_screenheight()))
        # on some platforms, also remove decorations if fullscreen
        # if self.fullscreen:
            # try:
                # self.overrideredirect(True)
            # except Exception:
                # pass
        # else:
            # try:
                # self.overrideredirect(False)
            # except Exception:
                # pass

    def _build_overlay_controls(self):
        # floating small control frame (appears near bottom center)
        self.overlay = tk.Frame(self, bg="#000000")
        btn_prev = tk.Button(self.overlay, text="◀ Prev", command=self.prev_image)
        btn_play = tk.Button(self.overlay, text="Play/Pause", command=self.toggle_play)
        btn_next = tk.Button(self.overlay, text="Next ▶", command=self.next_image)
        btn_open = tk.Button(self.overlay, text="Open (O)", command=self.open_folder)
        btn_prev.pack(side="left", padx=6, pady=6)
        btn_play.pack(side="left", padx=6, pady=6)
        btn_next.pack(side="left", padx=6, pady=6)
        btn_open.pack(side="left", padx=6, pady=6)

    def bind_keys(self):
        self.bind("<Right>", lambda e: self.next_image())
        self.bind("<Left>", lambda e: self.prev_image())
        self.bind("<space>", lambda e: self.toggle_play())
        self.bind("o", lambda e: self.open_folder())
        self.bind("O", lambda e: self.open_folder())
        self.bind("<Escape>", lambda e: self.quit())
        self.bind("<Up>", lambda e: self.change_interval(-500))
        self.bind("<Down>", lambda e: self.change_interval(500))
        self.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.bind("d", lambda e: self.toggle_overlay())
        self.bind("D", lambda e: self.toggle_overlay())
    
    def getNewsClipPath(self):
        now = datetime.now()
        path=r"\\172.16.199.85\新聞剪報\\" + now.strftime("%Y%m%d")
        return path
        
    def open_folder(self):
        folder = filedialog.askdirectory(title="Select folder with images")
        if not folder:
            return
        paths = []
        for ext in IMAGE_EXTS:
            paths.extend(glob.glob(os.path.join(folder, ext)))
        print (paths)
        paths.sort()
        if not paths:
            messagebox.showinfo("No images", "No supported images found in the selected folder.")
            return
        self.image_paths = paths
        self.index = 0
        self.show_image()
        self.update_status()
        self.show_overlay(3000)

    def update_status(self):
        if not self.image_paths:
            self.status_var.set("No images loaded")
        else:
            p = self.image_paths[self.index]
            self.status_var.set(f"{self.index+1}/{len(self.image_paths)} — {os.path.basename(p)}")

    
    def _load_image(self, path, target_w, target_h):
        try:
            img = Image.open(path)
        except Exception:
            return None
        # use first frame for animated images
        try:
            img.seek(0)
        except Exception:
            pass
        iw, ih = img.size
        if iw == 0 or ih == 0:
            return None
        # scale to fit inside target while preserving aspect ratio
        scale = min(max(1e-6, target_w / iw), max(1e-6, target_h / ih))
        new_w = max(1, int(iw * scale))
        new_h = max(1, int(ih * scale))
        img = img.resize((new_w, new_h), Image.LANCZOS)
        return ImageTk.PhotoImage(img)

    def show_image(self):
        if not self.image_paths:
            self.canvas.delete("all")
            return
        path = self.image_paths[self.index]
        c_w = max(10, self.canvas.winfo_width())
        c_h = max(10, self.canvas.winfo_height())
        photo = self._load_image(path, c_w, c_h)
        if photo is None:
            return
        self.current_photo = photo
        self.canvas.delete("all")
        x = (c_w - photo.width()) // 2
        y = (c_h - photo.height()) // 2
        self.canvas.create_rectangle(0, 0, c_w, c_h, fill="black", outline="")
        self.canvas.create_image(x, y, anchor="nw", image=photo)
        self.update_status()

    def next_image(self):
        if not self.image_paths:
            return
        self.index = (self.index + 1) % len(self.image_paths)
        self.show_image()

    def prev_image(self):
        if not self.image_paths:
            return
        self.index = (self.index - 1) % len(self.image_paths)
        self.show_image()

    def toggle_play(self):
        if self.playing:
            self.stop_play()
        else:
            self.start_play()

    def start_play(self):
        if not self.image_paths:
            return
        self.playing = True
        self._schedule_next()

    def _schedule_next(self):
        if self._after_id:
            self.after_cancel(self._after_id)
        self._after_id = self.after(self.interval_ms, self._play_step)

    def _play_step(self):
        self._after_id = None
        if not self.playing:
            return
        self.next_image()
        self._schedule_next()

    def stop_play(self):
        self.playing = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None

    def change_interval(self, delta_ms):
        new = max(200, self.interval_ms + delta_ms)
        self.interval_ms = new
        self.show_overlay(1500)
        # if playing, reschedule
        if self.playing:
            self._schedule_next()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self._apply_fullscreen()
        self.show_overlay(1000)

    def toggle_overlay(self):
        if self.overlay_visible:
            self.hide_overlay()
        else:
            self.show_overlay(4000)

    def show_overlay(self, ms=4000):
        # position overlay near bottom center
        if not self.overlay_visible:
            w = self.winfo_width()
            h = self.winfo_height()
            # place overlay centered horizontally, 50 px above bottom
            self.overlay.place(x=max(10, w//2 - 200), y=max(10, h - 80))
            # place status
            self.status_label.place(x=10, y=10)
            self.overlay_visible = True
        # schedule hide
        if ms > 0:
            if hasattr(self, "_overlay_hide_id") and self._overlay_hide_id:
                self.after_cancel(self._overlay_hide_id)
            self._overlay_hide_id = self.after(ms, self.hide_overlay)

    def hide_overlay(self):
        try:
            self.overlay.place_forget()
            self.status_label.place_forget()
        except Exception:
            pass
        self.overlay_visible = False

    def _on_resize(self, event):
        # redraw image to fit new size
        self.show_image()

    def _on_mouse_move(self, event):
        # show cursor when mouse moves and show overlay momentarily
        self.last_mouse_move = time.time()
        if self.cursor_hidden:
            self.config(cursor="")
            self.cursor_hidden = False
        self.show_overlay(3000)
        # reset hide timer
        self._schedule_cursor_hide()

    def _schedule_cursor_hide(self):
        if self._hide_after_id:
            self.after_cancel(self._hide_after_id)
        self._hide_after_id = self.after(self._hide_cursor_after_ms, self._maybe_hide_cursor)

    def _maybe_hide_cursor(self):
        # if no recent mouse motion, hide cursor
        if time.time() - self.last_mouse_move >= (self._hide_cursor_after_ms / 1000.0):
            try:
                self.config(cursor="none")
                self.cursor_hidden = True
            except Exception:
                pass
        else:
            # reschedule
            self._schedule_cursor_hide()

    def quit(self):
        # cleanup timers
        if self._after_id:
            self.after_cancel(self._after_id)
        if self._hide_after_id:
            self.after_cancel(self._hide_after_id)
        super().quit()

if __name__ == "__main__":
    # change to False if you want to start in windowed mode
    start_fullscreen = True
    app = FullScreenSlideShow(start_fullscreen=start_fullscreen)
    # app.show_image()
    # app.update_status()
    app.mainloop()