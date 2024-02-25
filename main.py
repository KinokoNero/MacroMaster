import pickle
import sys
import time

from pynput import mouse, keyboard
from pynput.mouse import Controller

from classes import Action, Macro, Command, Input

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


def listen_for_inputs():
    inputs = {}
    input_key = None

    def check_inactivity():
        if inputs and all(value is False for value in inputs.values()):
            mouse_listener.stop()
            keyboard_listener.stop()

    def on_click(x, y, button, pressed):
        nonlocal input_key
        input_key = Input(Input.InputSource.MOUSE, Input.InputEvent(input_code=button, input_coordinates={'x': x, 'y': y}))
        if pressed:
            inputs[input_key] = True
        else:
            inputs[input_key] = False
            check_inactivity()

    def on_press(key):
        nonlocal input_key
        input_key = Input(Input.InputSource.KEYBOARD, Input.InputEvent(input_code=key))
        inputs[input_key] = True

    def on_release(key):
        nonlocal input_key
        input_key = Input(Input.InputSource.KEYBOARD, Input.InputEvent(input_code=key))
        if input_key in inputs:
            inputs[input_key] = False
        check_inactivity()

    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()

    while mouse_listener.running and keyboard_listener.running:
        pass

    return list(inputs.keys())


def format_action_input_name(action_input):
    formatted_action_input_name = str(action_input)
    if formatted_action_input_name.startswith("Button."):
        formatted_action_input_name = formatted_action_input_name.replace("Button.", "") + " MOUSE BUTTON"
    elif formatted_action_input_name.startswith("Key."):
        formatted_action_input_name = formatted_action_input_name.replace("Key.", "")
    return formatted_action_input_name.strip("'\"").upper()


def create_macro_wizard():
    def listen_for_single_input() -> Input:
        # Mouse handling
        def on_click(x, y, button, pressed):
            nonlocal recorded_input
            recorded_input = Input(Input.InputSource.MOUSE, Input.InputEvent(input_code=button, input_coordinates={'x': x, 'y': y}))
            mouse_listener.stop()

        # Keyboard handling
        def on_press(pressed_key):
            nonlocal recorded_input
            recorded_input = Input(Input.InputSource.KEYBOARD, Input.InputEvent(input_code=pressed_key))
            keyboard_listener.stop()

        keyboard_listener = keyboard.Listener(on_press=on_press)
        keyboard_listener.start()
        mouse_listener = mouse.Listener(on_click=on_click)
        mouse_listener.start()

        while keyboard_listener.running and mouse_listener.running:
            pass

        keyboard_listener.stop()
        mouse_listener.stop()
        return recorded_input

    actions = []

    # Hotkey recording
    print("Record hotkey now...")
    time.sleep(0.1)  # Added to ignore Enter while typing the create command
    hotkey = listen_for_inputs()

    # Macro recording
    add_more_actions = True
    while add_more_actions:
        add_another_simultaneous_action = True
        while add_another_simultaneous_action:
            print("Record a key and add it to the macro now...")
            recorded_input = listen_for_single_input()
            if recorded_input is not None:
                if recorded_input.input_source == Input.InputSource.MOUSE:
                    if input("Should the mouse click be at the recorded location (y/n)?\n").lower() in ['no', 'n']:
                        recorded_input.input_event.input_coordinates = None

                action_duration = float(input("How long should the action be active (in milliseconds)?: "))
                action = Action(action_duration=action_duration, action_input=recorded_input)
                actions.append(action)

            if input("Do you want to add another simultaneous input (y/n)?\n").lower() in ['no', 'n']:
                add_another_simultaneous_action = False

        wait_time = float(
            input("How long should be the pause between this and the next set of actions (in milliseconds)?: "))
        actions.append(Action(action_duration=wait_time))

        if input("Do you still want to add more actions to this macro (y/n)?\n").lower() in ['no', 'n']:
            add_more_actions = False

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

    if not macros:
        print("No saved macros.")

    for macros_index, macro in enumerate(macros):
        print(f"Macro {macros_index + 1}:")
        print("Hotkey: ", end="")
        for hotkeys_index, hotkey in enumerate(macro.hotkey):
            print(format_action_input_name(hotkey.input_event.input_code), end="")
            print_if_not_last_element(hotkeys_index, macro.hotkey, " + ")

        print("\nSequence: ", end="")
        for actions_index, action in enumerate(macro.actions):
            if action.action_input is not None:
                if action.action_input.input_source == Input.InputSource.MOUSE:
                    print("click ", end="")
                elif action.action_input.input_source == Input.InputSource.KEYBOARD:
                    print("press ", end="")

                print(f"{format_action_input_name(action.action_input.input_event.input_code)} ", end="")

                if action.action_input.input_event.input_coordinates is not None:
                    print(f"at X={action.action_input.input_event.input_coordinates['x']}, Y={action.action_input.input_event.input_coordinates['y']} ", end="")
            else:
                print("wait ", end="")

            print(f"for {action.action_duration}ms", end="")
            if actions_index < len(macro.actions) - 1 and (macro.actions[actions_index].action_input is not None and macro.actions[actions_index + 1].action_input is not None):
                print_if_not_last_element(actions_index, macro.actions, " and ")
            else:
                print_if_not_last_element(actions_index, macro.actions, " then ")

        if macros_index < len(macros) - 1:
            print()
        print()


def start_macros():
    def find_macro_by_hotkey(provided_hotkey):
        nonlocal macro
        for macro in macros:
            if macro.hotkey == provided_hotkey:  # TODO: fix
                return macro
        return None

    time.sleep(0.1)

    while True:
        pressed_keys = listen_for_inputs()
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
