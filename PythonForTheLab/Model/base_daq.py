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

    def get_voltage(self, channel):
        pass

    def set_voltage(self, channel, volts):
        pass

    def finalize(self):
        pass
