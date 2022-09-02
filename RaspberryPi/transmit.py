# -*- coding: utf-8 -*-
import socket
import time
import threading
from box import make_new_box, close_box
import select
import queue
from commands import exec_command
import os


out = os.popen('hostname -I')
HOST = out.read().replace(' \n', '')
PORT = 3002

MSGLEN = 64  # we can simply use a fixed-length protocoll as the amount of data is marginal

#time.sleep(8) # to make sure the wifi connection is established


def execute_client_commands(clientsocket):
    send_queue = queue.Queue()
    rsock, ssock = socket.socketpair()

    box = make_new_box()

    def lever_callback(event):
            print(event)
            msg = '{event}-{timestamp}'.format(event=event, timestamp=str(time.time())).encode()
            fillin = MSGLEN - len(msg)
            msg += b' ' * fillin
            send_queue.put(msg)
            ssock.send(b'\x00')  # tell clientsocket to send data

    box.ll.when_activated = lambda: lever_callback('LL')
    box.rl.when_activated = lambda: lever_callback('RL')
    print('receiving commands...')

    # listen to commands
    while True:
        rlist, _, _ = select.select([clientsocket, rsock], [], [])
        for ready_socket in rlist:
            if ready_socket is clientsocket:
                message = clientsocket.recv(MSGLEN)
                message = message.replace(b' ', b'')
                if message == b'':
                    print('Connection Terminated!')
                    close_box() # make absolutely sure box gets deleted to give pins and camera free to whoever uses them nex
                    return
                if 'terminate' in message.decode():
                    close_box()
                    print('connection terminated')
                    return
                print(message.decode())
                exec_command(box, message.decode())
            else:
                rsock.recv(1)
                clientsocket.sendall(send_queue.get())
        

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serversocket:
        print('Opening socket...')
        
        serversocket.bind((HOST, PORT))
        serversocket.listen()
        print('Server is listening at {h} : {p} !'.format(h=HOST, p=PORT))
        while True:
            clientsocket, addr = serversocket.accept()
            t = threading.Thread(target=execute_client_commands, args=(clientsocket,))
            t.start()
        
            print('successful connection established with client')

    
if __name__ == '__main__':
    main()
