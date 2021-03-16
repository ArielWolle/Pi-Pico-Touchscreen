import time

import adafruit_touchscreen
import board
import digitalio
import usb_hid
import storage
import ulab
from adafruit_hid.digitizer import Digitizer

green = digitalio.DigitalInOut(board.GP4)

top_L = digitalio.DigitalInOut(board.GP0)
top_R = digitalio.DigitalInOut(board.GP1)
bottom_L = digitalio.DigitalInOut(board.GP2)
bottom_R = digitalio.DigitalInOut(board.GP3)

switch = digitalio.DigitalInOut(board.USER_SW)
mode_sw = digitalio.DigitalInOut(board.GP7)
left_click = digitalio.DigitalInOut(board.GP6)

top_L.direction = digitalio.Direction.OUTPUT
top_R.direction = digitalio.Direction.OUTPUT
bottom_L.direction = digitalio.Direction.OUTPUT
bottom_R.direction = digitalio.Direction.OUTPUT
green.direction = digitalio.Direction.OUTPUT

switch.direction = digitalio.Direction.INPUT
mode_sw.direction = digitalio.Direction.INPUT
left_click.direction = digitalio.Direction.INPUT

mode_sw.switch_to_input(pull=digitalio.Pull.DOWN)
left_click.switch_to_input(pull=digitalio.Pull.DOWN)

ts = adafruit_touchscreen.Touchscreen(board.A3, board.A1, board.A2, board.A0)

top_L.value = True
top_R.value = True
bottom_L.value = True
bottom_R.value = True
green.value = True

time.sleep(1)

top_L.value = False
top_R.value = False
bottom_L.value = False
bottom_R.value = False
green.value = False


def light_on(obj):
    obj.value = True


def light_off(obj):
    obj.value = False


def solve(min, max):
    a = ulab.array([[min, 1], [max, 1]])
    b = ulab.array([[0], [32726]])
    x = ulab.linalg.dot(ulab.linalg.inv(a), b)
    return [x[0][0], x[1][0]]


def calibration():
    global ts

    p = ts.touch_point
    # TOP LEFT
    light_on(top_L)
    while True:
        p = ts.touch_point

        if p:
            if p[0] > 3000 and p[1] > 3000 and p[2] > 15000:
                break

    print(p)
    light_off(top_L)
    x_min = p[0]
    y_min = p[1]
    time.sleep(1)

    # TOP RIGHT
    p = ts.touch_point
    light_on(top_R)

    while True:
        p = ts.touch_point

        if p:
            if p[0] > 3000 and p[1] > 3000 and p[2] > 15000:
                break
    print(p)
    light_off(top_R)
    y_min = (y_min + p[1]) / 2
    x_max = p[0]
    time.sleep(1)

    # BOTTOM LEFT
    p = ts.touch_point

    light_on(bottom_L)
    while True:
        p = ts.touch_point
        if p:
            if p[0] > 3000 and p[1] > 3000 and p[2] > 15000:
                break
    print(p)
    light_off(bottom_L)
    x_min = (x_min + p[0]) / 2
    y_max = p[1]
    time.sleep(1)

    # BOTTOM RIGHT
    p = ts.touch_point

    light_on(bottom_R)
    while True:
        p = ts.touch_point
        if p:
            if p[0] > 3000 and p[1] > 3000 and p[2] > 15000:
                break
    print(p)
    light_off(bottom_R)
    x_max = (x_max + p[0]) / 2
    y_max = (y_max + p[1]) / 2
    time.sleep(1)

    print("X MIN: ", x_min)
    print("X MAX: ", x_max)
    print("Y MIN: ", y_min)
    print("Y MAX: ", y_max)
    temp = solve(x_min, x_max) + solve(y_min, y_max)
    try:
        storage.remount("/", False)

        with open("/saved.txt", "w") as fp:
            fp.write(str(temp[0]) + " " + str(temp[1]) + "\n")
            fp.write(str(temp[2]) + " " + str(temp[3]))
            fp.close()
            storage.remount("/", True)
    except:
        for i in range(3):
            light_on(green)
            time.sleep(0.25)
            light_off(green)
            time.sleep(0.25)

    return temp


def touch():
    mode = 0
    global ts
    x1 = 0
    x2 = 0
    y1 = 0
    y2 = 0
    last_mode = False
    digitizer = Digitizer(usb_hid.devices)
    try:
        with open("/saved.txt", "r") as fp:
            print("Opening")
            x1, x2 = fp.readline().split(" ")
            x1 = float(x1)
            x2 = float(x2)
            print(x1, x2)
            y1, y2 = fp.readline().split(" ")
            y1 = float(y1)
            y2 = float(y2)
            fp.close()
    except:
        print("ERROR when reading")
        x1 = 0.599657
        x2 = -2220.53
        y1 = 0.63508
        y2 = -3983.86
    while True:
        if left_click.value:
            x1, x2, y1, y2 = calibration()
        p = ts.touch_point
        if mode_sw.value:
            print("A")
            if mode == 1:
                mode = 0
                green.value = False
            elif mode == 0:
                mode = 1
                green.value = True
            last_mode = mode_sw.value
            time.sleep(1)
        if p:
            if p[0] > 10 and p[2] > 20000:
                try:
                    digitizer.move_pen(int(p[0] * x1 + x2), int(p[1] * y1 + y2))
                    digitizer.press_buttons(1)
                    if mode == 0:
                        digitizer.press_buttons(2)
                    elif mode == 1 and left_click.value:
                        digitizer.press_buttons(2)
                except:
                    print("ERROR values: ", p)
        else:
            digitizer.release_all_buttons()


def main():

    while True:
        touch()


main()
