import time
import pyautogui

print("Move your mouse around. Press Ctrl+C in your terminal to stop.")

try:
    while True:
        # Get the current x and y positions
        x, y = pyautogui.position()
        
        # Print the positions on the same line
        print(f"X: {x} Y: {y}", end="\r")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nDone.")