from gpiozero import LED, Button
from time import sleep

led = LED(17)
button = Button(3)

for i in range(1):
    led.off()
    if button.value == 1:
        led.off()
