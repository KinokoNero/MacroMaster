import sys
import time
import pickle
from pynput import mouse, keyboard
from pynput.mouse import Button, Controller, Listener

from classes import Action, Macro, Command

macros = []
keyboard_controller = Controller()


def save_macros_to_file():
    with open('macros.pkl', 'wb') as file:
        pickle.dump(macros, file)


def load_macros_from_file():
    try:
        with open('macros.pkl', 'rb') as file:
            global macros
            macros = pickle.load(file)
    except FileNotFoundError:
        return


def exit_program():
    sys.exit()


def print_help():
    print("Commands:\n"
          "Create new macro: 'new' or 'n'\n"
          "List all saved macros: 'list' or 'ls' or 'l'\n"
          "Delete saved macro: 'delete' or 'del' or 'd'\n"
          "Start listening to hotkeys: 'start' or 's'")


def listen_for_key_sequence():
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


def create_macro_wizard():
    def record_action() -> Action or None:
        TIMEOUT_DURATION = 3  # in seconds
        recorded_action = None

        # Keyboard handling
        def on_press(pressed_key):
            nonlocal recorded_action
            recorded_action = Action(action_type=Action.Type.KEY, action_input=pressed_key)
            keyboard_listener.stop()

        # Mouse handling
        def on_click(x, y, button, pressed):
            nonlocal recorded_action
            recorded_action = Action(action_type=Action.Type.CLICK, action_input=button, click_coordinates=[x, y])
            mouse_listener.stop()

        keyboard_listener = keyboard.Listener(on_press=on_press)
        keyboard_listener.start()
        mouse_listener = mouse.Listener(on_click=on_click)
        mouse_listener.start()

        # Timeout handling
        start_time = time.time()
        while keyboard_listener.running and mouse_listener.running:
            elapsed_time = time.time() - start_time
            if elapsed_time >= TIMEOUT_DURATION:
                keyboard_listener.stop()
                break

        return recorded_action

    actions = []

    # Hotkey recording
    print("Record hotkey now...")
    time.sleep(0.1)  # Added to ignore Enter while typing the create command
    hotkey = listen_for_key_sequence()

    # Macro recording
    print("Record a key and add it to the macro now...")
    while True:
        if actions:
            print("Record a key and add it to the macro now...")

        recorded_action = record_action()
        if recorded_action is not None:
            if recorded_action.action_type == Action.Type.CLICK:
                user_input = input("Should the mouse click be at the recorded location (y/n)?").lower()
                if user_input in ['no', 'n']:
                    recorded_action.click_coordinates = None

            recorded_action.action_duration = float(input("How long should the action be active (in milliseconds)?: "))
            actions.append(recorded_action)

            wait_time = float(
                input("How long should be the pause between this and the next action (in milliseconds)?: "))
            actions.append(Action(action_type=Action.Type.WAIT, action_duration=wait_time))
        elif recorded_action is None and actions:
            break

    macros.append(Macro(hotkey=hotkey, actions=actions))
    print("Macro created successfully!")

    save_macros_to_file()


def delete_macro_wizard():
    list_macros()
    index = int(input("\nEnter the number of the macro to be deleted: "))
    del macros[index - 1]
    save_macros_to_file()


def list_macros():
    def print_if_not_last_element(current_index, elements_collection, string):
        if current_index < len(elements_collection) - 1:
            print(string, end="")

    def format_action_input_name(action_input):
        formatted_action_input_name = str(action_input)
        if formatted_action_input_name.startswith("Button."):
            formatted_action_input_name = formatted_action_input_name.replace("Button.", "") + " MOUSE BUTTON"
        elif formatted_action_input_name.startswith("Key."):
            formatted_action_input_name = formatted_action_input_name.replace("Key.", "")

        return formatted_action_input_name.strip("'\"").upper()

    if not macros:
        print("No saved macros.")

    for macros_index, macro in enumerate(macros):
        print(f"Macro {macros_index + 1}:")
        print("Hotkey: ", end="")
        for hotkeys_index, hotkey in enumerate(macro.hotkey):
            print(format_action_input_name(hotkey), end="")
            print_if_not_last_element(hotkeys_index, macro.hotkey, " + ")

        print("\nSequence: ", end="")
        for actions_index, action in enumerate(macro.actions):
            print(f"{action.action_type.value} ", end="")
            if action.action_type != Action.Type.WAIT:
                print(f"{format_action_input_name(action.action_input)} ", end="")
            if action.action_type == Action.Type.CLICK and action.click_coordinates:
                print(f"at X={action.click_coordinates[0]}, Y={action.click_coordinates[1]} ", end="")
            print(f"for {action.action_duration}ms", end="")
            print_if_not_last_element(actions_index, macro.actions, " then ")

        if macros_index < len(macros) - 1:
            print()
        print()


def start_macros():
    def find_macro_by_hotkey(provided_hotkey):
        nonlocal macro
        for macro in macros:
            if macro.hotkey == provided_hotkey:
                return macro
        return None

    time.sleep(0.1)

    while True:
        pressed_keys = listen_for_key_sequence()
        macro = find_macro_by_hotkey(pressed_keys)
        if macro:
            if not macro.running:
                macro.start()
            elif macro.running:
                macro.stop()


commands = [
    Command(['quit', 'q'], 'Exits the program.', exit_program),
    Command(['help', 'h'], 'Prints available commands.', print_help),
    Command(['new', 'n'], 'Creates a new macro.', create_macro_wizard),
    Command(['list', 'ls', 'l'], 'Lists created macros.', list_macros),
    Command(['delete', 'del', 'd'], 'Deletes a chosen macro.', delete_macro_wizard),
    Command(['start', 's'], 'Allows the macros to be used.', start_macros)
]

if __name__ == '__main__':
    load_macros_from_file()
    print("Enter 'help' or 'h' to show command list.")
    print("Enter 'quit' or 'q' to quit.")

    while True:
        user_input = input()
        for command in commands:
            if user_input in command.aliases:
                command.execute()
                break
