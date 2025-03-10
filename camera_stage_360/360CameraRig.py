import threading
import sys
import evdev
from evdev import InputDevice, categorize, ecodes, KeyEvent
from capture_360images import Camerastage 
import RPi.GPIO as GPIO
from time import sleep
import cv2
import argparse

class Gamepad:
    def __init__(self):
        self.name = 'Gamepad'
        self.dpad_up_down_code = 1
        self.dpad_left_right_code = 0
        self.start_code = 297
        self.select_code = 296
        self.a_code = 290
        self.b_code = 289
        self.x_code = 288
        self.y_code = 291
        self.l_code = 292
        self.r_code = 293

        self.dpad_up_value = 0
        self.dpad_vertical_neutral_value = 127
        self.dpad_down_value = 255
        self.dpad_left_value = 0
        self.dpad_horizontal_neutral_value = 127
        self.dpad_right_value = 255
        self.start_on_value = 1
        self.select_on_value = 1
        self.a_on_value = 1
        self.b_on_value = 1 
        self.y_on_value = 1
        self.x_on_value = 1
        self.l_on_value = 1
        self.r_on_value = 1

        self.start_off_value = 0
        self.select_off_value = 0
        self.a_off_value = 0 
        self.b_off_value = 0
        self.y_off_value = 0
        self.x_off_value = 0 
        self.l_off_value = 0
        self.r_off_value = 0

class Gamepad_f310(Gamepad):
    def __init__(self):
        super().__init__()
        self.name = 'F310'
        self.dpad_up_down_code = 17
        self.dpad_left_right_code = 16
        self.start_code = 315
        self.select_code = 314
        self.a_code = 304
        self.b_code = 305
        self.y_code = 308
        self.x_code = 307
        self.l_code = 310
        self.r_code = 311

        self.dpad_up_value = -1
        self.dpad_vertical_neutral_value = 0
        self.dpad_down_value = 1
        self.dpad_left_value = -1
        self.dpad_horizontal_neutral_value = 0
        self.dpad_right_value = 1
        

