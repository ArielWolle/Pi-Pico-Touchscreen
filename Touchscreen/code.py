import time

import adafruit_touchscreen
import board
import digitalio
import usb_hid
import storage
import ulab
from adafruit_hid.digitizer import Digitizer

yelloww = digitalio.DigitalInOut(board.GP4)

top_L = digitalio.DigitalInOut(board.GP0)
top_R = digitalio.DigitalInOut(board.GP1)
bottom_L = digitalio.DigitalInOut(board.GP2)
bottom_R = digitalio.DigitalInOut(board.GP3)

switch = digitalio.DigitalInOut(board.GP6)
mode_sw = digitalio.DigitalInOut(board.GP7)
left_click = digitalio.DigitalInOut(board.GP5)

top_L.direction = digitalio.Direction.OUTPUT
top_R.direction = digitalio.Direction.OUTPUT
bottom_L.direction = digitalio.Direction.OUTPUT
bottom_R.direction = digitalio.Direction.OUTPUT
yelloww.direction = digitalio.Direction.OUTPUT

switch.direction = digitalio.Direction.INPUT
mode_sw.direction = digitalio.Direction.INPUT
left_click.direction = digitalio.Direction.INPUT

mode_sw.switch_to_input(pull=digitalio.Pull.DOWN)
left_click.switch_to_input(pull=digitalio.Pull.DOWN)
switch.switch_to_input(pull=digitalio.Pull.DOWN)

ts = adafruit_touchscreen.Touchscreen(board.A3, board.A1, board.A2, board.A0)


def startup():

    # Initial Start up sequence so that you know all is going well

    # Turn on all LEDS
    top_L.value = True
    top_R.value = True
    bottom_L.value = True
    bottom_R.value = True
    yelloww.value = True

    # Wait a second
    time.sleep(1)

    # Turn all LEDS off
    top_L.value = False
    top_R.value = False
    bottom_L.value = False

    bottom_R.value = False
    yelloww.value = False


def light_on(obj):

    # Helper method to turn on the LEDS

    obj.value = True


def light_off(obj):

    # Helper method to turn off LEDS

    obj.value = False


def solve(min, max):

    # Uses linear algebra to find the soloution of 2 linear equations

    a = ulab.array([[min, 1], [max, 1]])  # Stores the equation side of the matrix

    b = ulab.array([[0], [32726]])  # Stores the resultant side of the matrix

    x = ulab.linalg.dot(
        ulab.linalg.inv(a), b
    )  # Uses the formula inv(A) dot (B) = Soloution matrix

    return [x[0][0], x[1][0]]  # Returns soloution matrix


def calibration_loop():
    while True:
        if left_click.value:
            return 1
        p = ts.touch_point

        if p:
            if p[0] > 3000 and p[1] > 3000 and p[2] > 15000:
                return p


def calibration(old_data):
    # Calibration method

    # Calibrates the screen by having the user press the 4 corners of the touchscreen, the corner that is meant to be touched lights up with LEDS

    # Each corner press has 5 steps

    # Turn on the corressponding LED
    # Wait for touch input
    # Print the x,y,strength of the touch point to the serial com port
    # Turn off corresponding LED
    # Save the x and y values (automatically averages out min/max values)
    # Wait one second

    ############################

    # Start of corner touch calibration

    # TOP LEFT
    light_on(top_L)

    p = calibration_loop()
    if p == 1:
        return old_data

    print(p)
    light_off(top_L)
    x_min = p[0]
    y_min = p[1]
    time.sleep(1)

    # TOP RIGHT
    p = ts.touch_point
    light_on(top_R)

    p = calibration_loop()
    if p == 1:
        return old_data
    print(p)
    light_off(top_R)
    y_min = (y_min + p[1]) / 2
    x_max = p[0]
    time.sleep(1)

    # BOTTOM LEFT
    p = ts.touch_point

    light_on(bottom_L)
    p = calibration_loop()
    if p == 1:
        return old_data
    print(p)
    light_off(bottom_L)
    x_min = (x_min + p[0]) / 2
    y_max = p[1]
    time.sleep(1)

    # BOTTOM RIGHT
    p = ts.touch_point

    light_on(bottom_R)
    p = calibration_loop()
    if p == 1:
        return old_data
    print(p)
    light_off(bottom_R)
    x_max = (x_max + p[0]) / 2
    y_max = (y_max + p[1]) / 2
    time.sleep(1)

    # End of corner touch calibration

    #######################

    # Print the minimium and maximium values onto the serial com port
    print("X MIN: ", x_min)
    print("X MAX: ", x_max)
    print("Y MIN: ", y_min)
    print("Y MAX: ", y_max)

    # Use linear algebra to solve the system of two equations to conver the touchscreens 0-65xxx(max 12 bit ADC max value) to the digitizer 0-32767 values

    temp = solve(x_min, x_max) + solve(y_min, y_max)

    # Try to save the calibration data onto the flash memory

    # You need to eject the USB mass storage device with the current firmware build new firmware will be uploaded whent this issue is resolved https://github.com/adafruit/circuitpython/issues/4417

    try:
        storage.remount("/", False)  # Try mounting the storage to save

        # Saves the calibration data for the two y=mx+b as:
        # m1 b1\nm2 b2
        with open("/saved.txt", "w") as fp:
            fp.write(str(temp[0]) + " " + str(temp[1]) + "\n")
            fp.write(str(temp[2]) + " " + str(temp[3]))
            fp.close()
        storage.remount("/", True)  # Unmount the storage
    except:

        # If the calibration does not save the yellow LED flashes quickly 3 times but the calibration stays until next power cycle

        for i in range(3):
            light_on(yelloww)
            time.sleep(0.25)
            light_off(yelloww)
            time.sleep(0.25)

    return temp


