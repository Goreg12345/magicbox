import queue
import socket
import time

import select


MSGLEN = 64


class Box:
    def __init__(self, box_number, port=3002):
        print('Opening socket...')
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f'Waiting for box {box_number} to connect...')
        self.s.connect((socket.gethostbyname(f'raspberrypi{box_number}'), port))
        print(f'Box {box_number} successfully connected!')

        # to enable sending and receiving at the same time in different threads
        # see https://stackoverflow.com/questions/51104534/python-socket-receive-send-multi-threading
        self.queue = queue.Queue()
        self.rsock, self.ssock = socket.socketpair()
        self.listener_started = False

    def listen_for_events(self, method, timeout_s=45*60):
        self.listener_started = True
        start = time.time()
        while time.time() - start < timeout_s:
            rlist, _, _ = select.select([self.s, self.rsock], [], [])
            for ready_socket in rlist:
                if ready_socket is self.s:
                    message = self.s.recv(MSGLEN)
                    message = message.replace(b' ', b'')
                    if message == b'':
                        print('connection terminated')
                        break
                    elif message:
                        method(*message.decode().split('-'))
                else:
                    self.rsock.recv(1)
                    self.s.send(self.queue.get())
        print('Stop listening')
        self.listener_started = False

    def __del__(self):
        self.stop_video_capture()
        self.disconnect()
        self.s.close()

    def send(self, msg):
        fillin = MSGLEN - len(msg)
        msg += b' ' * fillin
        if self.listener_started:
            self.queue.put(msg)
            self.ssock.send(b"\x00")
        else:
            self.s.sendall(msg)

    def left_light_on(self):
        self.send(b'left_light_on')

    def right_light_on(self):
        self.send(b'right_light_on')

    def food_light_on(self):
        self.send(b'food_light_on')

    def view_light_on(self):
        self.send(b'view_light_on')

    def house_light_on(self):
        self.send(b'house_light_on')

    def left_light_off(self):
        self.send(b'left_light_off')

    def right_light_off(self):
        self.send(b'right_light_off')

    def food_light_off(self):
        self.send(b'food_light_off')

    def view_light_off(self):
        self.send(b'view_light_off')

    def house_light_off(self):
        self.send(b'house_light_off')

    def left_light_blink(self):
        self.send(b'left_light_blink')

    def right_light_blink(self):
        self.send(b'right_light_blink')

    def food_light_blink(self):
        self.send(b'food_light_blink')

    def view_light_blink(self):
        self.send(b'view_light_blink')

    def house_light_blink(self):
        self.send(b'house_light_blink')

    def dispense_pellet(self):
        self.send(b'dispense_pellet')

    def start_video_capture(self, filename):
        self.send('start_video:{f}'.format(f=filename).encode())

    def stop_video_capture(self):
        self.send(b'stop_video')

    def disconnect(self):
        self.send(b'terminate')
