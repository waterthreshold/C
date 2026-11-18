import subprocess
import time
import pyautogui
time.sleep(3)
# 1. Launch your app in the background
# process = subprocess.Popen(["python", "poe_controller.py"])
# time.sleep(10) # Wait for window to load
print('start')

# 2. Automatically click the main button (adjust coordinates to match your layout)
pyautogui.click(x=653, y=50399) 
time.sleep(1)
pyautogui.click(x=945, y=61749) 
time.sleep(1)
# 3. Automatically click 'Yes' on the pop-up dialog coordinate
# pyautogui.click(x=200, y=200)

# 4. Terminate app process
# process.terminate()