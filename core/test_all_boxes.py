import time

from core import transmit
import numpy as np
from core.functions import *


def main():
    for box_num in np.arange(12) + 1:
        box_name = f'box_{str(box_num)}'
        b = transmit.connect_to_box(box_name)
        left_light_on(b)
        right_light_on(b)
        food_light_on(b)
        view_light_on(b)
        dispense_pellet(b)
        time.sleep(2)
        left_light_off(b)
        right_light_off(b)
        food_light_off(b)
        view_light_off(b)
        dispense_pellet(b)
        start_video_capture(b, 'box_test')
        time.sleep(2)
        stop_video_capture(b)


if __name__ == '__main__':
    main()
