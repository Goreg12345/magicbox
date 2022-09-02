import socket

import time
from pythonosc.udp_client import SimpleUDPClient
from datetime import datetime


FPS = 30
WIDTH = 640
HEIGHT = 480


class CameraEncoder:

    def __init__(self, vid_name, log_name, udp_hostname='DESKTOP-AEG7FUV'):
        ip = '149.4.217.18'
        port = 2342
        self.bonsai_sender = SimpleUDPClient(ip, port)  # Create client to send timestmaps to bonsai
        self.address = '/{hostname}/video'.format(hostname=socket.gethostname())
        self.writer = open(vid_name, 'wb')
        self.logger = open(log_name, 'w')
        self.time_last_frame = 0
        self.frame_counter = 0

    def write(self, frame):
        self.writer.write(frame)

        t = time.time()
        if t - self.time_last_frame > (FPS/1000 - FPS/5000): # sometimes this method gets called although no new frame was written
            self.frame_counter += 1
            self.logger.write(f'{t}\n')

            # send udp message to bonsai to synchronize the video timestamps with photometry
            self.time_last_frame = t
            self.bonsai_sender.send_message(self.address, '{f},{t},{d}'.format(f=self.frame_counter, t=t, d=datetime.now()))

    def flush(self):
        self.writer.close()
        self.logger.close()
