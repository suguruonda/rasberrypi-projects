from time import sleep
import RPi.GPIO as GPIO

DIR = 21 #Direction GPIO Pin
STEP = 20 #Step GPIO Pin
CW =1 #Clockwise Rotaion
CCW = 0 #Counterclockwise Rotation
SPR = 200 #Steps per Resolution (360 / 1.8)

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(STEP, GPIO.OUT)
GPIO.output(DIR, CW)

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

for x in range(step_count):
    GPIO.output(STEP, GPIO.HIGH)
    sleep(delay)
    GPIO.output(STEP, GPIO.LOW)
    sleep(delay)

sleep(.5)
GPIO.output(DIR, CCW)
for x in range(step_count):
    GPIO.output(STEP, GPIO.HIGH)
    sleep(delay)
    GPIO.output(STEP, GPIO.LOW)
    sleep(delay)


GPIO.cleanup()