import threading
import time
from enum import Enum
from pynput.keyboard import Controller

keyboard_controller = Controller()


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
                if action.action_type == Action.Type.WAIT:
                    time.sleep(action.action_duration)
                elif action.action_type == Action.Type.KEY:
                    keyboard_controller.press(action.action_key)
                    time.sleep(action.action_duration)
                    keyboard_controller.release(action.action_key)


class Action:
    class Type(Enum):
        WAIT = 'wait'
        KEY = 'hold'

    def __init__(self, action_type, action_duration, action_key=None):
        self.action_type = action_type
        self.action_duration = action_duration / 1000
        self.action_key = action_key
