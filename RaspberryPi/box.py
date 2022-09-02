# -*- coding: utf-8 -*-
import gpiozero as io
from picamera import PiCamera
import CameraEncoder


## settings
feeder_trig_pulse=.05  # trigger pulse duration for feeder in ms
digout_active_high=True # for LEDs, rev v2.09 
feeder_active_high=False # for feeder
lever_pull_up=True  #  v2.02

bounce_s=.05
pull_up=True




## get dev code form dev pin, dictionary for device code based in pin number
Devices={
    0: 'P0', # program code
    1: 'P1', # program code
    4: 'TS', # temp sensor
    5: 'LB', # left bulb
    6: 'RB', # right bulb
    7: 'T1', # timer 1
    8: 'T2', # timer 2
    9: 'T3', # timer 3  
    12: 'SI', # sync_in
    13: 'FB', # feeder bulb
    16: 'WH', # wheel
    17: 'LP', # left lever power, pin 11, v2.00
    18: 'RP', # right lever power pin 12, v2.00
    19: 'HB', # house bulb
    20: 'LL', # left lever
    21: 'RL', # right lever
    22: 'SO', # sync_out
    23: 'ST', # v1.07 Session Timer, just for an object, the pin is not actuallly used
    24: 'IT', # v1.07 Interval Timer, just for an object, the pin is not actuallly used
    26: 'FD', # food dispenser
    27: 'VB'  # viewing bulb 
    }

# get dev pin from dev code, inverse mapping for Devices
Pins={v:k for k,v in Devices.items()}

box = None
n_listeners = 0

def make_new_box():
    global box
    global n_listeners
    n_listeners += 1
    if box:
        # if multiple clients control the box at the same time, make sure to yield the
        # same box, otherwise, you get a gpio not accessible error!
        return box
    else:
        box = Box()
        return box
        
    
def close_box():
    global box
    global n_listeners
    n_listeners -= 1
    
    # delete if there is no client anymore who wants the box
    # this frees the gpio pins such that other programs, e.g. the old GUI or launcher can still run in parallel
    if not n_listeners:
        box.__del__()
        box = None


class Box(object):

    def __init__(self):
        self.feeder = io.LED(Pins['FD'], feeder_active_high,True)
        self.food_light = io.LED(Pins['FB'],digout_active_high,False)
        self.left_light = io.LED(Pins['LB'],digout_active_high,False)
        self.right_light = io.LED(Pins['RB'],digout_active_high,False)
        self.house_light = io.LED(Pins['HB'],digout_active_high,False)
        self.view_light = io.LED(Pins['VB'],digout_active_high,False)

        self.camera = PiCamera()

        self.ll = io.Button(20, pull_up=pull_up, bounce_time = bounce_s)
        self.rl = io.Button(21, pull_up=pull_up, bounce_time = bounce_s)

    def dispense_pellet(self):
        self.feeder.blink(feeder_trig_pulse,0,1)

    def start_video(self, video_name, log_name):
        self.camera.resolution = (CameraEncoder.WIDTH, CameraEncoder.HEIGHT)
        self.camera.framerate=CameraEncoder.FPS
        self.camera.start_preview()
        self.video_writer = CameraEncoder.CameraEncoder(video_name, log_name)
        self.camera.start_recording(self.video_writer, format='h264')

    def stop_video(self):
        self.camera.stop_recording()
        self.camera.stop_preview()

    def __del__(self):
        print('box deleted')
        self.feeder.close()
        self.food_light.close()
        self.left_light.close()
        self.right_light.close()
        self.house_light.close()
        self.view_light.close()
        self.camera.close()
        self.ll.close()
        self.rl.close()
