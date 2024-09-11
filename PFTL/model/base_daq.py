"""
Base DAQ
========
Base class for the DAQ objects. It keeps track of the functions that every new model should implement.
This helps keeping the code organized and to maintain downstream compliancy.
"""


class DAQBase:
    def __init__(self, port):
        self.port = port

    def initialize(self):
        pass

    def idn(self):
        pass

    def get_input_voltage(self, channel):
        pass

    def set_output_voltage(self, channel, volts):
        pass

    def get_output_voltage(self, channel):
        pass

    def finalize(self):
        pass

    def __str__(self):
        return f"DAQ on port: {self.port}"