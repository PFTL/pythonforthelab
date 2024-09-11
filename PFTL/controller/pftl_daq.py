"""
PFTL DAQ controller
=====================

Python For The Lab revolves around controlling a simple DAQ device built on top of an Arduino.
The DAQ device is capable of generating up to two analog outputs in the range 0-3.3V and to acquire
several analog inputs.

Because of the pedagogy of the course Python for the Lab, it was assumed that the device can generate
value by value and not a sequence. This forces the developer to think on how to implement a solution
purely on Python.
"""

from time import sleep

import serial


class Device:
    """controller for the serial devices that ships with Python for the Lab.

    Parameters
    ----------
    port : str
        The port where the device is connected. Something like COM3 on Windows, or /dev/ttyACM0 on Linux

    Attributes
    ----------
    rsc : serial
        The serial communication with the device
    port : str
        The port where the device is connected, such as COM3 or /dev/ttyACM0
    """

    DEFAULTS = {
        "write_termination": "\n",
        "read_termination": "\r\n",
        "encoding": "ascii",
        "baudrate": 9600,
        "read_timeout": 1,
        "write_timeout": 1,
    }

    def __init__(self, port):
        self.port = port
        self.rsc = None

    def initialize(self):
        """Opens the serial port with the DEFAULTS."""
        self.rsc = serial.Serial(
            port=self.port,
            baudrate=self.DEFAULTS["baudrate"],
            timeout=self.DEFAULTS["read_timeout"],
            write_timeout=self.DEFAULTS["write_timeout"],
        )
        sleep(1)

    def idn(self):
        """Get the serial number from the device.

        Returns
        -------
        str
            The serial number of the device
        """

        return self.query("*IDN?")

    def get_analog_input(self, channel):
        """Get the Analog input in a channel

        Parameters
        ----------
        channel : int
            The channel
        output_value : int
            The output value in the range 0-4095

        Returns
        -------
        int
            The value
        """
        message = f"MEAS:CH{channel}?"
        ans = self.query(message)
        ans = int(ans)
        return ans

    def set_analog_output(self, channel, output_value):
        """Sets the analog output of a channel

        Parameters
        ----------
        channel : int
            The channel
        output_value : int
            The output value in the range 0-4095

        Returns
        -------
        int
            The value returned by the device
        """
        message = f"OUT:CH{channel} {output_value}"
        return self.query(message)

    def get_analog_output(self, channel):
        """Retrieves the current value set to the analog channel

        Parameters
        ----------
        channel : int
            The channel from which to retrieve the value

        Returns
        -------
        int
            The setpoint in the given channel
        """
        message = f"OUT:CH{channel}?"
        ans = self.query(message)
        ans = int(ans)
        return ans

    def query(self, message):
        """Wrapper around writing and reading from the device to make the flow easier.

        Parameters
        ----------
        message : str
            The message to send to the device

        Returns
        -------
        str
            Whatever the message outputs
        """
        message = message + self.DEFAULTS["write_termination"]
        message = message.encode(self.DEFAULTS["encoding"])
        self.rsc.write(message)
        ans = self.rsc.readline()
        ans = ans.decode(self.DEFAULTS["encoding"]).strip()
        if ans.startswith("ERROR"):
            raise Exception(f"There was an error with the message passed to the device: {ans}")
        return ans

    def finalize(self):
        """Closes the resource"""
        if self.rsc is not None:
            self.rsc.close()


if __name__ == "__main__":
    dev = Device("/dev/ttyACM0")  # <---- Remember to change the port
    dev.initialize()
    serial_number = dev.idn()
    print(f"The device serial number is: {serial_number}")
    for i in range(10):
        dev.set_analog_output(0, 4000)
        volts = dev.get_analog_input(0)
        print(f"Measured {volts}")
        sleep(0.5)
        dev.set_analog_output(0, 0)
        volts = dev.get_analog_input(0)
        print(f"Measured {volts}")
        sleep(0.5)
