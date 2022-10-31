import socket
import time


MSGLEN = 64

rfid_host = '149.4.217.23' #socket.gethostbyname('raspberrypi15')  # 192.168.0.115'
rfid_port = 3001

host_names = {
    'box_1': socket.gethostbyname('raspberrypi1'),
    'box_2': socket.gethostbyname('raspberrypi2'),
    'box_3': socket.gethostbyname('raspberrypi3'),
    'box_4': socket.gethostbyname('raspberrypi4'),
    'box_5': socket.gethostbyname('raspberrypi5'),
    'box_6': socket.gethostbyname('raspberrypi6'),
    'box_7': socket.gethostbyname('raspberrypi7'),
    'box_8': socket.gethostbyname('raspberrypi8'),
    'box_9': socket.gethostbyname('raspberrypi9'),
    'box_10': socket.gethostbyname('raspberrypi10'),
    'box_11': socket.gethostbyname('raspberrypi11'),
    'box_12': socket.gethostbyname('raspberrypi12'),

}
port_names = {
    'box_1': 3002,
    'box_2': 3002,
    'box_3': 3002,
    'box_4': 3002,
    'box_5': 3002,
    'box_6': 3002,
    'box_7': 3002,
    'box_8': 3002,
    'box_9': 3002,
    'box_10': 3002,
    'box_11': 3002,
    'box_12': 3002,

}


def connect_to_box(box_name, port=None):
    if not port:
        port = port_names[box_name]
    print('Opening socket...')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print('Waiting for {b} to connect...'.format(b=box_name))
    s.connect((host_names[box_name], port))
    print('{b} successfully connected!'.format(b=box_name))
    return s


def listen_for_events(box, method, timeout_s=45*60):
    start = time.time()
    while time.time() - start < timeout_s:
        message = box.recv(MSGLEN)
        message = message.replace(b' ', b'')
        if message == b'':
            print('connection terminated')
            break
        elif message:
            method(*message.decode().split('-'))


def read_rfid_tag():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((rfid_host, rfid_port))
        return s.recv(MSGLEN).decode()

