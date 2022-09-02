import time

from core.functions import left_light_on, right_light_on, food_light_on, left_light_off, right_light_off, \
    food_light_off, left_light_blink, right_light_blink, food_light_blink


class StartupSequence:
    def __init__(self, box, box_name, mouse_name):
        left_light_on(box)
        right_light_on(box)
        food_light_on(box)
        self.rl_startup = False
        self.ll_startup = False
        self.box = box
        self.box_name = box_name
        self.mouse_name = mouse_name

    def handle(self, event):
        # require to press both levers to make sure they work
        if event == 'LL':
            self.ll_startup = True
            left_light_off(self.box)
        elif event == 'RL':
            self.rl_startup = True
            right_light_off(self.box)
        if self.ll_startup and self.rl_startup:
            print(f'Box {self.box_name} started!')
            food_light_off(self.box)
            time.sleep(1)
            for _ in range(2):
                left_light_blink(self.box)
                right_light_blink(self.box)
                food_light_blink(self.box)
                time.sleep(2)
            return False
        return True
