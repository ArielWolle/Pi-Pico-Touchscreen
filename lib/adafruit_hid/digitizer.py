import struct
import time

from . import find_device


class Digitizer:
    """Emulate a digitizer with 4 buttons,
    numbered 1-4, and ``x` and ``y`` values.
    """

    def __init__(self, devices):
        """Create a Digitizer object that will send USB digitizer HID reports.

        Devices can be a list of devices that includes a digitizer device or a digitizer device
        itself. A device is any object that implements ``send_report()``, ``usage_page`` and
        ``usage``.
        """
        self._digitizer_device = find_device(devices, usage_page=0x0D, usage=0x02)

        # Reuse this bytearray to send reports
        # report[0] buttons 1-4 (LSB is button 1)
        # report[1:2] digitizer x: 0 to 32767
        # report[3:4] digitizer 0 y: 0 to 32767
        self._report = bytearray(5)

        # Remember the last report as well, so we can avoid sending
        # duplicate reports.
        self._last_report = bytearray(5)

        # Store settings separately before putting into report. Saves code
        # especially for buttons.
        self._buttons_state = 0
        self._x = 0
        self._y = 0

        # Send an initial report to test if HID device is ready.
        # If not, wait a bit and try once more.
        try:
            self.reset_all()
        except OSError:
            time.sleep(1)
            self.reset_all()

    def press_buttons(self, *buttons):
        """Press and hold the given buttons. """
        for button in buttons:
            self._buttons_state |= 1 << self._validate_button_number(button) - 1
        self._send()

    def release_buttons(self, *buttons):
        """Release the given buttons. """
        for button in buttons:
            self._buttons_state &= ~(1 << self._validate_button_number(button) - 1)
        self._send()

    def release_all_buttons(self):
        """Release all the buttons."""

        self._buttons_state = 0
        self._send()

    def click_buttons(self, *buttons):
        """Press and release the given buttons."""
        self.press_buttons(*buttons)
        self.release_buttons(*buttons)

    def move_pen(self, x=None, y=None):
        """Set and send the given digitizer pen values.
        The location will remain the same until changed.
        Any values left as ``None`` will not be changed.

        All values must be in the range 0 to 32767 inclusive.

        Example::

            # Change x and y values.
            gp.move_pen(x=100, y=-50)
        """
        if x is not None:
            self._x = self._validate_digitizer_value(x)
        if y is not None:
            self._y = self._validate_digitizer_value(y)
        self._send()

    def reset_all(self):
        """Release all buttons and set digitizer to middle of pad."""
        self._buttons_state = 0
        self._x = 16384
        self._y = 16384
        self._send(always=True)

    def _send(self, always=False):
        """Send a report with all the existing settings.
        If ``always`` is ``False`` (the default), send only if there have been changes.
        """
        struct.pack_into(
            "<BHH",
            self._report,
            0,
            self._buttons_state,
            self._x,
            self._y,
        )

        if always or self._last_report != self._report:
            self._digitizer_device.send_report(self._report)
            # Remember what we sent, without allocating new storage.
            self._last_report[:] = self._report

    @staticmethod
    def _validate_button_number(button):
        if not 1 <= button <= 4:
            raise ValueError("Button number must in range 1 to 4")
        return button

    @staticmethod
    def _validate_digitizer_value(value):
        if not 0 <= value <= 32767:
            raise ValueError("Digitizer value must be in range 0 to 32767")
        return value
