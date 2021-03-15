import time

import adafruit_touchscreen
import board
import digitalio
import usb_hid
import ulab
from adafruit_hid.digitizer import Digitizer


red = digitalio.DigitalInOut(board.LED_R)
green = digitalio.DigitalInOut(board.LED_G)
blue = digitalio.DigitalInOut(board.LED_B)
switch = digitalio.DigitalInOut(board.USER_SW)

red.direction = digitalio.Direction.OUTPUT
blue.direction = digitalio.Direction.OUTPUT
green.direction = digitalio.Direction.OUTPUT
switch.direction = digitalio.Direction.INPUT

ts = adafruit_touchscreen.Touchscreen(board.A0, board.A1, board.A2, board.A3)

green.value = True
blue.value = True
red.value = True


def light_on(obj):
    obj.value = False


def light_off(obj):
    obj.value = True


def light():
    while True:

        if switch.value:
            red.value = False  # switch not pressed light on
        else:
            red.value = True  # switch pressed light off
        print(red.value)
        time.sleep(0.01)


def solve(min, max):
    a = ulab.array([[min, 1], [max, 1]])
    b = ulab.array([[0], [32726]])
    x = ulab.linalg.dot(ulab.linalg.inv(a), b)
    return [x[0][0], x[1][0]]


def calibration():
    global ts

    p = ts.touch_point
    # TOP LEFT
    light_on(red)
    while True:
        p = ts.touch_point

        if p:
            if p[0] > 3000 and p[1] > 3000 and p[2] > 15000:
                break

    print(p)
    light_off(red)
    x_min = p[0]
    y_min = p[1]
    time.sleep(1)

    # TOP RIGHT
    p = ts.touch_point
    light_on(red)

    while True:
        p = ts.touch_point

        if p:
            if p[0] > 3000 and p[1] > 3000 and p[2] > 15000:
                break
    print(p)
    light_off(red)
    y_min = (y_min + p[1]) / 2
    x_max = p[0]
    time.sleep(1)

    # BOTTOM LEFT
    p = ts.touch_point

    light_on(red)
    while True:
        p = ts.touch_point
        if p:
            if p[0] > 3000 and p[1] > 3000 and p[2] > 15000:
                break
    print(p)
    light_off(red)
    x_min = (x_min + p[0]) / 2
    y_max = p[1]
    time.sleep(1)

    # BOTTOM RIGHT
    p = ts.touch_point

    light_on(red)
    while True:
        p = ts.touch_point
        if p:
            if p[0] > 3000 and p[1] > 3000 and p[2] > 15000:
                break
    print(p)
    light_off(red)
    x_max = (x_max + p[0]) / 2
    y_max = (y_max + p[1]) / 2
    time.sleep(1)

    print("X MIN: ", x_min)
    print("X MAX: ", x_max)
    print("Y MIN: ", y_min)
    print("Y MAX: ", y_max)

    return solve(x_min, x_max) + solve(y_min, y_max)


def touch(x1, x2, y1, y2):
    global ts
    digitizer = Digitizer(usb_hid.devices)
    while True:
        if not switch.value:
            return
        p = ts.touch_point
        if p:
            if p[0] > 10 and p[2] > 15000:
                try:
                    digitizer.move_pen(int(p[0] * x1 + x2), int(p[1] * y1 + y2))
                    digitizer.press_buttons(1)
                    digitizer.press_buttons(2)
                except:
                    print("ERROR values: ", p)
        else:
            digitizer.release_all_buttons()


while True:
    x_m, x_b, y_m, y_b = calibration()
    touch(x_m, x_b, y_m, y_b)
