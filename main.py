from pynput import mouse, keyboard
from pynput.mouse import Button, Controller
import threading
import time

macros = {}
keyboard_controller = Controller()


def on_hotkey_activate(hotkey):
    print("test")


class Macro:
    def __init__(self, hotkey, actions):
        self.hotkey = hotkey
        self.actions = actions
        self.running = False
        self.thread = None

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def run(self):  # TODO: fix this
        while self.running:
            keyboard_controller.press(self.macro_key)
            time.sleep(self.pressed_duration)
            keyboard_controller.release(self.macro_key)
            time.sleep(self.released_duration)


def activate_macro(macro):
    macro.start()


def create_macro_wizard():
    def record_key_sequence():
        pressed_keys = {}
        hotkey = None

        def on_press(key):
            pressed_keys[key] = True

        def on_release(key):
            if key in pressed_keys:
                pressed_keys[key] = False

            if all(value is False for value in pressed_keys.values()):
                keyboard_listener.stop()

        keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        keyboard_listener.start()

        while keyboard_listener.running:
            pass

        return list(pressed_keys.keys())

    def record_action() -> object:
        TIMEOUT_DURATION = 3  # in seconds
        recorded_action = None

        # Mouse handling TODO

        # Keyboard handling
        pressed_keys = {}

        def on_press(pressed_key):
            nonlocal recorded_action
            recorded_action = pressed_key
            keyboard_listener.stop()

        keyboard_listener = keyboard.Listener(on_press=on_press)
        keyboard_listener.start()

        start_time = time.time()
        while keyboard_listener.running:
            elapsed_time = time.time() - start_time
            if elapsed_time >= TIMEOUT_DURATION:
                keyboard_listener.stop()
                break

        return recorded_action

    actions = []

    print("Record hotkey now...")
    time.sleep(0.1)  # Added to ignore Enter while typing the 'new' command
    hotkey = record_key_sequence()

    while True:
        print("Record a key and add it to the macro now...")
        recorded_action = record_action()
        if recorded_action is not None:
            actions.append(recorded_action)
        elif recorded_action is None and actions:
            break

    macros[hotkey] = Macro(hotkey, actions)  # TODO: fix this

    print("Macro created successfully!")


if __name__ == '__main__':
    print("Enter 'help' or 'h' to show command list.")
    print("Enter 'quit' or 'q' to quit.\n")

    while True:
        command = input()

        if command.startswith(('new', 'n')):
            create_macro_wizard()

        if command.startswith(('list', 'l')):
            print("TODO")
