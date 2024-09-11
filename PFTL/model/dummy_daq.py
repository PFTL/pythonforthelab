"""
Dummy DAQ model
===============
it only generates random values.
"""
from random import random

from PFTL import ur
from PFTL.model.base_daq import DAQBase


class DummyDaq(DAQBase):
    def get_input_voltage(self, channel):
        """Generates a randomg value in Volts

        Returns
        -------
        Quantity
            Random value
        """
        return random()*ur('V')

    def get_output_voltage(self, channel):
        """ Generates a random value in Volts
        Returns
        -------
        Quantity
            Random value
        """
        return random() * ur('V')


if __name__ == "__main__":
    daq = DummyDaq("/dev/ttyACM0")
    daq.initialize()
    voltage = 3
    daq.set_output_voltage(0, voltage)
    input_volts = daq.get_input_voltage(0)
    print(input_volts)
    daq.finalize()
