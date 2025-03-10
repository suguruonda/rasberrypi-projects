import RPi.GPIO as GPIO
from capture_360images import Camerastage 
from time import sleep
p = Camerastage(False)
p.set_motor_direction(True)
pitch = 32
#p.change_step_pitch("1/" + str(pitch))
#print(p.step_count)

try:

    """
    one_step = int(pitch/1)
    start_list = []
    end_list = []
    for j in range(10):
        start = 0
        flag = False
        end = 0
        for i in range(int(p.step_count/one_step)):
            p.rotate_stage(one_step)
            if(p.hallsensor() == True) and not(flag):
                start = i
                flag = True
            if (p.hallsensor() == False) and flag:
                end = i
                flag = False
        start_list.append(start)
        end_list.append(end)
        sleep(1)
        
    print(start_list)
    print(end_list)

    
    one_step = int(pitch/1)

    loc = 0
    while True:
        current_position = p.hallsensor()
        p.rotate_stage(one_step)
        next_position = p.hallsensor()   
        loc += 1
        if current_position == True and next_position == False:
            break


    print(loc)
    """
    #p.softbox_SW_ALL(True)
    for i in range(10):
        p.set_motor_initial_position()
        sleep(1)
    GPIO.cleanup()
except KeyboardInterrupt:
    print('interrupted!')
    GPIO.cleanup()








