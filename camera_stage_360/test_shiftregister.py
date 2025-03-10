import RPi.GPIO as GPIO
import time

interval_time = 0.5
loop_num = 1

OE = 4
SRCLK = 17
RCLK = 27
SI = 22

GPIO.setmode(GPIO.BCM)
GPIO.setup(OE, GPIO.OUT, initial = GPIO.HIGH)
GPIO.setup([SRCLK, RCLK, SI], GPIO.OUT, initial = GPIO.LOW)

def fire():
  GPIO.output(RCLK, GPIO.HIGH)
  GPIO.output(RCLK, GPIO.LOW)
  
def shift():
  GPIO.output(SRCLK, GPIO.HIGH)
  GPIO.output(SRCLK, GPIO.LOW)

def output_disable():
  GPIO.output(OE, GPIO.HIGH)

def output_enable():
  bit_val = 0b1111111111111111
  send_bits(bit_val)
  fire()
  GPIO.output(OE, GPIO.LOW)

def send_bits(data):
  for i in range(16): 
    GPIO.output(SI, (data >> i ) & 1)
    shift()

def lighting(num):
  send_bits(num)
  fire()
  print(bin(num))


try:
  print("start")
  output_enable()
  for num in range(loop_num):
    lighting(0b11111111 * 0b100000000 + 0b11111111)
    time.sleep(interval_time)
    lighting(0b00000000 * 0b100000000 + 0b11111111)
    time.sleep(interval_time)
         
    #lighting(0b1000000000000000)
    time.sleep(interval_time)
    time.sleep(interval_time)

finally:
  print("finish")
  output_disable()
  GPIO.cleanup()
