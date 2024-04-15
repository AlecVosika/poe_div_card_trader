import customtkinter as ctk
from pynput.keyboard import Key, Listener
from pynput.mouse import Button, Controller, Listener as MouseListener
import random
import time

class HotkeyTool:
    def __init__(self):
        # Create window
        self.window = ctk.CTk()
        self.window.title("Hotkey Tool")

        # Create buttons for setting hotkeys
        self.button1 = ctk.CTkButton(self.window, text="Set Hotkey 1", command=lambda: self.set_hotkey(1))
        self.button1.pack(pady=10)
        self.button2 = ctk.CTkButton(self.window, text="Set Hotkey 2", command=lambda: self.set_hotkey(2))
        self.button2.pack()

        # Hotkey variables
        self.hotkey1 = None
        self.hotkey2 = None

        # Create buttons for getting locations
        self.loc_button1 = ctk.CTkButton(self.window, text="Get Location 1", command=lambda: self.get_location(1))
        self.loc_button1.pack(pady=10)
        self.loc_button2 = ctk.CTkButton(self.window, text="Get Location 2", command=lambda: self.get_location(2))
        self.loc_button2.pack()

        # Location variables
        self.location1 = None
        self.location2 = None

        # Mouse controller and listener
        self.mouse = Controller()
        self.mouse_listener = MouseListener(on_move=self.on_mouse_move)
        self.mouse_listener.start()

        # On/Off Switch
        self.switch_var = ctk.StringVar(value="off")
        self.switch = ctk.CTkSwitch(self.window, text="Automation", command=self.toggle_automation, variable=self.switch_var, onvalue="on", offvalue="off")
        self.switch.pack(pady=10)

        # Automation variables
        self.automation_active = False
        self.initial_location = None
        self.click_count = 0
        self.left_button_down = False
        self.waiting_for_release = False
        self.current_mouse_position = None

        # Initialize listeners for hotkey and location capture
        self.hotkey_listener1 = Listener(on_press=lambda key: self.on_hotkey_press(key, 1))
        self.hotkey_listener2 = Listener(on_press=lambda key: self.on_hotkey_press(key, 2))
        self.location_listener1 = Listener(on_press=lambda key: self.on_location_press(key, 1))
        self.location_listener2 = Listener(on_press=lambda key: self.on_location_press(key, 2))

        # Initialize listeners for automation
        self.keyboard_listener = Listener(on_press=self.on_press)

        # Start automation listeners immediately 
        self.keyboard_listener.start()

        self.window.mainloop()

    def on_mouse_move(self, x, y):
        self.current_mouse_position = (x, y)

    def move_to_location(self, target_location):
        current_x, current_y = self.mouse.position
        target_x, target_y = target_location

        steps = 10  # Number of steps to take
        for i in range(steps + 1):
            # Calculate intermediate coordinates
            intermediate_x = current_x + (target_x - current_x) * i / steps
            intermediate_y = current_y + (target_y - current_y) * i / steps
            self.mouse.position = (int(intermediate_x), int(intermediate_y))
            time.sleep(0.01)  # Adjust delay as needed

    def set_hotkey(self, button_num):
        if button_num == 1:
            self.hotkey_listener1.start()  # Start listener for hotkey 1
        elif button_num == 2:
            self.hotkey_listener2.start()  # Start listener for hotkey 2

    def on_hotkey_press(self, key, button_num):
        if button_num == 1:
            self.hotkey1 = key
            self.button1.configure(text=f"Hotkey 1: {key}")
            self.hotkey_listener1.stop()  # Stop listener for hotkey 1
        elif button_num == 2:
            self.hotkey2 = key
            self.button2.configure(text=f"Hotkey 2: {key}")
            self.hotkey_listener2.stop()  # Stop listener for hotkey 2

    def get_location(self, button_num):
        if button_num == 1:
            self.location_listener1.start()  # Start listener for location 1
        elif button_num == 2:
            self.location_listener2.start()  # Start listener for location 2

    def on_location_press(self, key, button_num):
        if button_num == 1 and key == self.hotkey1:
            self.location1 = self.current_mouse_position  # Use the tracked position
            self.loc_button1.configure(text=f"Location 1: {self.location1}")
            self.location_listener1.stop()  # Stop listener for location 1
        elif button_num == 2 and key == self.hotkey2:
            self.location2 = self.current_mouse_position
            self.loc_button2.configure(text=f"Location 2: {self.location2}")

    def toggle_automation(self):
        self.automation_active = self.switch_var.get() == "on"

    def on_press(self, key):
        if self.automation_active and key == Key.ctrl_l and self.left_button_down:
            self.waiting_for_release = True

    def on_click(self, x, y, button, pressed):
        if button == Button.left:
            self.left_button_down = pressed
            if not pressed and self.waiting_for_release:
                with Controller() as keyboard:
                    keyboard.press(Key.ctrl_l)  # Press Ctrl
                    if self.click_count == 0:
                        self.initial_location = self.mouse.position
                        self.click_count += 1
                        # Move to a new random location around location1
                        x, y = self.location1  # Get current base position
                        x += random.randint(-15, 15)  # Add random offset
                        y += random.randint(-15, 15)
                        self.move_to_location((x, y)) 
                    elif self.click_count == 1:
                        self.click_count += 1
                        # Move to a new random location around location2
                        x, y = self.location2  # Get current base position
                        x += random.randint(-15, 15)  # Add random offset
                        y += random.randint(-15, 15)
                        self.move_to_location((x, y)) 
                    else:
                        self.click_count = 0
                        self.move_to_location(self.initial_location) 
                    keyboard.release(Key.ctrl_l)  # Release Ctrl
                self.waiting_for_release = False

if __name__ == "__main__":
    HotkeyTool()