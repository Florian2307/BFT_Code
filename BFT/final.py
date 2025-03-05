from gpiozero import LED, Button
from time import sleep

led = LED(17)
button = Button(2)
while True:

    if button.value == 0:
        led.on()    