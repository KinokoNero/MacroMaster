from enum import Enum


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


class Action:
    class Type(Enum):
        WAIT = 'wait'
        KEY = 'hold'

    def __init__(self, action_type, action_duration, action_key=None):
        self.action_type = action_type
        self.action_duration = action_duration
        self.action_key = action_key