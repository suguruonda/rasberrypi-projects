import RPi.GPIO as GPIO
import time

interval_time = 0.5
loop_num = 3

SRCLR = 26
SRCLK = 19
RCLK = 13
SI = 6

GPIO.setmode(GPIO.BCM)
GPIO.setup([SRCLR, SRCLK, RCLK, SI], GPIO.OUT, initial = GPIO.LOW)

def fire():
  GPIO.output(RCLK, GPIO.HIGH)
  GPIO.output(RCLK, GPIO.LOW)
  
def shift():
  GPIO.output(SRCLK, GPIO.HIGH)
  GPIO.output(SRCLK, GPIO.LOW)

def reset():
  GPIO.output(SRCLR, GPIO.LOW)
  fire()
  GPIO.output(SRCLR, GPIO.HIGH)
  GPIO.output([SRCLK, RCLK, SI], GPIO.LOW)



def send_bits(data):
  for i in range(16): 
    GPIO.output(SI, ((1 << i ) & data))
    shift()

def lighting(num):
  send_bits(num)
  fire()
  print(bin(num))

try:
  print("start")
  reset()
  for num in range(loop_num):
    lighting(0b1101100101000101)
    time.sleep(interval_time)
    reset()
    time.sleep(interval_time)

finally:
  print("finish")
  reset()
  GPIO.cleanup()
