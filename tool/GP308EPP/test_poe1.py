import tkinter as tk
from tkinter import font

class PoESwitchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PoE Switch Port Controller")
        self.root.geometry("820x240")
        self.root.config(bg="#2b2b2b") # Dark industrial background for switch chassis

        # Main Switch Chassis Frame (Outer Black/Dark Box with border)
        chassis = tk.Frame(root, bg="#1e1e1e", bd=4, relief="solid")
        chassis.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)

        # Title / Switch Label
        title_lbl = tk.Label(chassis, text="PoE Switch Model-8004 [Ports 1-4]", 
                             fg="#888888", bg="#1e1e1e", font=("Arial", 10, "bold"))
        title_lbl.pack(anchor="w", padx=10, pady=(5, 0))

        # Container for the port cards (lays them out horizontally)
        ports_container = tk.Frame(chassis, bg="#1e1e1e")
        ports_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Port Data (Initial states for 4 ports)
        self.ports_data = [
            {"id": 1, "voltage": "53.2V", "current": "0.15A", "power": "8.0W", "class": "Class 4", "state": True},
            {"id": 2, "voltage": "54.0V", "current": "0.32A", "power": "17.2W", "class": "Class 4", "state": True},
            {"id": 3, "voltage": "0.0V",  "current": "0.00A", "power": "0.0W",  "class": "Disconnected", "state": False},
            {"id": 4, "voltage": "52.8V", "current": "0.08A", "power": "4.2W",  "class": "Class 2", "state": True},
        ]

        # Keep track of UI elements for updating later
        self.port_cards = []

        # Generate each port widget block based on the data
        for index, data in enumerate(self.ports_data):
            card = self.create_port_card(ports_container, data)
            card.pack(side=tk.LEFT, padx=10, expand=True, fill=tk.BOTH)
            self.port_cards.append(card)

    def create_port_card(self, parent, data):
        # Outer Card Frame (representing the red box in your drawing)
        card_frame = tk.Frame(parent, bg="#ffffff", bd=2, relief="groove")
        
        # Top Info Section (Displays metrics like voltage, power, class)
        info_frame = tk.Frame(card_frame, bg="#f0f0f0", bd=1, relief="solid")
        info_frame.pack(fill=tk.X, padx=8, pady=8)

        port_label = tk.Label(info_frame, text=f"Port {data['id']}", bg="#f0f0f0", font=("Arial", 9, "bold"), fg="#333333")
        port_label.pack(anchor="w", padx=4, pady=(2, 0))

        # Detail text widget inside info panel
        info_text = f"{data['voltage']} | {data['current']}\n{data['power']} ({data['class']})"
        info_val_lbl = tk.Label(info_frame, text=info_text, bg="#f0f0f0", font=("Consolas", 8), fg="#0055aa", justify="left")
        info_val_lbl.pack(anchor="w", padx=4, pady=(0, 2))

        # Power Toggle Button (the circle/power icon representation)
        # We use a button that changes color depending on port state
        btn_color = "#2ecc71" if data['state'] else "#e74c3c"
        btn_text = "PWR ON" if data['state'] else "PWR OFF"
        
        power_btn = tk.Button(card_frame, text=btn_text, bg=btn_color, fg="white", 
                              font=("Arial", 9, "bold"), width=12, height=2,
                              command=lambda d=data: self.toggle_port(d))
        power_btn.pack(pady=(10, 15), padx=8)

        # Store references inside the card frame object for easy updating
        card_frame.info_lbl = info_val_lbl
        card_frame.power_btn = power_btn
        
        return card_frame

    def toggle_port(self, data):
        # Toggle state
        data['state'] = not data['state']
        
        # If turned off, zero out metrics
        if not data['state']:
            data['voltage'] = "0.0V"
            data['current'] = "0.00A"
            data['power'] = "0.0W"
            data['class'] = "Off / Standby"
        else:
            # Restore sample active metrics when turned back on
            data['voltage'] = "53.5V"
            data['current'] = "0.20A"
            data['power'] = "10.7W"
            data['class'] = "Class 4"

        # Refresh UI for this specific port
        for card in self.port_cards:
            # Find the matching card and update its widgets
            if f"Port {data['id']}" in card.winfo_children()[0].winfo_children()[0].cget("text"):
                new_info = f"{data['voltage']} | {data['current']}\n{data['power']} ({data['class']})"
                card.info_lbl.config(text=new_info)
                
                if data['state']:
                    card.power_btn.config(text="PWR ON", bg="#2ecc71")
                else:
                    card.power_btn.config(text="PWR OFF", bg="#e74c3c")

if __name__ == "__main__":
    root = tk.Tk()
    app = PoESwitchApp(root)
    root.mainloop()