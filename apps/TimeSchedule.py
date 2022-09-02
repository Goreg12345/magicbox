import threading

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


def time_schedule(box_name, schedule, time_s, log_dir, mouse_name, session=1, startup_sequence=True):

    box = connect_to_box(box_name)
    bonsai_sender = SimpleUDPClient(ip, port)

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
            nonlocal session

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


                    startup_sequence = False
                return

            timestamp = time.time()
            datetimestamp = str(datetime.now())
            print(box_name, mouse_name, event)
            log_writer.writerow([mouse_name, event, pi_timestamp, timestamp, datetimestamp])
            bonsai_sender.send_message('/flexratio', f'{mouse_name},{event},{pi_timestamp},{timestamp},{datetimestamp}')


        t = threading.Thread(target=listen_for_events, args=(box, on_event, time_s))
        t.start()
        start = time.time()
        print(schedule)
        for next_reward in schedule:
            time.sleep(next_reward)
            timestamp = time.time()
            datetimestamp = str(datetime.now())
            dispense_pellet(box)
            food_light_blink(box)
            print('FD', box_name)
            log_writer.writerow([mouse_name, 'FD', -1, time.time(), datetime.now()])
            bonsai_sender.send_message('/flexratio', f'{mouse_name},"FD", -1,{timestamp},{datetimestamp}')

        stop_video_capture(box)
        log_writer.writerow([mouse_name, 'video_stop', -1, time.time(), datetime.now()])
        bonsai_sender.send_message('/flexratio', f'{mouse_name},"video_stop",-1,{time.time()},{datetime.now()}')
        disconnect(box)
        box.close()


if __name__ == '__main__':
    time_schedule('box_4', [2,2,8,2], 60, '', 'B1234')