class CameraRig(Camerastage):
    def __init__(self,gamepadclass):
        parser = argparse.ArgumentParser()
        parser.add_argument("-p", action='store_true')
        self.args = parser.parse_args()
        super().__init__(self.args.p)

        self.g = gamepadclass()
        self.cw_bool = True
        self.start_bool = False
        self.stop_bool = False
        self.top_camera_bool = False
        self.bottom_camera_bool = False
        self.a_bool = False
        self.b_bool = False
        self.x_bool = False
        self.y_bool = False

        self.sb1_bool = False
        self.sb2_bool = False
        self.sb3_bool = False
        self.sb4_bool = False
        self.projector1_bool = False
        self.projector2_bool = False
        self.projector1_num = 0
        self.projector2_num = 0

        self.select_bool = False

        #Setting for gamepad
        devices = [InputDevice(path) for path in evdev.list_devices()]
        find_pad = False
        for device in devices:
            if self.g.name in device.name:
                dev_path = device.path
                find_pad = True
                print("A Gamepad is found.")
        if not(find_pad):
            print("No gamepad detected.")
            sys.exit()

        self.device = InputDevice(dev_path)
        if self.args.p:
            cv2.imshow(self.windowname1, self.blank_img)
            cv2.imshow(self.windowname2, self.blank_img)
            cv2.waitKey(2000)
            cv2.imshow(self.windowname1, self.blank_img)
            cv2.imshow(self.windowname2, self.blank_img)
            cv2.waitKey(500)

        print("Ready to use 360CameraRIg")
        self.print_instruction()

    def __del__(self):
        print("Shut down button is pressed...")
        self.all_light_off()
        cv2.destroyAllWindows()
        GPIO.cleanup()
        print("This program has been successfuly stopped.")

    def cw_true(self):
        if not(self.cw_bool):
            self.cw_bool = True
            self.set_motor_direction(self.cw_bool)
            #GPIO.output(self.DIR, self.CW)

    def cw_false(self):
        if self.cw_bool:
            self.cw_bool = False
            self.set_motor_direction(self.cw_bool)
            #GPIO.output(self.DIR, self.CCW)
    
    def increment_projector_num(self, projector_num, plus_bool):
        if plus_bool:
            add_num = 1
        else:
            add_num = -1
        if projector_num == 1:
            self.projector1_num += add_num
            self.projector1_num = self.projector1_num % len(self.files)
        elif projector_num == 2:
            self.projector2_num += add_num
            self.projector2_num = self.projector2_num % len(self.files)

    def show_projector_image(self, projector_num):
        if projector_num == 1:
            img_path = self.files[self.projector1_num]
            window_name = self.windowname1
        elif projector_num == 2:
            img_path = self.files[self.projector2_num]
            window_name = self.windowname2
        img = cv2.imread(img_path)
        cv2.imshow(window_name, img)
        cv2.waitKey(500)

    def all_light_off(self):
        self.softbox_SW(0, False)
        self.softbox_SW(1, False)
        self.a_bool = False
        self.softbox_SW(2, False)
        self.softbox_SW(3, False)
        self.b_bool = False
        self.softbox_SW(4, False)
        self.softbox_SW(5, False)
        self.x_bool = False
        #self.y_bool = False
        if self.args.p:
            cv2.imshow(self.windowname1, self.blank_img)
            cv2.imshow(self.windowname2, self.blank_img)
            cv2.waitKey(500)
        self.projector1_bool = False
        self.projector2_bool = False        

    def readevent(self, code, value):
        if code == self.g.dpad_left_right_code and value == self.g.dpad_left_value:
            self.cw_false()
            self.start_bool = True
        elif code == self.g.dpad_left_right_code and value == self.g.dpad_right_value:
            self.cw_true()
            self.start_bool = True
        elif code == self.g.dpad_left_right_code and value == self.g.dpad_horizontal_neutral_value:
            self.start_bool = False
        elif code == self.g.dpad_up_down_code and value == self.g.dpad_down_value:
            self.projector1_bool = True
        elif code == self.g.dpad_up_down_code and value == self.g.dpad_up_value:
            self.projector2_bool = True
        elif code == self.g.dpad_up_down_code and value == self.g.dpad_vertical_neutral_value:
            self.projector1_bool = False
            self.projector2_bool = False
        elif code == self.g.start_code and value == self.g.start_on_value:
            self.stop_bool = True
        elif code == self.g.select_code and value == self.g.select_off_value:
            self.select_bool = False
        elif code == self.g.select_code and value == self.g.select_on_value:
            self.select_bool = True
        elif code == self.g.r_code and value == self.g.r_off_value:
            self.top_camera_bool = False
        elif code == self.g.r_code and value == self.g.r_on_value:
            self.top_camera_bool = True
        elif code == self.g.l_code and value == self.g.l_off_value:
            self.bottom_camera_bool = False
        elif code == self.g.l_code and value == self.g.l_on_value:
            self.bottom_camera_bool = True
        elif code == self.g.a_code and value == self.g.a_off_value:
            self.a_bool = False
        elif code == self.g.a_code and value == self.g.a_on_value:
            self.a_bool = True
        elif code == self.g.b_code and value == self.g.b_off_value:
            self.b_bool = False
        elif code == self.g.b_code and value == self.g.b_on_value:
            self.b_bool = True
        elif code == self.g.x_code and value == self.g.x_off_value:
            self.x_bool = False
        elif code == self.g.x_code and value == self.g.x_on_value:
            self.x_bool = True
        elif code == self.g.y_code and value == self.g.y_off_value:
            self.y_bool = False
        elif code == self.g.y_code and value == self.g.y_on_value:
            self.y_bool = True

    def eventloop(self):
        for event in self.device.read_loop():
            if (event.type == evdev.ecodes.EV_KEY) or (event.type == evdev.ecodes.EV_ABS):
                self.readevent(event.code, event.value) 
                #print(str((event.code, event.value)))
                if self.stop_bool:
                    break
                if self.select_bool:
                    #self.set_motor_initial_position()
                    #add thread stop and perform later
                    self.all_light_off()
                    self.select_bool = False
                if self.top_camera_bool and self.bottom_camera_bool:
                    if self.projector1_bool:
                        if self.args.p:
                            self.increment_projector_num(1,False)
                            self.show_projector_image(1)
                            self.projector1_bool = False
                    if self.projector2_bool:
                        if self.args.p:
                            self.increment_projector_num(2,False)
                            self.show_projector_image(2)
                            self.projector2_bool = False
                elif not(self.top_camera_bool) and not(self.bottom_camera_bool):
                    if self.projector1_bool:
                        if self.args.p:
                            self.increment_projector_num(1,True)
                            self.show_projector_image(1)
                            self.projector1_bool = False
                    if self.projector2_bool:
                        if self.args.p:
                            self.increment_projector_num(2,True)
                            self.show_projector_image(2)
                            self.projector2_bool = False
                    if self.a_bool:
                        self.sb1_bool = not(self.sb1_bool)
                        self.softbox_SW(0, self.sb1_bool)
                        self.softbox_SW(1, self.sb1_bool)
                        self.a_bool = False
                    if self.b_bool:
                        self.sb2_bool = not(self.sb2_bool)
                        self.softbox_SW(2, self.sb2_bool)
                        self.softbox_SW(3, self.sb2_bool)
                        self.b_bool = False
                    if self.x_bool:
                        self.sb3_bool = not(self.sb3_bool)
                        self.softbox_SW(4, self.sb3_bool)
                        self.softbox_SW(5, self.sb3_bool)
                        self.x_bool = False
                    if self.y_bool:
                        self.sb4_bool = not(self.sb4_bool)
                        self.y_bool = False
                else:
                    if self.top_camera_bool and self.a_bool:
                        self.shooting_an_image(0b11110111)
                        self.a_bool = False
                    if self.top_camera_bool and self.b_bool:
                        self.shooting_an_image(0b11111011)
                        self.b_bool = False
                    if self.top_camera_bool and self.x_bool:
                        self.shooting_an_image(0b11111101)
                        self.x_bool = False
                    if self.top_camera_bool and self.y_bool:
                        self.shooting_an_image(0b11111110)
                        self.y_bool = False

                    if self.bottom_camera_bool and self.a_bool:
                        self.shooting_an_image(0b01111111)
                        self.a_bool = False
                    if self.bottom_camera_bool and self.b_bool:
                        self.shooting_an_image(0b11011111)
                        self.b_bool = False
                    if self.bottom_camera_bool and self.x_bool:
                        self.shooting_an_image(0b10111111)
                        self.x_bool = False
                    if self.bottom_camera_bool and self.y_bool:
                        self.shooting_an_image(0b11101111)
                        self.y_bool = False

    def motorloop(self):   
        while True:
            try:
                if self.start_bool:
                    self.rotate_stage(1)
                if self.stop_bool:
                    break
            except KeyboardInterrupt:
                self.stop_bool = True
                break

    def print_instruction(self):
        print("------------------------------------------------------------------------")
        print("360 CameraRig manual instruction")
        print("------------------------------------------------------------------------")
        print("### camera shooting ###")
        print("camera1              :L + A")
        print("camera2              :L + X")
        print("camera3              :L + B")
        print("camera4              :L + Y")
        print("camera5              :R + A")
        print("camera6              :R + B")
        print("camera7              :R + X")
        print("camera8              :R + Y")
        print("")
        print("### Softbox ON/OFF ###")
        print("No.1,2                 :A")
        print("No.3,4                 :B")
        print("No.5,6                 :X")
        #print("No.4                 :Y")
        print("")
        print("### Stepper Motor Rotation ###")
        print("Clockwise            :D-Pad Right")
        print("Counter Clockwise    :D-Pad Left")
        print("")
        if self.args.p:
            print("### Projector Calibration image change ###")
            print("No.1                 :D-Pad UP")
            print("No.2                 :D-Pad Down")
            print("No.1 inverse         :L + R + D-Pad UP")
            print("No.2 inverse         :L + R + D-Pad Down")
            print("")
        print("### Reset Motor Position/Turn off all lights###")
        print("Press Select button")
        print("")
        print("### Finish this program ###")
        print("Press Start button")
        print("------------------------------------------------------------------------")

if __name__ == "__main__":
    threads = []
    #g = CameraRig(Gamepad_f310)
    g = CameraRig(Gamepad)
    g.set_motor_initial_position()
    th1 = threading.Thread(target=g.motorloop)
    th2 = threading.Thread(target=g.eventloop)
    th1.start()
    th2.start()


