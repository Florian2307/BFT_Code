import time
import RPi.GPIO as GPIO

while True:
    if taster:
        lampe.turn_on()
    if not taster:
        lampe.turn_off()
