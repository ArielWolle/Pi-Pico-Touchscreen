
# PI-Pico-Touchscreen


Custom touchscreen designed by me running off of a pimoroni tiny 2040 + 4 wire resistive touchscreen

Code is in the Touchscreen folder


![image](https://user-images.githubusercontent.com/36164850/111881001-e8d69f00-8984-11eb-9831-54cff7fd3ced.png)



## Prerequisites

Cirrcuitpython enabled device with 4 analog I/O (they need to be digital compatible as well), 7 digital IO, and a usb port with HID communication enabled.

4 wire resistive touchscreen (the one I got https://www.ebay.ca/itm/12-1inch-4-wire-Resistive-Touch-Panel-For-1024x768-1440x1050-4-3-LCD-Screen/180842889555?ssPageName=STRK%3AMEBIDX%3AIT&_trksid=p2060353.m2749.l2649)

3 6x6 pushbutton switches

4 3mm green LED

1 3mm yellow LED

3D Printer

## Usage

This project is run off of adafruit's circuit python. 

You will need to make a new build of circuitpython to enable the digitizer (touchscreen). If running off of a pimoroni tiny 2040 a firmware build is included in the firmware folder.

On your circuitpython device you need to install the libraryies in the lib folder. 

Next copy the code.py onto the device.

Print enclosure

Assemble and wire up everything

Lastly draw to your hearts content.

## Known Bugs


## Next Steps

Make wiring diagram

Improving CAD as current 3d print looks bad.

Touchscreen wire placement

Build new firmware with the fix of (https://github.com/adafruit/circuitpython/issues/4417)


Drawing vid
https://user-images.githubusercontent.com/36164850/138474686-7877d604-5d39-49c1-bcea-47a5bc7aa096.mov


Calibration vid
https://user-images.githubusercontent.com/36164850/138474673-e01c95d1-a04b-4b8c-a8dc-2e1ca639f9e3.mov

