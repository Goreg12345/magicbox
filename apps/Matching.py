import threading

from numpy import random

from core.Logger import Logger
from core.startup_sequence import StartupSequence
from core.transmit import connect_to_box, listen_for_events
from core.functions import *
import time
from pathlib import Path


def get_new_interval(mean, stdev):
    min_cap = mean - 2 * stdev
    max_cap = mean + 2 * stdev
    next_interval = random.normal(mean, stdev)
    if min_cap > next_interval:
        next_interval = min_cap
    elif max_cap < next_interval:
        next_interval = max_cap
    return next_interval


def matching(box_name, mean_ll, stdev_ll, mean_rl, stdev_rl, punishment_s, time_s, log_dir, mouse_name, session=1, startup_sequence=True):

    box = connect_to_box(box_name)

    # samples from a poisson distribution
    logger = Logger(Path(log_dir) / mouse_name)

    next_reward_available = {
        'LL': 0,
        'RL': 0,
    }
    means = {
        'LL': mean_ll,
        'RL': mean_rl
    }
    stdevs = {
        'LL': stdev_ll,
        'RL': stdev_rl
    }
    last_lever = None

    if startup_sequence:
        # give the undergrad a hint where to put the mouse
        startup = StartupSequence(box, box_name, mouse_name)

    def on_event(event, pi_timestamp):
        nonlocal startup_sequence
        nonlocal box_name
        nonlocal mouse_name
        nonlocal next_reward_available
        nonlocal session
        nonlocal last_lever

        if event != 'LL' and event != 'RL': return

        if startup_sequence:
            startup_sequence = startup.handle(event)
            if not startup_sequence:
                start_video_capture(box, '{m}_{s}'.format(m=mouse_name, s=session))
                logger.log_event(mouse_name, 'video_start', -1)

                for lever in ['LL', 'RL']:
                    new_interval = get_new_interval(means[lever], stdevs[lever])
                    next_reward_available[lever] = time.time() + new_interval
                    logger.log_event(mouse_name, f'next_interval_{lever}-{new_interval}', pi_timestamp)

                return

        if not last_lever:
            last_lever = event
        elif last_lever != event:
            next_reward_available[event] += punishment_s
            logger.log_event(mouse_name, f'punishment_{event}', pi_timestamp)
        last_lever = event

        if not startup_sequence:
            logger.log_event(mouse_name, event, pi_timestamp)
            if time.time() > next_reward_available[event]:
                dispense_pellet(box)
                logger.log_event(mouse_name, 'FD', pi_timestamp)
                new_interval = get_new_interval(means[event], stdevs[event])
                next_reward_available[event] = time.time() + new_interval
                logger.log_event(mouse_name, f'next_interval-{new_interval}', pi_timestamp)

    listen_for_events(box, on_event, time_s)
    stop_video_capture(box)
    logger.log_event(mouse_name, 'video_stop', -1)
    disconnect(box)
    box.close()


if __name__ == '__main__':
    t = threading.Thread(target=matching, args=['box_7', 90, 10, 30, 5, 5, 1800, r'C:\Users\FED3\Desktop\DATA\Federico', 'B1677', 6, True])
    t.start()

    t = threading.Thread(target=matching, args=['box_8', 90, 10, 30, 5, 5, 1800, r'C:\Users\FED3\Desktop\DATA\Federico', 'B1577', 6, True])
    t.start()

    t = threading.Thread(target=matching, args=['box_9', 90, 10, 30, 5, 5, 1800, r'C:\Users\FED3\Desktop\DATA\Federico', 'B1623', 6, True])
    t.start()
