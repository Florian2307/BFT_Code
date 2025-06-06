from gpiozero import LED, Button
from time import sleep

led = LED(17)
button = Button(3)

while True:
    led.off()
    if button.value == 1:
        led.off()
