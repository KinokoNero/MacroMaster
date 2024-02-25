import threading
import time
from enum import Enum
from pynput.keyboard import Controller as KeyboardController
from pynput.mouse import Controller as MouseController

keyboard_controller = KeyboardController()
mouse_controller = MouseController()


class Command:
    def __init__(self, aliases, description, function):
        self.aliases = aliases
        self.description = description
        self.function = function

    def execute(self):
        self.function()


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

    def run(self):
        while self.running:
            for action in self.actions:
                action_duration = action.action_duration / 1000

                if action.action_input is None:
                    time.sleep(action_duration)

                elif action.action_input.input_source == Input.InputSource.MOUSE:
                    if action.click_coordinates:
                        mouse_controller.position = (action.click_coordinates[0], action.click_coordinates[1])
                    mouse_controller.press(action.action_input)
                    time.sleep(action_duration)
                    mouse_controller.release(action.action_input)

                elif action.action_input.input_source == Input.InputSource.KEYBOARD:
                    keyboard_controller.press(action.action_input)
                    time.sleep(action_duration)
                    keyboard_controller.release(action.action_input)


class Action:
    def __init__(self, action_duration=None, action_input=None):
        self.action_duration = action_duration
        self.action_input = action_input


class Input:  # Represents singular key/button press
    class InputSource(Enum):
        MOUSE = 'mouse'
        KEYBOARD = 'keyboard'

    class InputEvent:
        def __init__(self, input_code, input_coordinates=None):
            self.input_code = input_code
            self.input_coordinates = input_coordinates

        def __hash__(self):
            coordinates_tuple = tuple(self.input_coordinates.items()) if self.input_coordinates else None
            return hash((self.input_code, coordinates_tuple))

        def __eq__(self, other):
            return (self.input_code, self.input_coordinates) == (other.input_code, other.input_coordinates)

    def __init__(self, input_source, input_event):
        self.input_source = input_source
        self.input_event = input_event

    def __hash__(self):
        return hash((self.input_source, self.input_event))

    def __eq__(self, other):
        return (self.input_source, self.input_event) == (other.input_source, other.input_event)
