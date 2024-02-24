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
                if action.action_type == Action.Type.WAIT:
                    time.sleep(action_duration)
                elif action.action_type == Action.Type.KEY:
                    keyboard_controller.press(action.action_input)
                    time.sleep(action_duration)
                    keyboard_controller.release(action.action_input)
                elif action.action_type == Action.Type.CLICK:
                    if action.click_coordinates:
                        mouse_controller.position = (action.click_coordinates[0], action.click_coordinates[1])
                    mouse_controller.press(action.action_input)
                    time.sleep(action_duration)
                    mouse_controller.release(action.action_input)


class Action:
    class Type(Enum):
        WAIT = 'wait'
        KEY = 'hold'
        CLICK = 'click'

    def __init__(self, action_type, action_duration=None, action_input=None, click_coordinates=None):
        self.action_type = action_type
        self.action_duration = action_duration
        self.action_input = action_input
        self.click_coordinates = click_coordinates
