"""
Analog DAQ
==========
Class for communicating with a real device. It implements the base for communicating with the device
through a Controller. The experiment in mind is measuring the I-V curve of a diode, adding the logic
into a separate Model for the experiment may seem redundant, but incredibly useful in bigger projects.

"""
from PythonForTheLab.Controller.pftl_daq import Device
from PythonForTheLab import ur


class AnalogDaq:
    """Simple Model that reflects the logic of the MVC pattern. This model relies on the real controller
    for communicating with an Arduino based DAQ.

    Parameters
    ----------
    port : str
        See :mod:`~PythonForTheLab.Controller.pftl_daq`

    Attributes
    ----------
    port : str
        The port information
    driver : Device
        The controller
    """

    def __init__(self, port):
        self.port = port
        self.driver = Device(self.port)

    def initialize(self):
        """Initialize the driver and sets the voltage on the outputs to 0"""
        self.driver.initialize()
        self.set_output_voltage(0, ur("0V"))
        self.set_output_voltage(1, ur("0V"))

    def finalize(self):
        """Set the outputs to 0V and finalize the driver"""
        self.set_output_voltage(0, ur("0V"))
        self.set_output_voltage(1, ur("0V"))
        self.driver.finalize()

    def set_output_voltage(self, channel, volts):
        """Set the voltage to a given value on a given channel

        Parameters
        ----------
        channel : int
            The channel number
        volts : Quantity
            The value to set, a quantity using Pint
        """
        value_volts = volts.m_as("V")
        value_int = round(value_volts / 3.3 * 4095)
        self.driver.set_analog_output(channel, value_int)

    def get_output_voltage(self, channel):
        """Gets the voltage from a given output channel

        Parameters
        ----------
        channel : int
            The channel number

        Returns
        -------
        Quantity
            The voltage setpoint in the channel
        """
        voltage_bits = self.driver.get_analog_output(channel)
        voltage = voltage_bits * ur("3.3V") / 4095
        return voltage

    def get_input_voltage(self, channel):
        """Retrieve the voltage from the device

        Parameters
        ----------
        channel : int
            Channel number

        Returns
        -------
        Quantity
            The voltage read
        """
        voltage_bits = self.driver.get_analog_input(channel)
        voltage = voltage_bits * ur("3.3V") / 1023
        return voltage

    def __str__(self):
        return "Analog Daq"


if __name__ == "__main__":
    daq = AnalogDaq("/dev/ttyACM0")
    daq.initialize()
    voltage = ur("3000mV")
    daq.set_output_voltage(0, voltage)
    input_volts = daq.get_input_voltage(0)
    print(input_volts)
    daq.finalize()
