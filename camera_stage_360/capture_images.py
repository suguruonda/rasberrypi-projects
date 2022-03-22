from time import sleep
import RPi.GPIO as GPIO

class Camerastage:
    def __init__(self, DIR, STEP, MODE1, MODE2, MODE3, SW1, SW2, SS):
        self.DIR = DIR #Direction GPIO Pin
        self.STEP = STEP #Step GPIO Pin
        self.SW1 = SW1 #Autofocus switch
        self.SW2 = SW2 #Shutter switch
        self.MODE = (MODE1, MODE2, MODE3) #Microstep Resolution GPIO Pins
        self.SS = SS #Shutter speed

        self.SPR = 200 #Steps per Resolution (360 / 1.8)
        self.CW =1 #Clockwise Rotaion
        self.CCW = 0 #Counterclockwise Rotation
        self.RESOLUTION_MODE = '1/32'
        self.RESOLUTION = {'Full':(0,0,0),
                      'Half':(1,0,0),
                      '1/4':(0,1,0),
                      '1/8':(1,1,0),
                      '1/16':(0,0,1),
                      '1/32':(1,0,1)}
        self.RESOLUTION_MICROSTEP = {'Full':1,
                                'Half':2,
                                '1/4':4,
                                '1/8':8,
                                '1/16':16,
                                '1/32':32}
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.STEP, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.DIR, GPIO.OUT)
        GPIO.setup([self.SW1, self.SW2],GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.MODE, GPIO.OUT)
        GPIO.output(self.MODE, self.RESOLUTION[self.RESOLUTION_MODE])
        self.step_count = self.SPR * self.RESOLUTION_MICROSTEP[self.RESOLUTION_MODE]
        self.delay = .005 / self.RESOLUTION_MICROSTEP[self.RESOLUTION_MODE]

    def shooting_an_image(self):
        sleep(0.5)
        GPIO.output(self.SW1, GPIO.LOW)
        sleep(0.5)
        GPIO.output(self.SW2, GPIO.LOW)
        sleep(self.SS + 0.5)

        GPIO.output(self.SW2, GPIO.HIGH)
        GPIO.output(self.SW1, GPIO.HIGH)

    def stage_rotate_shooting(self, images_per_rotation, clock_wise=True):
        if self.step_count < images_per_rotation:
            print('ERROR:images_per_rotation must be less than step_count')
            return -1
        rotation_step = self.step_count // (images_per_rotation)
        if clock_wise == True:
            GPIO.output(self.DIR, self.CW)
        else:
            GPIO.output(self.DIR, self.CCW)
            
        for x in range(self.step_count):
            if x % rotation_step == 0:
                self.shooting_an_image()
                
            GPIO.output(self.STEP, GPIO.HIGH)
            sleep(self.delay)
            GPIO.output(self.STEP, GPIO.LOW)
            sleep(self.delay)


if __name__ == "__main__":
    
    DIR = 21 #Direction GPIO Pin
    STEP = 20 #Step GPIO Pin
    MODE1 = 13 #Microstep Resolution GPIO Pins
    MODE2 = 19 #Microstep Resolution GPIO Pins
    MODE3 = 26 #Microstep Resolution GPIO Pins
    SW1 = 17 #Autofocus switch
    SW2 = 4 #Shutter switch
    SS = 1/60 #Shutter speed
    images_per_rotation = 20
    p = Camerastage(DIR, STEP, MODE1, MODE2, MODE3, SW1, SW2, SS)
    p.stage_rotate_shooting(images_per_rotation)
    GPIO.cleanup()
