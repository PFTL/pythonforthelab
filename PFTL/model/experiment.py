"""
Experiment model
================
Building a model for the experiment allows developers to have a clear picture of the logic of their
experiments. It allows to build simple GUIs around them and to easily share the code with other users.

"""
import threading
from datetime import datetime
from pathlib import Path
from time import sleep

import numpy as np
import yaml

from PFTL import ur


class Experiment:
    """Experiment to measure the IV curve of a diode

    Parameters
    ----------
    config_file : str
        Path to the config file. Should be a YAML file, later used by :meth:`~load_daq`
    """

    def __init__(self, config_file):
        self.scan_thread = None
        self.config = {}
        self.config_file = config_file
        self.is_running = False  # Variable to check if the scan is running
        self.daq = None

        self.scan_range = np.array([0]) * ur("V")
        self.scan_data = np.array([0]) * ur("V")

        self.last_measured_value = 0 * ur("A")
        self.voltage_out = 0 * ur("V")

        self.keep_running = False
        self.current_scan_index = 0

    def load_config(self):
        """Load the configuration file"""
        with open(self.config_file, "r") as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        self.config = data

    def load_daq(self):
        """Load the DAQ. Works with ``DummyDaq`` or ``AnalogDaq``

        NOTE:
            The import of DummyDaq or AnalogDaq happen in this method. It is not best practice, but shows a pattern that
            is allowed by Python and exploited by many developers. It allows to dynamically load modules if we need them
            which opens interesting alternatives to having the full program developed.
        """
        name = self.config["DAQ"]["name"]
        port = self.config["DAQ"]["port"]
        if name == "DummyDaq":
            from PFTL.model.dummy_daq import DummyDaq
            self.daq = DummyDaq(port)

        elif name == "AnalogDaq":
            from PFTL.model.analog_daq import AnalogDaq
            self.daq = AnalogDaq(port)
        else:
            raise Exception("The daq specified is not yet supported")

        self.daq.initialize()

    def do_scan(self):
        """Does a scan. This method blocks. See :meth:`~start_scan` for threaded scans."""
        if self.is_running:
            print("Scan already running")
            return
        self.is_running = True
        start = ur(self.config["Scan"]["start"]).m_as("V")
        stop = ur(self.config["Scan"]["stop"]).m_as("V")
        num_steps = int(self.config["Scan"]["num_steps"])
        delay = ur(self.config["Scan"]["delay"])
        self.scan_range = np.linspace(start, stop, num_steps) * ur("V")
        self.scan_data = np.zeros(num_steps) * ur("A")
        self.current_scan_index = 0
        self.keep_running = True
        for volt in self.scan_range:
            if not self.keep_running:
                break
            self.daq.set_output_voltage(self.config["Scan"]["channel_out"], volt)
            self.voltage_out = self.daq.get_output_voltage(
                self.config["Scan"]["channel_out"]
            )
            measured_voltage = self.daq.get_input_voltage(self.config["Scan"]["channel_in"])
            measured_current = measured_voltage / ur(self.config['DAQ']['resistance'])
            self.last_measured_value = measured_current
            self.scan_data[self.current_scan_index] = measured_current
            self.current_scan_index += 1
            sleep(delay.m_as("s"))
        self.is_running = False

    def start_scan(self):
        """Start a scan on a separate thread"""
        self.scan_thread = threading.Thread(target=self.do_scan)
        self.scan_thread.start()

    def stop_scan(self):
        """Stops the scan.

        .. Warning::
            It does not wait for the scan to actually finish. That behavior needs to be handled by the user.

        """
        self.keep_running = False

    def save_data(self):
        """Save data to the folder specified in the config file."""

        data_folder = Path(self.config["Saving"]["folder"]).expanduser()
        today_folder = f"{datetime.today():%Y-%m-%d}"
        saving_folder = data_folder / today_folder

        saving_folder.mkdir(exist_ok=True, parents=True)

        data = np.vstack([self.scan_range.m_as('V'), self.scan_data.m_as('mA')]).T
        header = "Scan range in 'V', Scan Data in 'mA'"

        filename = Path(self.config["Saving"]["filename"])

        i = 1
        new_filename = f'{filename.stem}_{i:04d}{filename.suffix}'
        complete_path = saving_folder / new_filename
        while complete_path.exists():
            new_filename = f'{filename.stem}_{i:04d}{filename.suffix}'
            complete_path = saving_folder / new_filename
            i += 1

        metadata_file = complete_path.with_suffix('.yml')
        np.savetxt(complete_path, data, header=header)

        with open(metadata_file, "w") as f:
            f.write(yaml.dump(self.config, default_flow_style=False))

    def finalize(self):
        """Finalize the experiment, closing the communication with the device and stopping the scan"""
        print("Finalizing Experiment")
        self.stop_scan()
        while self.is_running:
            sleep(0.1)

        self.daq.finalize()
