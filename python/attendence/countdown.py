import tkinter as tk
from tkinter import messagebox
import time

# 7-segment mapping for digits 0-9 (segments a,b,c,d,e,f,g)
SEGMENTS = {
    '0': (1,1,1,1,1,1,0),
    '1': (0,1,1,0,0,0,0),
    '2': (1,1,0,1,1,0,1),
    '3': (1,1,1,1,0,0,1),
    '4': (0,1,1,0,0,1,1),
    '5': (1,0,1,1,0,1,1),
    '6': (1,0,1,1,1,1,1),
    '7': (1,1,1,0,0,0,0),
    '8': (1,1,1,1,1,1,1),
    '9': (1,1,1,1,0,1,1),
    ' ': (0,0,0,0,0,0,0)
}

# Visual tuning
DIGIT_WIDTH = 40
DIGIT_HEIGHT = 80
SEG_GAP = 6            # gap between segments
SEG_THICK = 12         # thickness of segment
DIGIT_SPACING = 10
COLON_WIDTH = 10
COLON_HEIGHT = 10

ON_COLOR = "#FF3B30"   # lit segment color (red-ish)
OFF_COLOR = "#2B2B2B"  # unlit segment color (dark gray)
BG_COLOR = "#000000"   # background

class SevenSegDigit:
    def __init__(self, canvas, x, y, width=DIGIT_WIDTH, height=DIGIT_HEIGHT):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.w = width
        self.h = height
        self.seg_items = {}
        self._create_segments()

    def _poly(self, points):
        # shift points by (x,y)
        return [coord + off for coord, off in zip(points, (self.x, self.y) * (len(points)//2))] if False else points

    def _create_segments(self):
        x, y, w, h = 0, 0, self.w, self.h
        t = SEG_THICK
        g = SEG_GAP
        # Precompute key coordinates for polygons for segments a..g (relative to x=0,y=0)
        # We will use simple polygons for segments: each segment is a rectangle with chamfer-like ends.
        # a (top horizontal)
        a = [(g, 0), (w - g, 0), (w - g - t, t), (g + t, t)]
        # d (bottom horizontal)
        d = [(g, h ) , (w - g, h) ,(w - g - t  , h - t), ( g+t, h - t)]
        # g (middle horizontal)
        gpos = h/2# - t/2
        gseg = [(g, gpos), (g + t, gpos - g ), (w - g - t, gpos -g ), (w - g, gpos ) ,(w - g - t , gpos + g ) ,(g + t , gpos + g )]
        # f (top-left vertical)
        f = [(0, g), (t, g + t), (t, h/2 - t//2), (0, h/2)]
        # b (top-right vertical)
        b = [(w - t, g + t), (w, g), (w, h/2), (w - t, h/2 - t//2)]
        # e (bottom-left vertical)
        e = [(0, h/2), (t, h/2 + t//2), (t, h - g - t), (0, h - g)]
        # c (bottom-right vertical)
        c = [(w - t, h/2 + t//2), (w, h/2), (w, h - g), (w - t, h - g - t)]

        coords = {
            'a': a, 'b': b, 'c': c, 'd': d, 'e': e, 'f': f, 'g': gseg
        }

        # create polygons and store IDs
        for name, pts in coords.items():
            # shift by self.x,self.y when drawing
            flat = []
            for px, py in pts:
                flat.extend((self.x + px, self.y + py))
            item = self.canvas.create_polygon(flat, fill=OFF_COLOR, outline=OFF_COLOR)
            self.seg_items[name] = item

    def set_digit(self, ch):
        patt = SEGMENTS.get(ch, SEGMENTS[' '])
        for name, on in zip(['a','b','c','d','e','f','g'], patt):
            color = ON_COLOR if on else OFF_COLOR
            self.canvas.itemconfigure(self.seg_items[name], fill=color, outline=color)

class Colon:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.top = canvas.create_oval(x, y, x + COLON_WIDTH, y + COLON_HEIGHT, fill=OFF_COLOR, outline=OFF_COLOR)
        self.bottom = canvas.create_oval(x, y + COLON_HEIGHT + 10, x + COLON_WIDTH, y + 2*COLON_HEIGHT + 10, fill=OFF_COLOR, outline=OFF_COLOR)

    def set_on(self, on=True):
        color = ON_COLOR if on else OFF_COLOR
        self.canvas.itemconfigure(self.top, fill=color, outline=color)
        self.canvas.itemconfigure(self.bottom, fill=color, outline=color)


class CountdownApp:
    def __init__(self, root):
        self.root = root
        root.title("7-Segment Countdown Timer")
        root.configure(bg=BG_COLOR)

        control_frame = tk.Frame(root, bg=BG_COLOR)
        control_frame.pack(padx=10, pady=8, anchor='n')

        tk.Label(control_frame, text="Enter time (HH:MM:SS):", fg="white", bg=BG_COLOR).grid(row=0, column=0, columnspan=4)
        self.entry = tk.Entry(control_frame, width=12, justify='center', font=("Consolas", 12))
        self.entry.insert(0, "00:01:00")
        self.entry.grid(row=1, column=0, columnspan=2, pady=6)

        self.start_btn = tk.Button(control_frame, text="Start", command=self.start)
        self.pause_btn = tk.Button(control_frame, text="Pause", command=self.pause, state='disabled')
        self.reset_btn = tk.Button(control_frame, text="Reset", command=self.reset, state='disabled')
        self.start_btn.grid(row=1, column=2, padx=4)
        self.pause_btn.grid(row=1, column=3, padx=4)
        self.reset_btn.grid(row=1, column=4, padx=4)

        # Canvas for display
        total_digits = 8  # HH:MM:SS => 8 with two colons
        canvas_width = (DIGIT_WIDTH * 6) + (DIGIT_SPACING * 5) + (COLON_WIDTH * 2) + 40
        canvas_height = DIGIT_HEIGHT + 20
        self.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(padx=10, pady=6)

        # create digits and colons
        self.digits = []
        x = 20
        # positions for H H : M M : S S
        for i in range(8):
            if i in (2,5):  # colon positions (after HH and after MM)
                col = Colon(self.canvas, x, 20)
                self.digits.append(col)
                x += COLON_WIDTH + DIGIT_SPACING
            else:
                d = SevenSegDigit(self.canvas, x, 10)
                self.digits.append(d)
                x += DIGIT_WIDTH + DIGIT_SPACING

        self.running = False
        self.time_left = 0
        self._timer_id = None
        self.colon_state = True

        # initial display
        self._update_display_from_seconds(0)

    def _parse_input(self):
        s = self.entry.get().strip()
        try:
            parts = s.split(':')
            if len(parts) != 3:
                raise ValueError
            h, m, sec = map(int, parts)
            if m < 0 or m > 59 or sec < 0 or sec > 59 or h < 0:
                raise ValueError
            return h*3600 + m*60 + sec
        except Exception:
            messagebox.showerror("Invalid input", "Please enter time as HH:MM:SS (e.g. 01:02:03)")
            return None

    def _seconds_to_hms(self, secs):
        h = secs // 3600
        m = (secs % 3600) // 60
        s = secs % 60
        return h, m, s

    def _update_display_from_seconds(self, secs):
        h, m, s = self._seconds_to_hms(max(0, secs))
        # format HH MM SS as 2-digit each
        text = f"{h:02}{m:02}{s:02}"  # 6 digits
        # map to digit objects (skip colon positions)
        idx = 0
        for i, obj in enumerate(self.digits):
            if isinstance(obj, Colon):
                # colon
                obj.set_on(self.colon_state and self.running)
            else:
                ch = text[idx]
                obj.set_digit(ch)
                idx += 1

    def start(self):
        if self.running:
            return
        secs = self._parse_input()
        if secs is None or secs <= 0:
            return
        self.time_left = secs
        self.running = True
        self.start_btn.config(state='disabled')
        self.pause_btn.config(state='normal', text="Pause")
        self.reset_btn.config(state='normal')
        self._tick()

    def _tick(self):
        # update colon blink
        self.colon_state = not self.colon_state
        self._update_display_from_seconds(self.time_left)

        if self.time_left <= 0:
            self.running = False
            self.start_btn.config(state='normal')
            self.pause_btn.config(state='disabled')
            self.reset_btn.config(state='normal')
            messagebox.showinfo("Time's up", "Countdown finished!")
            return

        self.time_left -= 1
        # schedule next tick in 1 second
        self._timer_id = self.root.after(1000, self._tick)

    def pause(self):
        if not self.running:
            # resume
            if self.time_left > 0:
                self.running = True
                self.pause_btn.config(text="Pause")
                self.start_btn.config(state='disabled')
                self._tick()
            return
        # pause
        self.running = False
        if self._timer_id:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None
        self.pause_btn.config(text="Resume")
        self.start_btn.config(state='normal')

    def reset(self):
        # stop
        if self._timer_id:
            self.root.after_cancel(self._timer_id)
            self._timer_id = None
        self.running = False
        self.time_left = 0
        self._update_display_from_seconds(0)
        self.start_btn.config(state='normal')
        self.pause_btn.config(state='disabled', text="Pause")
        self.reset_btn.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownApp(root)
    root.mainloop()