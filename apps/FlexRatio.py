from core.transmit import connect_to_box, listen_for_events
import csv
from core.functions import *
import time
from datetime import datetime
from pathlib import Path
import pytz
from pythonosc.udp_client import SimpleUDPClient

ip = '127.0.0.1'
port = 2342


def flex_ratio(box_name, initial, progressive, time_s, log_dir, mouse_name, session=1, light_on_lever=False, startup_sequence=True, active_lever='LL'):
    if initial < 1:
        raise Exception(m='initial must be at least 1!')
    state = {
        'active_lever_presses': 0,
        'next_reward': initial
    }

    box = connect_to_box(box_name)
    bonsai_sender = SimpleUDPClient(ip, port)

    with open(Path(log_dir) / '{m}_{p}_{s}.log'.format(m=mouse_name, p=progressive, s=session), 'w', newline='') as f:
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
            nonlocal progressive
            nonlocal session
            nonlocal light_on_lever
            nonlocal bonsai_sender


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
                    start_video_capture(box, '{m}_{p}_{s}'.format(m=mouse_name, p=progressive, s=session))
                    bonsai_sender.send_message('/flexratio', f'{mouse_name},"video_start",-1,{time.time()},{str(datetime.now(pytz.utc))}')

                    startup_sequence = False
                return

            timestamp = time.time()
            datetimestamp = str(datetime.now())
            print(box_name, mouse_name, event)
            log_writer.writerow([mouse_name, event, pi_timestamp, timestamp, datetimestamp])
            bonsai_sender.send_message('/flexratio', f'{mouse_name},{event},{pi_timestamp},{timestamp},{datetimestamp}')

            if event == active_lever:
                state['active_lever_presses'] += 1
                if state['active_lever_presses'] == state['next_reward']:
                    dispense_pellet(box)
                    food_light_blink(box)
                    log_writer.writerow([mouse_name, 'FD', pi_timestamp, timestamp, datetimestamp])
                    bonsai_sender.send_message('/flexratio', f'{mouse_name},"FD",{pi_timestamp},{timestamp},{datetimestamp}')
                    state['active_lever_presses'] = 0
                    state['next_reward'] += progressive
            if light_on_lever:
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
    flex_ratio('box_4', 2, 0, 30, '', 'B1234', 1, True)

