import time
import RPi.GPIO as GPIO

for i in range(3):
    lampe.turn_on()
    time.sleep(1)
    lampe.turn_off()
    time.sleep(8)
