from gpiozero import LED, Button
from time import sleep

led = LED(17)
button = Button(3)

for i in range(4):
    led.on()
    sleep(1)
    led.off()
