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


class ActionType(Enum):
    WAIT = 'wait'
    CLICK = 'click'
    KEY = 'press'


class Action:
    def __init__(self, action_type, duration=None, input_code=None, mouse_coordinates=None):
        self.action_type = action_type
        self.duration = duration
        self.input_code = input_code
        self.mouse_coordinates = mouse_coordinates

    def run(self):
        duration = self.duration / 1000

        if self.action_type == ActionType.WAIT:
            time.sleep(duration)

        elif self.action_type == ActionType.CLICK:
            if self.mouse_coordinates is not None:
                mouse_controller.position = self.mouse_coordinates
            mouse_controller.press(self.input_code)
            time.sleep(duration)
            mouse_controller.release(self.input_code)

        elif self.action_type == ActionType.KEY:
            keyboard_controller.press(self.input_code)
            time.sleep(duration)
            keyboard_controller.release(self.input_code)


class Macro:
    def __init__(self, hotkey, actions):
        self.hotkey = hotkey
        self.actions = actions
        self.running = False
        self.thread = None

    def run(self):
        while self.running:
            for action in self.actions:
                action.run()

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()

    def toggle(self):
        if self.running:
            self.stop()
        else:
            self.start()
