from core.observers.AbstractObserver import AbstractObserver
from time import sleep
import json


class CommandObserver(AbstractObserver):

    def __init__(self):
        super().__init__()
        self.keyboard = self.make_keyboard()

    def group(self, iterable, count): 
        return 

    def make_keyboard(self, one_time=False, columns=2):
        buttons = []
        cmds = self.commands.copy()
        counter = 0
        temp_arr = []
        while cmds:
            temp_arr.append(cmds.pop(0).keyboard)
            counter += 1
            if counter == columns or len(cmds) < columns:
                buttons.append(temp_arr.copy())
                temp_arr.clear()
                counter = 0

        keyboard = {
            'one_time': one_time,
            'buttons': buttons
        }     
        self.keyboard = json.dumps(keyboard)
        print(keyboard)
        return self.keyboard

    def execute(self, user_id, message, attachments, group, **kwargs):
        
        button = kwargs['payload']['button']
        if not button: return
        for command in self.commands:
            if command.trigger == button:
                group.api.messages.setActivity(user_id=user_id, type="typing")
                
                if command.system:
                    kwargs.update({"commands": self.commands})

                return command.proceed(user_id, message, attachments, group, keyboard=self.keyboard, **kwargs)