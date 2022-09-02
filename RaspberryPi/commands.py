

def exec_command(box, cmd):
    if cmd == 'left_light_on':
        box.left_light.on()
    elif cmd == 'right_light_on':
        box.right_light.on()
    elif cmd == 'food_light_on':
        box.food_light.on()
    elif cmd == 'view_light_on':
        box.view_light.on()
    elif cmd == 'house_light_on':
        box.house_light.on()
    elif cmd == 'view_light_off':
        box.view_light.off()
    elif cmd == 'house_light_off':
        box.house_light.off()
    elif cmd == 'right_light_off':
        box.right_light.off()
    elif cmd == 'left_light_off':
        box.left_light.off()
    elif cmd == 'food_light_off':
        box.food_light.off()
    elif cmd == 'left_light_blink':
        box.left_light.blink(n=1)
    elif cmd == 'right_light_blink':
        box.right_light.blink(n=1)
    elif cmd == 'food_light_blink':
        box.food_light.blink(n=1)
    elif cmd == 'view_light_blink':
        box.view_light.blink(n=1)
    elif cmd == 'house_light_blink':
        box.house_light.blink(n=1)
    elif cmd == 'dispense_pellet':
        box.dispense_pellet()
    elif cmd.split(':')[0] == 'start_video':
        box.start_video('/home/pi/Desktop/operant/videos/{c}.h264'.format(c=cmd.split(':')[1]), 
                        '/home/pi/Desktop/operant/videos/{c}_timestamps.csv'.format(c=cmd.split(':')[1]))
    elif cmd == 'stop_video':
        box.stop_video()