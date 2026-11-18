#!/usr/bin/env python3
import tkinter as tk
from tkinter import font

class FullscreenNumpadApp:
    def __init__(self, root):
        self.root = root
        self.fullscreen = True

        # Window setup
        root.title("Fullscreen Numpad")
        root.attributes("-fullscreen", True)
        root.configure(bg="#111")

        # Fonts
        self.entry_font = font.Font(family="Helvetica", size=56, weight="bold")
        self.button_font = font.Font(family="Helvetica", size=28, weight="bold")
        self.small_font = font.Font(family="Helvetica", size=14)

        # Top frame holding the entry + status
        top = tk.Frame(root, bg="#111", pady=20)
        top.pack(fill="x")

        # Entry (input box)
        self.var = tk.StringVar()
        self.entry = tk.Entry(top, textvariable=self.var, font=self.entry_font,
                              justify="center", bd=6, relief="ridge", bg="#222", fg="#fff",
                              insertbackground="#fff")
        self.entry.pack(ipadx=10, ipady=20, padx=30, pady=(10, 6), fill="x", expand=True)
        self.entry.focus_set()

        # status label (shows submitted text briefly)
        self.status = tk.Label(top, text="", bg="#111", fg="#8f8", font=self.small_font)
        self.status.pack(pady=(0, 6))

        # Keep entry focused (resilient)
        root.bind_all("<Button-1>", self._refocus_entry, add='+')

        # Key bindings for keyboard input (0-9, Backspace, Delete->Reset, Return->Enter)
        for d in "0123456789":
            # root.bind(d, lambda e, ch=d: self.insert_digit(ch))
            root.bind(f"<KP_{d}>", lambda e, ch=d: self.insert_digit(ch))
        root.bind("<BackSpace>", lambda e: self.backspace())
        root.bind("<Delete>", lambda e: self.reset_all())
        root.bind("<Return>", lambda e: self.submit())
        root.bind("<KP_Enter>", lambda e: self.submit())
        root.bind("<Escape>", lambda e: self.quit_app())
        root.bind("<F11>", lambda e: self.toggle_fullscreen())

        # Numeric pad frame (4 columns)
        pad = tk.Frame(root, bg="#111", padx=30, pady=20)
        pad.pack(expand=True)

        # Buttons layout: we'll use a 4-column grid for clearer layout
        # We'll create button metadata with label and command name
        buttons_meta = [
            ('7', self._make_insert('7')), ('8', self._make_insert('8')), ('9', self._make_insert('9')), ('⬅', self.backspace),
            ('4', self._make_insert('4')), ('5', self._make_insert('5')), ('6', self._make_insert('6')), ('C', self.reset_all),
            ('1', self._make_insert('1')), ('2', self._make_insert('2')), ('3', self._make_insert('3')), ('↵', self.submit),
            ('', None), ('0', self._make_insert('0')), ('', None), ('', None),
        ]

        # Create and place buttons
        self.buttons = []
        r = 0
        c = 0
        for label, cmd in buttons_meta:
            if label == '':
                c += 1
                if c > 3:
                    c = 0
                    r += 1
                continue

            b = tk.Button(pad, text=label, command=cmd,
                          font=self.button_font, width=6, height=2, bd=4, relief="raised",
                          bg="#333", fg="#fff", activebackground="#555", activeforeground="#fff",
                          highlightthickness=0)
            b.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
            self._make_vivid(b)
            # ensure entry regains focus after click
            b.bind("<ButtonRelease-1>", lambda e: self.entry.focus_set(), add='+')

            self.buttons.append(b)
            c += 1
            if c > 3:
                c = 0
                r += 1

        # make columns expand evenly for nicer layout if not fullscreen
        for i in range(4):
            pad.grid_columnconfigure(i, weight=1)

        # small footer with tips
        footer = tk.Label(root, text="Keys: 0-9 / Backspace / Delete (Reset) / Enter (submit)  F11 toggle fullscreen  Esc exit",
                          bg="#111", fg="#ddd", font=self.small_font)
        footer.pack(side="bottom", pady=8)

    # helper to return a function that inserts a digit (avoids late binding trap)
    def _make_insert(self, ch):
        return lambda: self.insert_digit(ch)

    def insert_digit(self, ch: str):
        # append digit at the current cursor position
        idx = self.entry.index(tk.INSERT)
        s = self.var.get()
        new = s[:idx] + ch + s[idx:]
        self.var.set(new)
        self.entry.icursor(idx + 1)
        self.entry.focus_set()

    def backspace(self):
        # remove char left of cursor
        idx = self.entry.index(tk.INSERT)
        if idx > 0:
            s = self.var.get()
            new = s[:idx-1] + s[idx:]
            self.var.set(new)
            self.entry.icursor(idx-1)
        self.entry.focus_set()

    def reset_all(self):
        self.var.set("")
        self.entry.focus_set()

    def submit(self):
        text = self.var.get()
        # ---- place your actual submit/save/send logic here ----
        # For demonstration we show a temporary status label and print to console.
        print("Submitted:", text)
        self.status.configure(text=f"Submitted: {text}")
        self.root.after(2000, lambda: self.status.configure(text=""))
        # optionally keep the input or clear it:
        # self.reset_all()
        self.entry.focus_set()
        self.var.set("")

    def _refocus_entry(self, event):
        widget = event.widget
        # allow selecting text in entry when clicking it; otherwise focus back to entry
        if widget is not self.entry and not str(widget).startswith(str(self.entry)):
            # tiny delay ensures button commands run first before refocusing
            self.root.after(1, self.entry.focus_set)

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
        self.entry.focus_set()

    def quit_app(self):
        self.root.destroy()

    # Vivid button effects: hover highlight, press animation, and a quick click flash
    def _make_vivid(self, button: tk.Button):
        normal_bg = "#333"
        hover_bg = "#4a7"
        press_bg = "#2a5"
        normal_fg = "#fff"

        # store original style into button object for later restore (safe)
        button._vivid_state = (normal_bg, normal_fg)

        def on_enter(e):
            try:
                button.configure(bg=hover_bg)
            except tk.TclError:
                pass

        def on_leave(e):
            try:
                button.configure(bg=normal_bg)
            except tk.TclError:
                pass

        def on_press(e):
            try:
                button.configure(relief="sunken", bg=press_bg)
            except tk.TclError:
                pass

        def on_release(e):
            # quick flash: briefly set to a brighter color then back to hover/normal
            try:
                button.configure(relief="raised", bg="#6af")
                # after short delay restore hover or normal depending on pointer
                def restore():
                    # if mouse pointer still over widget, set hover bg, else normal
                    x, y = e.x_root, e.y_root
                    widget_under = self.root.winfo_containing(x, y)
                    if widget_under is button:
                        button.configure(bg=hover_bg)
                    else:
                        button.configure(bg=normal_bg)
                self.root.after(80, restore)
            except tk.TclError:
                pass

        # bind events
        button.bind("<Enter>", on_enter, add='+')
        button.bind("<Leave>", on_leave, add='+')
        button.bind("<ButtonPress-1>", on_press, add='+')
        button.bind("<ButtonRelease-1>", on_release, add='+')

if __name__ == "__main__":
    root = tk.Tk()
    app = FullscreenNumpadApp(root)
    root.mainloop()