def touch():

    # Touch Method that sends the USB HID packets

    # This method first reads the on flash memory calibration data and stores it in a variable
    # If this read Fails it reverts to defulat settings and flashes the yelloww LEDS 3 times

    mode = 0
    digitizer = Digitizer(usb_hid.devices)
    last_time = time.monotonic()
    last_speed = 1
    p = ts.touch_point
    last_p = [0, 0, 0]

    # The useful digitzer methods include
    # digitizer.move_pen(x,y)
    # This method moves the pen to the corresponding x and y location with a max value of 32767 and a minimium value of 0
    # digitizer.press_buttons(button)
    # This method takes in an int corresponding to which button is pressed
    # Button 1 = move cursor
    # Button 2 = left click mouse
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
        for i in range(0, 3):
            # Turn on yelloww LEDS
            top_L.value = True
            top_R.value = True
            bottom_L.value = True
            bottom_R.value = True

            # Wait
            time.sleep(0.25)

            # Turn all yelloww LEDS off
            top_L.value = False
            top_R.value = False
            bottom_L.value = False
            bottom_R.value = False

            # wait
            time.sleep(0.25)

    while True:
        # Main loop that runs while using the touchscreen

        # Checks if the user wants to recalibrate the screen and if so resets the x and y values to the new calibration data

        if switch.value:
            x1, x2, y1, y2 = calibration([x1, x2, y1, y2])
            light_off(bottom_L)
            light_off(bottom_R)
            light_off(top_L)
            light_off(top_R)

        # Uses the Adafruit touchscreen library to recive and store touch input in the varibale p
        p = ts.touch_point

        # If the switch mode button is pressed swap modes and wait one second
        if mode_sw.value:

            if mode == 1:
                mode = 0
                yelloww.value = False
            elif mode == 0:
                mode = 1
                yelloww.value = True
            time.sleep(1)

        # Checks if the touchscreen is being pressed
        if p:
            # Checks if the touchscreen input is not garbage and if the touchscreen is being held with enough pressure
            if p[0] > 10 and p[2] > 10000:
                if last_p == 1:
                    last_p = p
                speed = (
                    ((p[0] - last_p[0]) ** 2 + (p[1] - last_p[1]) ** 2) ** (1 / 2)
                ) / ((time.monotonic() - last_time) * 1000)

                if (speed / last_speed) < 1.5:
                    try:
                        # Moves the pen to the corresponding x and y values from a range of 0-32767 using the calibration data
                        digitizer.move_pen(int(p[0] * x1 + x2), int(p[1] * y1 + y2))
                        # Moves the cursor itself
                        digitizer.press_buttons(1)

                        # Checks if the mode is in drawing mode, if so hold left click as you move the cursor
                        if mode == 0:
                            digitizer.press_buttons(2)

                        # Checks if the mode is in the cursor mode, if so just move the cursor don't press left click

                        # The current tablet is missing a button so that in this mode if the button is pressed down the tablet will left click
                        elif mode == 1 and left_click.value:
                            digitizer.press_buttons(2)

                    except:
                        # If the touchscreen records input from outside the calibration square the input is desregarded
                        print("ERROR values: ", p)
                last_p = p
                last_time = time.monotonic()
                if speed == 0:
                    last_speed = 0.001
                else:
                    last_speed = speed

        else:
            if last_p != 1:
                last_p = 1
            last_time = time.monotonic()
            # if the touchscreen sees no input let go of left click and the cursor
            digitizer.release_all_buttons()


startup()
touch()
