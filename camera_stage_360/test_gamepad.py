import RPi.GPIO as GPIO
from time import sleep

SW = 5
DIR = 20 #Direction GPIO Pin
STEP = 21 #Step GPIO Pin
CW =1 #Clockwise Rotaion
CCW = 0 #Counterclockwise Rotation
SPR = 200 #Steps per Resolution (360 / 1.8)

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.output(DIR, CW)
GPIO.setup(SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)


MODE = (13,19,26) #Microstep Resolution GPIO Pins
GPIO.setup(MODE, GPIO.OUT)
RESOLUTION = {'Full':(0,0,0),
              'Half':(1,0,0),
              '1/4':(0,1,0),
              '1/8':(1,1,0),
              '1/16':(0,0,1),
              '1/32':(1,0,1)}

RESOLUTION_MICROSTEP = {'Full':1,
                        'Half':2,
                        '1/4':4,
                        '1/8':8,
                        '1/16':16,
                        '1/32':32}

RESOLUTION_MODE = '1/32'

GPIO.output(MODE, RESOLUTION[RESOLUTION_MODE])

step_count = SPR * RESOLUTION_MICROSTEP[RESOLUTION_MODE]
delay = .005 / RESOLUTION_MICROSTEP[RESOLUTION_MODE]

rotation_num = 20


####################################

import threading
import sys
import evdev
from evdev import InputDevice, categorize, ecodes, KeyEvent

devices = [InputDevice(path) for path in evdev.list_devices()]
find_pad = False
for device in devices:
    if 'F310' in device.name:
        dev_path = device.path
        find_pad = True

if not(find_pad):
    print("No gamepad detected")
    sys.exit()

device = InputDevice(dev_path)

class flags():
    def __init__(self):
        self.cw_bool = True
        self.start_bool = False
        self.stop_bool = False

    def cw_true(self):
        if not(self.cw_bool):
            self.cw_bool = True
            GPIO.output(DIR, CW)

    def cw_false(self):
        if self.cw_bool:
            self.cw_bool = False
            GPIO.output(DIR, CCW)

    def onestep(self):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(delay)
        GPIO.output(STEP, GPIO.LOW)
        sleep(delay)

    def readevent(self, code, value):
        if code == 0 and value == 32767:
            self.cw_true()
            self.start_bool = True
        elif code == 0 and value == -32768:
            self.cw_false()
            self.start_bool = True
        elif code == 0 and value == 128:
            self.start_bool = False
        elif code == 315 and value == 1:
            self.stop_bool = True

    def eventloop(self):
        for event in device.read_loop():
            self.readevent(event.code, event.value)
            if self.stop_bool:
                break

    def motorloop(self):   
        while True:
            if self.start_bool:
                self.onestep()
            if self.stop_bool:
                GPIO.cleanup()
                print("This program has been stopped")
                break


if __name__ == "__main__":
    f = flags()
    th1 = threading.Thread(target=f.motorloop)
    th2 = threading.Thread(target=f.eventloop)
    th1.start()
    th2.start()

