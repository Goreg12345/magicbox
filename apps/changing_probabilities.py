import random

from core.transmit import connect_to_box, listen_for_events
import csv
from core.functions import *
import time
from datetime import datetime
from pathlib import Path
from pythonosc.udp_client import SimpleUDPClient
import pytz

ip = '127.0.0.1'
port = 2342

def changing_probabilities(box_name, min_time, max_time, high_prob, low_prob, time_s, log_dir, mouse_name, session=1, startup_sequence=True):
    state = {
        'LL': 0,  # prob of reward
        'RL': 0,
        'time_started': .0,
        'time_to_change': random.randint(min_time, max_time)
    }

    box = connect_to_box(box_name)
    bonsai_sender = SimpleUDPClient(ip, port)

    timeout = 5  # number of seconds there will be no pellet after pellet delivery: to ensure we don't get multiple rewards at the same time (will clog the food port and makes interpretation difficult
    last_pellet = time.time()

    with open(Path(log_dir) / '{m}_{s}.log'.format(m=mouse_name, s=session), 'w', newline='') as f:
        log_writer = csv.writer(f)
        log_writer.writerow(['mouse', 'event', 'pi_timestamp', 'pc_timestamp', 'datetimestamp'])
        if startup_sequence:
            # give the undergrad a hint where to put the mouse
            left_light_on(box)
            right_light_on(box)
            food_light_on(box)
            rl_startup = False
            ll_startup = False

        def on_event(event, pi_timestamp):
            nonlocal startup_sequence
            nonlocal box_name
            nonlocal mouse_name
            nonlocal log_writer
            nonlocal rl_startup
            nonlocal ll_startup
            nonlocal state
            nonlocal session
            nonlocal min_time
            nonlocal max_time
            nonlocal high_prob
            nonlocal low_prob
            nonlocal bonsai_sender
            nonlocal timeout
            nonlocal last_pellet

            if event != 'LL' and event != 'RL': return

            if startup_sequence:
                # require to press both levers to make sure they work
                if event == 'LL':
                    ll_startup = True
                    left_light_off(box)
                elif event == 'RL':
                    rl_startup = True
                    right_light_off(box)
                if ll_startup and rl_startup:
                    print(f'Box {box_name} started!')
                    food_light_off(box)
                    time.sleep(1)
                    for _ in range(2):
                        left_light_blink(box)
                        right_light_blink(box)
                        food_light_blink(box)
                        time.sleep(2)

                    log_writer.writerow([mouse_name, 'video_start', -1, time.time(), datetime.now()])
                    start_video_capture(box, '{m}_{s}'.format(m=mouse_name, s=session))
                    bonsai_sender.send_message('/flexratio', f'{mouse_name},"video_start",-1,{time.time()},{str(datetime.now(pytz.utc))}')

                    # setup starting probabilities
                    state['time_started'] = time.time()
                    if random.random() > .5:
                        state['LL'] = high_prob
                        state['RL'] = low_prob
                    else:
                        state['LL'] = low_prob
                        state['RL'] = high_prob

                    startup_sequence = False
                return

            timestamp = time.time()
            datetimestamp = str(datetime.now())

            # check whether schedule needs to be changed
            if time.time() - state['time_started'] > state['time_to_change']:
                state['LL'], state['RL'] = state['RL'], state['LL']
                state['time_to_change'] = random.randint(min_time, max_time)
                state['time_started'] = time.time()
                log_writer.writerow([mouse_name, 'P_LL={ll}_RL={rl}'.format(ll=state['LL'], rl=state['RL']), pi_timestamp, timestamp, datetimestamp])
                bonsai_sender.send_message('/flexratio', f'{mouse_name},P_LL={state["LL"]}_RL={state["RL"]},{pi_timestamp},{timestamp},{datetimestamp}')

                print('P_LL={ll}_RL={rl}'.format(ll=state['LL'], rl=state['RL']))
                print(f'{box_name}, P(LL) = {state["LL"]}, P(RL) = {state["RL"]}, next change in {state["time_to_change"]} seconds')
            log_writer.writerow([mouse_name, event, pi_timestamp, timestamp, datetimestamp])
            bonsai_sender.send_message('/flexratio', f'{mouse_name},{event},{pi_timestamp},{timestamp},{datetimestamp}')


            give_reward = True if random.random() < state[event] and time.time() - last_pellet > timeout else False
            if give_reward:
                dispense_pellet(box)
                food_light_blink(box)
                log_writer.writerow([mouse_name, 'FD', pi_timestamp, timestamp, datetimestamp])
                bonsai_sender.send_message('/flexratio', f'{mouse_name},"FD",{pi_timestamp},{timestamp},{datetimestamp}')
                print(box_name, mouse_name, event, 'food dispensed!')
                last_pellet = time.time()
            else:
                print(box_name, mouse_name, event)

                if event == 'LL':
                    left_light_on(box)
                    time.sleep(0.01)
                    left_light_off(box)
                if event == 'RL':
                    right_light_on(box)
                    time.sleep(0.01)
                    right_light_off(box)

        listen_for_events(box, on_event, time_s)
        stop_video_capture(box)
        bonsai_sender.send_message('/flexratio', f'{mouse_name},"video_stop",-1,{time.time()},{datetime.now()}')
        log_writer.writerow([mouse_name, 'video_stop', -1, time.time(), datetime.now()])
        disconnect(box)
        box.close()


if __name__ == '__main__':
    changing_probabilities('box_11', 5, 15, .90, .10, 30, '', 'B1234')

