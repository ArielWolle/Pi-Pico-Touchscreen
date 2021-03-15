"""
LED example for Pico. Blinks external LED on and off.

REQUIRED HARDWARE:
* LED on pin GP14.
"""
import time
import board
import digitalio
from analogio import AnalogIn

x = 0
y = 0
while True:
    x1 = digitalio.DigitalInOut(board.A0)
    x1.direction = digitalio.Direction.OUTPUT
    x1.value = True
    y2 = digitalio.DigitalInOut(board.A3)
    y2.direction = digitalio.Direction.OUTPUT
    y2.value = False
    x2 = AnalogIn(board.A1)

    x = x2.value
    if x < 12500:
        x = 0
    x1.deinit()
    y2.deinit()
    x2.deinit()

    x1 = digitalio.DigitalInOut(board.A2)
    x1.direction = digitalio.Direction.OUTPUT
    x1.value = True
    y2 = digitalio.DigitalInOut(board.A1)
    y2.direction = digitalio.Direction.OUTPUT
    y2.value = False
    x2 = AnalogIn(board.A3)
    y = x2.value
    if y < 15500:
        y = 0
    x1.deinit()
    y2.deinit()
    x2.deinit()
    if x != 0 and y != 0:
        print(x, " ", y)
    time.sleep(0.001)