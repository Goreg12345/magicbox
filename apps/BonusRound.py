import threading

from numpy import random

from core.Logger import Logger
from core.box import Box
import time
from pathlib import Path


def get_new_interval(mean, stdev, cap):
    min_cap = mean - cap * stdev
    max_cap = mean + cap * stdev
    next_interval = random.normal(mean, stdev)
    if min_cap > next_interval:
        next_interval = min_cap
    elif max_cap < next_interval:
        next_interval = max_cap
    return next_interval


def get_new_schedule(min, max):
    return random.uniform(min, max)


def bonus_round(box_number, schedules, active_lever, cap, time_s, log_dir, mouse_name, session=1, startup_sequence=False):

    box = Box(box_number)

    # samples from a poisson distribution
    logger = Logger(Path(log_dir) / mouse_name)

    current_schedule = 0
    last_schedule = 0
    schedule_start = time.time()

    next_reward_s = get_new_interval(schedules[current_schedule]['mean'], schedules[current_schedule]['stdev'], cap)
    next_reward_available = time.time() + next_reward_s
    logger.log_event(mouse_name, f'next_interval-{next_reward_s}', -1)

    box.start_video_capture('{m}_{s}'.format(m=mouse_name, s=session))
    logger.log_event(mouse_name, 'video_start', -1)

    def on_event(event, pi_timestamp):
        nonlocal startup_sequence
        nonlocal mouse_name
        nonlocal next_reward_available
        nonlocal session
        nonlocal current_schedule
        nonlocal box
        nonlocal last_schedule

        if event != 'LL' and event != 'RL': return

        logger.log_event(mouse_name, event, pi_timestamp)
        if event == active_lever:
            if last_schedule != current_schedule:
                last_schedule = current_schedule
                next_reward_s = get_new_interval(schedules[current_schedule]['mean'], schedules[current_schedule]['stdev'], cap)
                next_reward_available = schedule_start + next_reward_s
                logger.log_event(mouse_name, f'next_interval-{next_reward_s}', -1)

            if next_reward_available < time.time():
                box.dispense_pellet()
                box.food_light_blink()
                logger.log_event(mouse_name, 'FD', pi_timestamp)

                next_reward_s = get_new_interval(schedules[current_schedule]['mean'],
                                                 schedules[current_schedule]['stdev'], cap)
                next_reward_available = time.time() + next_reward_s
                logger.log_event(mouse_name, f'next_interval-{next_reward_s}', -1)

    threading.Thread(target=box.listen_for_events, args=[on_event, time_s]).start()

    start_time = time.time()
    while time.time() < start_time + time_s:
        new_schedule = get_new_schedule(schedules[current_schedule]['min'], schedules[current_schedule]['max'])
        if time.time() + new_schedule > start_time + time_s:
            new_schedule = start_time + time_s - time.time()
        logger.log_event(mouse_name, f'next_schedule-{new_schedule}', -1)
        time.sleep(new_schedule)
        if current_schedule % 2:
            box.house_light_off()
            print('light_off')
        else:
            box.house_light_on()
            print('light_on')
        current_schedule += 1
        if current_schedule == len(schedules):
            current_schedule = 0
        schedule_start = time.time()

    box.house_light_off()
    logger.log_event(mouse_name, 'video_stop', -1)


if __name__ == '__main__':
    t = threading.Thread(target=bonus_round, args=[4, [
        {
            'mean': 6,
            'stdev': 1,
            'min': 12,
            'max': 16
        },
        {
            'mean': 6,
            'stdev': 1,
            'min': 16,
            'max': 20
        }
    ], "RL", 2, 60, r'', 'B1677', 1, False])
    t.start()
