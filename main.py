from pynput import mouse, keyboard
from pynput.mouse import Button, Controller
import threading
import time

from classes import Action, Macro

macros = {}
keyboard_controller = Controller()


def on_hotkey_activate(hotkey):
    print("test")


def activate_macro(macro):
    macro.start()


def create_macro_wizard():
    def record_key_sequence():
        pressed_keys = {}

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
    time.sleep(0.01)  # Added to ignore Enter while typing the 'new' command
    hotkey = record_key_sequence()

    print("Record a key and add it to the macro now...")
    while True:
        if actions:
            print("Record a key and add it to the macro now...")
        recorded_action = record_action()
        if recorded_action is not None:
            action_duration = float(input("How long should the action be active (in milliseconds)?: "))
            actions.append(Action(action_type=Action.Type.KEY, action_duration=action_duration, action_key=recorded_action))
            wait_time = float(input("How long should be the pause between this and the next action (in milliseconds)?: "))
            actions.append(Action(Action.Type.WAIT, wait_time))
        elif recorded_action is None and actions:
            break

    macros[tuple(hotkey)] = Macro(hotkey, actions)
    print("Macro created successfully!")


def list_macros():
    def print_if_not_last_element(current_index, elements_collection, string):
        if current_index < len(elements_collection) - 1:
            print(string, end="")

    def format_key_name(key):
        return str(key).replace("Key.", "").strip("'\"").upper()

    for macros_index, macro_hotkey in enumerate(macros):
        print("Hotkey: ", end="")
        for hotkeys_index, key in enumerate(macro_hotkey):
            print(format_key_name(key), end="")
            print_if_not_last_element(hotkeys_index, macro_hotkey, " + ")

        print("\nSequence: ", end="")
        for actions_index, action in enumerate(macros[macro_hotkey].actions):
            print(f"{action.action_type.value} ", end="")
            if action.action_type == Action.Type.KEY:
                print(f"{format_key_name(action.action_key)} ", end="")
            print(f"for {action.action_duration}ms", end="")
            print_if_not_last_element(actions_index, macros[macro_hotkey].actions, " then ")

        if macros_index < len(macros) - 1:
            print()
        print()


if __name__ == '__main__':
    print("Enter 'help' or 'h' to show command list.")
    print("Enter 'quit' or 'q' to quit.\n")

    while True:
        command = input()

        if command.startswith(('new', 'n')):
            create_macro_wizard()

        if command.startswith(('list', 'l')):
            list_macros()
