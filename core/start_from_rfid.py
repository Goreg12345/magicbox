import json
import threading
import time
from ast import literal_eval
from json import JSONDecodeError

import pandas as pd

from apps.FlexRatio import flex_ratio
from apps.FlexTime import flex_time
from apps.FlexRatioReversed import flex_ratio_reversed
from apps.changing_probabilities import changing_probabilities
from transmit import read_rfid_tag
from apps.TimeSchedule import time_schedule
from apps.FixRatioSurprise import fix_ratio_surprise


def main(batch):
    exp_config = pd.read_csv(r'../cdat_config.csv', delimiter=';')  #r'C:\Users\Georg\OneDrive - City University of New York\0 '
                             #r'Research\data\cdat_PR\cdat_config.csv', delimiter=';').dropna()
    batch = exp_config[(exp_config.batch == batch) & (~exp_config.is_done.astype(bool))]
    batch = batch[batch.session == min(batch.session)]
    while ~batch.is_done.all():
        print('reading tag...')
        rfid = read_rfid_tag().replace('=', ':').replace("'", '"')
        print(rfid)
        try:
            current_mouse = json.loads(rfid)
        except JSONDecodeError:
            print('read unsuccessful, reading again')
            continue

        cur_cfg = batch[batch.mouse_name == current_mouse['mouse']]
        if batch[batch.mouse_name == current_mouse['mouse']].is_done.all():
            continue
        print('new mouse, starting program')
        batch.loc[batch.mouse_name == current_mouse['mouse'], 'is_done'] = 1
        if batch.loc[batch.mouse_name == current_mouse['mouse'], 'program'].iloc[0] == 'flex_ratio':
            t = threading.Thread(target=flex_ratio, args=cur_cfg.args.apply(literal_eval).iloc[0])
        elif batch.loc[batch.mouse_name == current_mouse['mouse'], 'program'].iloc[0] == 'flex_time':
            t = threading.Thread(target=flex_time, args=cur_cfg.args.apply(literal_eval).iloc[0])
        elif batch.loc[batch.mouse_name == current_mouse['mouse'], 'program'].iloc[0] == 'flex_ratio_reversed':
            t = threading.Thread(target=flex_ratio_reversed, args=cur_cfg.args.apply(literal_eval).iloc[0])
        elif batch.loc[batch.mouse_name == current_mouse['mouse'], 'program'].iloc[0] == 'time_schedule':
            t = threading.Thread(target=time_schedule, args=cur_cfg.args.apply(literal_eval).iloc[0])
        elif batch.loc[batch.mouse_name == current_mouse['mouse'], 'program'].iloc[0] == 'fix_ratio_surprise':
            t = threading.Thread(target=fix_ratio_surprise, args=cur_cfg.args.apply(literal_eval).iloc[0])
        else:
            t = threading.Thread(target=changing_probabilities, args=cur_cfg.args.apply(literal_eval).iloc[0])
        t.start()
        time.sleep(1)   # to prevent multiple tag reads
    print('all boxes started')


if __name__ == '__main__':
    main(1)
