from time import sleep
import RPi.GPIO as GPIO
import cv2
import screeninfo
import glob
import time

class Camerastage:
    def __init__(self, p):
        self.DIR = 20 #Direction GPIO Pin/Clockwise:True, Counterclockwise:false
        self.STEP = 21 #Step GPIO Pin
        self.OE = 4 #Output enable when this pin is low
        self.SRCLK = 17 #Shift register clock
        self.RCLK = 27 #Storage Register Clock
        self.SI = 22 #Serial data input
        self.MODE = (26, 19, 13) #Microstep Resolution GPIO Pins M0, M1, m2
        self.SS = 1/60 #Shutter speed

        self.SPR = 200 #Steps per Resolution (360 / 1.8)
        self.RESOLUTION_MODE = '1/32'
        self.RESOLUTION = {'1':(0,0,0),
                      '1/2':(1,0,0),
                      '1/4':(0,1,0),
                      '1/8':(1,1,0),
                      '1/16':(0,0,1),
                      '1/32':(1,0,1)}
        self.RESOLUTION_MICROSTEP = {'1':1,
                                '1/2':2,
                                '1/4':4,
                                '1/8':8,
                                '1/16':16,
                                '1/32':32}
        self.pimg_size = 511 #projrctor image size
        self.SW =5 #switch button
        self.SOFTBOX1 =18 #Softbox light relay input
        self.SOFTBOX2 =23 #Softbox light relay input
        self.SOFTBOX3 =24 #Softbox light relay input
        self.SOFTBOX4 =25 #Softbox light relay input
        self.LAMP1 =16 #Lamp relay input
        self.LAMP2 =12 #Lamp light relay input
        self.SB_list = [self.SOFTBOX1, self.SOFTBOX2, self.SOFTBOX3, self.SOFTBOX4, self.LAMP1, self.LAMP2]
        self.HALLSENSOR = 6 #Hall magnetic sensor
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.SW, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.SB_list, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(self.STEP, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.DIR, GPIO.OUT)
        GPIO.setup(self.OE, GPIO.OUT, initial = GPIO.HIGH)
        GPIO.setup([self.SRCLK, self.RCLK, self.SI], GPIO.OUT, initial = GPIO.LOW)
        GPIO.setup(self.MODE, GPIO.OUT)
        GPIO.output(self.MODE, self.RESOLUTION[self.RESOLUTION_MODE])
        self.step_count = self.SPR * self.RESOLUTION_MICROSTEP[self.RESOLUTION_MODE]
        self.delay = .005 / self.RESOLUTION_MICROSTEP[self.RESOLUTION_MODE] * 4
        GPIO.setup(self.HALLSENSOR, GPIO.IN)
        if p:
            screen_1 = screeninfo.get_monitors()[0]
            screen_2 = screeninfo.get_monitors()[1]
            image_dir = "projector_img/" + str(self.pimg_size)

            self.files = glob.glob(image_dir + '/*.png')
            self.files.sort()
            self.windowname1 = "1"
            self.windowname2 = "2"
            self.blank_img = cv2.imread(self.files[0])
            cv2.namedWindow(self.windowname1, cv2.WINDOW_FULLSCREEN)
            cv2.moveWindow(self.windowname1, screen_1.x, screen_1.y)
            cv2.setWindowProperty(self.windowname1, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

            cv2.namedWindow(self.windowname2, cv2.WINDOW_FULLSCREEN)
            cv2.moveWindow(self.windowname2, screen_2.x, screen_2.y)
            cv2.setWindowProperty(self.windowname2, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    def change_step_pitch(self, resmode : str):
        GPIO.output(self.MODE, self.RESOLUTION[resmode])
        self.step_count = self.SPR * self.RESOLUTION_MICROSTEP[resmode]
        self.delay = .005 / self.RESOLUTION_MICROSTEP[resmode] *4
    
    def set_motor_initial_position(self):
        self.set_motor_direction(True)
        pitch = 32
        self.change_step_pitch("1/" + str(pitch))
        one_step = int(pitch/1)
        loc = 0
        while True:
            current_position = self.hallsensor()
            self.rotate_stage(one_step)
            loc += 1
            next_position = self.hallsensor()   
            if current_position == True and next_position == False:
                break
        print(loc)
        return loc

        
    def hallsensor(self):
        return GPIO.input(self.HALLSENSOR)

    def softbox_SW(self, num, bool):     
        GPIO.output(self.SB_list[num], not(bool))

    def softbox_SW_ALL(self, bool):     
        GPIO.output(self.SB_list, not(bool))

    def output_serial(self):
        GPIO.output(self.RCLK, GPIO.HIGH)
        GPIO.output(self.RCLK, GPIO.LOW)
  
    def shift_bit(self):
        GPIO.output(self.SRCLK, GPIO.HIGH)
        GPIO.output(self.SRCLK, GPIO.LOW)

    def output_disable(self):
        GPIO.output(self.OE, GPIO.HIGH)

    def output_enable(self):
        bit_val = 0b1111111111111111
        self.set_16bits_serial(bit_val)
        self.output_serial()
        GPIO.output(self.OE, GPIO.LOW)

    def set_16bits_serial(self, data):
        for i in range(16): 
            GPIO.output(self.SI, (data >> i) & 1)
            self.shift_bit()

    def half_press_shutter_button(self, num):
        """
        num = 8 bits binary number
        each digit represent each camera and it performs autofocus if it is 0.
        ex) num = 0b01010101, then camera number 1, 3, 5, 7 run autofocus.
        """
        bit_val = num * 0b100000000 + 0b11111111
        self.set_16bits_serial(bit_val)
        self.output_serial()
        #print(bin(bit_val))

    def full_press_shutter_button(self, num):
        """
        num = 8 bits binary number
        each digit represent each camera and shoot a image if it is 0.
		ex) num = 0b01010101, then camera number 1, 3, 5, 7 shoot.
        """
        bit_val = num * 0b100000000  + num
        self.set_16bits_serial(bit_val)
        self.output_serial()
        #print(bin(bit_val))

    def shooting_an_image(self, num):
        self.output_enable()
        #sleep(1)
        #self.half_press_shutter_button(0b00000000)
        sleep(0.35)
        self.full_press_shutter_button(num)
        sleep(self.SS + 0.35)
        self.output_disable()

    def rotate_stage(self, step_count):
        for x in range(step_count):
            GPIO.output(self.STEP, GPIO.HIGH)
            sleep(self.delay)
            GPIO.output(self.STEP, GPIO.LOW)
            sleep(self.delay)

    def set_motor_direction(self, cw_bool):
        GPIO.output(self.DIR, not(cw_bool))

    def stage_rotate_shooting(self, images_per_rotation, clock_wise=True):
        self.set_motor_initial_position()
        if self.step_count < images_per_rotation:
            print('ERROR:images_per_rotation must be less than step_count')
            return -1
        rotation_step = self.step_count // (images_per_rotation)
        self.set_motor_direction(clock_wise)
            
        for x in range(images_per_rotation):
            self.shooting_an_image(0b11111111)
            sleep(self.delay)
            self.rotate_stage(rotation_step)

        #self.rotate_stage(self.step_count % (images_per_rotation))

    def stage_rotate_shooting2(self, clock_wise=True):
        self.set_motor_initial_position()
        sleep(self.SS+3)
        self.softbox_SW_ALL(True)
        sleep(self.SS+3)
        pitch = 32
        one_step = int(pitch/1)
        
        #sleep(self.SS + 1)
        #self.rotate_stage(one_step*5*8)
        #sleep(self.SS + 1)
        #self.rotate_stage(one_step*5*8)
        #sleep(self.SS + 1)
        #self.rotate_stage(one_step*5*8)
        #sleep(self.SS + 1)
        #self.rotate_stage(one_step*5*8)
        #sleep(self.SS + 1)
        
        #sleep(self.SS + 1)
        #self.rotate_stage(one_step*5*20)
        #self.rotate_stage(one_step*5*30)
        sleep(self.SS + 1)
        #self.shooting_an_image(0b01111111)
        self.shooting_an_image(0b11111110)
        sleep(self.SS + 1)
        self.shooting_an_image(0b11111110)
        #self.shooting_an_image(0b01111111)
        sleep(self.SS + 1)

        #for x in range(20):
        #for x in range(10):
        for x in range(40):
            self.shooting_an_image(0b11111110)
            #self.shooting_an_image(0b01111111)
            #self.shooting_an_image(0b10111111)
            sleep(self.SS+3)
            self.rotate_stage(one_step*5)
        sleep(self.SS+3)
        self.shooting_an_image(0b11111110)
        #self.shooting_an_image(0b01111111)
        #self.shooting_an_image(0b10111111)
        sleep(self.SS+3)

    def stage_rotate_shooting3(self, clock_wise=True):
        self.softbox_SW_ALL(True)
        pitch = 32
        one_step = int(pitch/1)
        for i in range(20):
            self.set_motor_initial_position()
            self.shooting_an_image(0b01111111)
            
            for j in range(40):
                self.rotate_stage(one_step*5)
                sleep(self.SS + 1)
            
            self.shooting_an_image(0b01111111)


    def stage_rotate_shooting_with_calibration(self, clock_wise=True):
        loc = self.set_motor_initial_position()
        if loc != 200:
            loc = self.set_motor_initial_position()
            if loc != 200:
                loc = self.set_motor_initial_position()
                if loc != 200:
                    print("Please check initial position")
                    input()
        #sleep(self.SS+3)
        print("Start")

        self.shooting_an_image(0b00001111)
        self.shooting_an_image(0b11110000)
        #self.shooting_an_image(0b00000001)
        #self.shooting_an_image(0b11111110)
        sleep(self.SS+1)
        self.shooting_an_image(0b00001111)
        self.shooting_an_image(0b11110000)
        #self.shooting_an_image(0b00000001)
        #self.shooting_an_image(0b11111110)
        #sleep(self.SS+1)

        pitch = 32
        one_step = int(pitch/1)*5
        images_per_rotation = 40

        cv2.imshow(self.windowname1, self.blank_img)
        cv2.imshow(self.windowname2, self.blank_img)
        cv2.waitKey(500)

        for x in range(images_per_rotation):
            if x == 0 or x == 20:
                self.softbox_SW_ALL(True)
                self.softbox_SW(5, False)
                self.softbox_SW(4, False)
                print()
                print("### Change Custom Mode to C2 ###")
                print("### Please press enter key if you are ready ###")
                input()
                self.softbox_SW_ALL(False)
                print("\rShooting image {0}/{1}".format(x+1, images_per_rotation), end="")
                cv2.imshow(self.windowname1, self.blank_img)
                cv2.imshow(self.windowname2, self.blank_img)        
                cv2.waitKey(500)
                
                cimg_num = 1
                for i in self.files[1:]:
                    print("\rShooting image {0}/{1}:calibration images {2}/{3}   ".format(x+1, images_per_rotation, cimg_num, len(self.files[1:])), end="")
                    img = cv2.imread(i)
                    cv2.imshow(self.windowname1, img)
                    cv2.imshow(self.windowname2, self.blank_img)   
                    cv2.waitKey(1)
                    sleep(self.SS+0.6)
                    self.shooting_an_image(0b00001111)
                    cv2.imshow(self.windowname2, img)
                    cv2.imshow(self.windowname1, self.blank_img)   
                    cv2.waitKey(1)
                    sleep(self.SS+0.6)
                    self.shooting_an_image(0b11110000)
                    #self.shooting_an_image(0b11110001)
                    #self.shooting_an_image(0b11111110)
                    if cimg_num == 18:
                        sleep(2)
                    """
                    if cimg_num%4 == 0:
                        if cimg_num == 20:
                            sleep(5)
                        elif cimg_num == 36:
                            sleep(1.5)
                        else:
                            sleep(3)
                    """
                    cimg_num += 1
                sleep(1.5)

                cv2.imshow(self.windowname1, self.blank_img)
                cv2.imshow(self.windowname2, self.blank_img)        
                cv2.waitKey(1)

                self.softbox_SW_ALL(True)
                self.softbox_SW(5, False)
                self.softbox_SW(4, False)
                print()
                print("### Change Custom Mode to C1 ###")
                print("### Please press enter key if you are ready ###")
                input()
                self.softbox_SW_ALL(True)
                #self.softbox_SW_ALL(False)
                sleep(2.0)

            #self.shooting_an_image(0b00000000)
            self.shooting_an_image(0b00001111)
            self.shooting_an_image(0b11110000)
            #self.shooting_an_image(0b11111110)
            #self.shooting_an_image(0b00000001)
            sleep(0.5)
            print("\rShooting image {0}/{1}:                                     ".format(x+1, images_per_rotation), end="")
            if x == (images_per_rotation - 1):
                current_position = self.hallsensor()
            self.rotate_stage(one_step)
            if x == (images_per_rotation - 1):
                next_position = self.hallsensor()   
                if current_position == True and next_position == False:
                    print()
                    print("***Success***")
                else:
                    print("Please check motor position")
            else:
                sleep(self.SS+0.5)
            """
            if (x+1)%4 == 0 and x != 19:
                sleep(2.5)
            """
        print("\nDone")
        #self.rotate_stage(self.step_count % (images_per_rotation))
        #self.set_motor_initial_position()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    
    start = time.time()
    #images_per_rotation = 4
    p = Camerastage(True)
    #p = Camerastage(False)
    #p.stage_rotate_shooting(images_per_rotation)
    p.stage_rotate_shooting_with_calibration()
    #p.stage_rotate_shooting2()
    GPIO.cleanup()
    elapsed_time = time.time() - start
    print ("elapsed_time:{0}".format(elapsed_time//60) + "[min] " + "{0}[sec]".format((elapsed_time%60)//1))

