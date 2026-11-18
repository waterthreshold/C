import pyautogui
import tkinter as tk
from tkinter import Menu
from tkinter import messagebox
# ================================
#  CIRCLE BUTTON CONFIG
# ================================
BTN_RADIUS = 60
BTN_COLOR = "deepskyblue"
BTN_HOVER = "dodgerblue"
TEXT_COLOR = "white"

# ================================
#  CALLBACK FUNCTION
# ================================
PRESS_CLICK_EVENT=0
def on_click():
    pyautogui.hotkey('win', 'ctrl', 'o')

def click_event(event):
    x, y = event.x, event.y
    if (x - BTN_RADIUS)**2 + (y - BTN_RADIUS)**2 <= BTN_RADIUS**2:
        on_click()

def hover_enter(event):
    global PRESS_CLICK_EVENT
    PRESS_CLICK_EVENT=1
    canvas.itemconfig(circle, fill=BTN_HOVER)
    

def hover_leave(event):
    global PRESS_CLICK_EVENT
    if PRESS_CLICK_EVENT == 1:
        pyautogui.hotkey('win', 'ctrl', 'o')
        PRESS_CLICK_EVENT=0
    canvas.itemconfig(circle, fill=BTN_COLOR)

def drag(event):
    root.geometry(f"+{event.x_root - BTN_RADIUS}+{event.y_root - BTN_RADIUS}")

def show_popup(event):
    popup.post(event.x_root, event.y_root)

def pop_version():
    messagebox.showinfo(title=r"Version", message="Version: 0.1\nAuthor: Jeff") 
# ================================
#  GUI SETUP
# ================================
root = tk.Tk()
root.overrideredirect(True)     # Remove window frame/title bar
root.wm_attributes("-topmost", True)  # Keep on top (optional)
TRANSPARENT_COLOR = "pink"
root.config(bg=TRANSPARENT_COLOR)
root.wm_attributes("-transparentcolor", TRANSPARENT_COLOR)
root.geometry(f"{BTN_RADIUS*2}x{BTN_RADIUS*2}+800+400")  # Position on screen

# Menu part 
popup = Menu(root, tearoff=0)
popup.add_command(label="version", command=pop_version)
# popup.add_command(label="Say Goodbye", command=say_goodbye)
popup.add_separator()
popup.add_command(label="Exit", command=root.quit)

# 

canvas = tk.Canvas(
    root,
    width=BTN_RADIUS*2,
    height=BTN_RADIUS*2,
    bg=TRANSPARENT_COLOR,
    highlightthickness=0
)
canvas.pack()

# Create circle
circle = canvas.create_oval(
    0, 0, BTN_RADIUS*2, BTN_RADIUS*2,
    fill=BTN_COLOR,
    outline=""
)

# Text label
label = canvas.create_text(
    BTN_RADIUS, BTN_RADIUS,
    text="OSK",
    fill=TEXT_COLOR,
    font=("Arial", 16, "bold")
)

# ================================
#  EVENT HANDLING
# ================================
   

# Bind events
canvas.bind("<Button-1>", click_event)
# canvas.bind("<Enter>", hover_enter)
canvas.bind("<ButtonPress-1>", hover_enter)   # Left mouse button down
canvas.bind("<ButtonRelease-1>", hover_leave)  # Left mouse button up
canvas.bind("<Leave>", hover_leave)
canvas.bind("<B1-Motion>", drag)
canvas.bind("<Button-3>", show_popup)
root.mainloop()