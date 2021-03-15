import machine
from machine import Pin, Timer
import utime

while True:

    s=machine.ADC(2)
    Pin(29,Pin.OUT).off()
    Pin(26,Pin.OUT).on()
    print(s.read_u16())
    utime.sleep_ms(100)