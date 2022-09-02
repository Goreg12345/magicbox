MSGLEN = 64


def send(box, msg):
    fillin = MSGLEN - len(msg)
    msg += b' ' * fillin
    box.send(msg)
    
def left_light_on(box):
    send(box, b'left_light_on')
def right_light_on(box):
    send(box, b'right_light_on')
def food_light_on(box):
    send(box, b'food_light_on')
def view_light_on(box):
    send(box, b'view_light_on')
def house_light_on(box):
    send(box, b'house_light_on')
def left_light_off(box):
    send(box, b'left_light_off')
def right_light_off(box):
    send(box, b'right_light_off')
def food_light_off(box):
    send(box, b'food_light_off')
def view_light_off(box):
    send(box, b'view_light_off')
def house_light_off(box):
    send(box, b'house_light_off')
def left_light_blink(box):
    send(box, b'left_light_blink')
def right_light_blink(box):
    send(box, b'right_light_blink')
def food_light_blink(box):
    send(box, b'food_light_blink')
def view_light_blink(box):
    send(box, b'view_light_blink')
def house_light_blink(box):
    send(box, b'house_light_blink')
def dispense_pellet(box):
    send(box, b'dispense_pellet')
def start_video_capture(box, filename):
    send(box, 'start_video:{f}'.format(f=filename).encode())
def stop_video_capture(box):
    send(box, b'stop_video')
def disconnect(box):
    send(box, b'terminate')
