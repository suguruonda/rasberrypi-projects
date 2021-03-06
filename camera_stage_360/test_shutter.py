import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BCM)

c1 = 17
c2 = 4
GPIO.setup([c1,c2],GPIO.OUT, initial=GPIO.HIGH)

GPIO.output(c1,GPIO.LOW)
sleep(0.3)
GPIO.output(c2,GPIO.LOW)
sleep(0.5)

GPIO.output(c2,GPIO.HIGH)
GPIO.output(c1,GPIO.HIGH)