import pickle
import sys

from pynput import mouse, keyboard
from pynput.mouse import Controller

from classes import Action, Macro, Command, ActionType

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


def format_input_code_str(input_code) -> str:
    formatted_action_input_name = str(input_code)
    if formatted_action_input_name.startswith("Button."):
        formatted_action_input_name = formatted_action_input_name.replace("Button.", "") + " MOUSE BUTTON"
    elif formatted_action_input_name.startswith("Key."):
        formatted_action_input_name = formatted_action_input_name.replace("Key.", "")
    return formatted_action_input_name.strip("'\"").upper()


def record_hotkey() -> list:
    inputs = {}

    def check_inactivity():
        if inputs and all(value is False for value in inputs.values()):
            keyboard_listener.stop()

    def on_press(key):
        inputs[key] = True

    def on_release(key):
        if key in inputs:
            inputs[key] = False
        check_inactivity()

    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()

    while keyboard_listener.running:
        pass

    return list(inputs.keys())


def listen_for_input() -> Action or None:
    action = None

    def stop_listeners():
        mouse_listener.stop()
        keyboard_listener.stop()

    def on_click(x, y, button, pressed):
        stop_listeners()
        nonlocal action, action_recorded
        action = Action(action_type=ActionType.CLICK, input_code=button)
        if input("Include mouse coordinates in saved action? (yes/no)") in ['yes', 'y']:
            action.mouse_coordinates = (x, y)
        action_recorded = True

    def on_press(key):
        stop_listeners()
        nonlocal action, action_recorded
        action = Action(action_type=ActionType.KEY, input_code=key)
        action_recorded = True

    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()
    keyboard_listener = keyboard.Listener(on_press=on_press)
    keyboard_listener.start()

    action_recorded = False
    while not action_recorded:
        pass

    return action


def create_macro():
    actions = []

    print("Record a hotkey for the macro now...")
    hotkey = record_hotkey()

    add_more_actions = True
    while add_more_actions:
        print("Record an action for the macro now...")
        action = listen_for_input()

        action.duration = float(input("How long should the action be active (in milliseconds)?: "))

        actions.append(action)

        wait_duration = float(
            input("How long should be the pause between this and the next input (in milliseconds)?: ")
        )
        if wait_duration > 0:
            wait = Action(ActionType.WAIT, wait_duration)
            actions.append(wait)

        add_more_actions = input("Do you want to add another action to the macro? (yes/no)") in ['yes', 'y']

    macro = Macro(hotkey=hotkey, actions=actions)
    macros.append(macro)
    save_macros_to_file()

    print("Macro created.")


def delete_macro():
    list_macros()
    index = int(input("\nEnter the number of the macro to be deleted: "))
    del macros[index - 1]
    save_macros_to_file()


def list_macros():
    def print_if_not_last_element(current_index, elements_collection, string):
        if current_index < len(elements_collection) - 1:
            print(string, end="")

    if not macros:
        print("No saved macros.")

    for macros_index, macro in enumerate(macros):
        print(f"Macro {macros_index + 1}:")
        print("Hotkey: ", end="")
        for hotkeys_index, hotkey_part in enumerate(macro.hotkey):
            print(format_input_code_str(hotkey_part), end="")
            print_if_not_last_element(hotkeys_index, macro.hotkey, " + ")

        print("\nSequence: ", end="")
        for actions_index, action in enumerate(macro.actions):
            if action.action_type != ActionType.WAIT:
                if action.action_type == ActionType.CLICK:
                    print("click ", end="")
                elif action.action_type == ActionType.KEY:
                    print("press ", end="")

                print(f"{format_input_code_str(action.input_code)} ", end="")

                if action.mouse_coordinates is not None:
                    print(f"at X={action.mouse_coordinates[0]}, Y={action.mouse_coordinates[1]} ", end="")

            elif action.action_type == ActionType.WAIT:
                print("wait ", end="")

            print(f"for {action.duration}ms", end="")

            print_if_not_last_element(actions_index, macro.actions, " then ")

        if macros_index < len(macros) - 1:
            print()
        print()


def start_macros():
    def hotkey_to_str(hotkey) -> str:
        hotkey_str = ""
        special_keys = [
            "alt", "alt_gr", "alt_l", "alt_r", "backspace", "caps_lock", "cmd", "cmd_l", "cmd_r", "ctrl", "ctrl_l",
            "ctrl_r", "delete", "down", "end", "enter", "esc", "f1", "home", "insert", "left", "media_next",
            "media_play_pause", "media_previous", "media_volume_down", "media_volume_mute", "media_volume_up", "menu",
            "num_lock", "page_down", "page_up", "pause", "print_screen", "right", "scroll_lock", "shift", "shift_l",
            "shift_r", "space", "tab", "up"
        ]

        for index, key in enumerate(hotkey):
            key_str = str(key)
            if key_str.startswith("Key."):
                hotkey_str += f"<{key_str.replace('Key.', '')}>"
            else:
                hotkey_str += format_input_code_str(key_str)

            if index < len(hotkey) - 1:
                hotkey_str += "+"

        return hotkey_str

    global_hotkeys = {}
    for macro in macros:
        hotkey_string = hotkey_to_str(macro.hotkey)

        global_hotkeys[hotkey_string] = macro.toggle

    with keyboard.GlobalHotKeys(global_hotkeys) as hotkeys:
        hotkeys.join()


commands = [
    Command(['quit', 'q'], 'Exits the program.', exit_program),
    Command(['help', 'h'], 'Prints available commands.', print_help),
    Command(['new', 'n'], 'Creates a new macro.', create_macro),
    Command(['list', 'ls', 'l'], 'Lists created macros.', list_macros),
    Command(['delete', 'del', 'd'], 'Deletes a chosen macro.', delete_macro),
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
