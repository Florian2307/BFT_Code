from gpiozero import LED, Button
from time import sleep

led = LED(17)
button = Button(3)

for i in range(3):
    led.on()
sleep(0)
led.off()
sleep(0)
