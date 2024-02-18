"""
Experiment Model
================
Building a model for the experiment allows developers to have a clear picture of the logic of their
experiments. It allows to build simple GUIs around them and to easily share the code with other users.

"""
import threading
from datetime import datetime
import numpy as np
import os
from time import sleep
import yaml
from PythonForTheLab import ur


class Experiment:
    """ Experiment to measure the IV curve of a diode

    Parameters
    ----------
    config_file : str
        Path to the config file. Should be a YAML file, later used by :meth:`~load_daq`
    """
    def __init__(self, config_file):
        self.config_file = config_file
        self.is_running = False  # Variable to check if the scan is running

        self.scan_range = np.array([0]) * ur('V')
        self.scan_data = np.array([0]) * ur('V')

        self.last_measured_value = 0 * ur('V')
        self.voltage_out = 0 * ur('V')

        self.keep_running = False
        self.current_scan_index = 0

    def load_config(self):
        """ Load the configuration file """
        with open(self.config_file, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        self.config = data

    def load_daq(self):
        """ Load the DAQ. Works with ``DummyDaq`` or ``AnalogDaq`` """
        name = self.config['DAQ']['name']
        port = self.config['DAQ']['port']
        if name == 'DummyDaq':
            from PythonForTheLab.Model.dummy_daq import DummyDaq
            self.daq = DummyDaq(port)

        elif name == 'AnalogDaq':
            from PythonForTheLab.Model.analog_daq import AnalogDaq
            self.daq = AnalogDaq(port)

        else:
            raise Exception('The daq specified is not yet supported')

        self.daq.initialize()

    def do_scan(self):
        """ Does a scan. This method blocks. See :meth:`~start_scan` for threaded scans. """
        if self.is_running:
            print('Scan already running')
            return
        self.is_running = True
        start = ur(self.config['Scan']['start']).m_as('V')
        stop = ur(self.config['Scan']['stop']).m_as('V')
        num_steps = int(self.config['Scan']['num_steps'])
        delay = ur(self.config['Scan']['delay'])
        self.scan_range = np.linspace(start, stop, num_steps) * ur('V')
        self.scan_data = np.zeros(num_steps) * ur('V')
        self.current_scan_index = 0
        self.keep_running = True
        for volt in self.scan_range:
            if not self.keep_running:
                break
            self.daq.set_voltage(self.config['Scan']['channel_out'], volt)
            self.voltage_out = self.daq.get_output_voltage(self.config['Scan']['channel_out'])
            measured_voltage = self.daq.get_voltage(self.config['Scan']['channel_in'])
            self.last_measured_value = measured_voltage
            self.scan_data[self.current_scan_index] = measured_voltage
            self.current_scan_index += 1
            sleep(delay.m_as('s'))
        self.is_running = False

    def start_scan(self):
        """ Start a scan on a separate thread """
        self.scan_thread = threading.Thread(target=self.do_scan)
        self.scan_thread.start()

    def stop_scan(self):
        """ Stops the scan. """
        self.keep_running = False

    def save_data(self):
        """ Save data to the folder specified in the config file. """
        data_folder = self.config['Saving']['folder']
        today_folder = f'{datetime.today():%Y-%m-%d}'
        saving_folder = os.path.join(data_folder, today_folder)
        if not os.path.isdir(saving_folder):
            os.makedirs(saving_folder)

        data = np.vstack([self.scan_range, self.scan_data]).T
        header = "Scan range in 'V', Scan Data in 'V'"

        filename = self.config['Saving']['filename']
        base_name = filename.split('.')[0]
        ext = filename.split('.')[-1]
        i = 1
        while os.path.isfile(os.path.join(saving_folder, f'{base_name}_{i:04d}.{ext}')):
            i += 1
        data_file = os.path.join(saving_folder, f'{base_name}_{i:04d}.{ext}')
        metadata_file = os.path.join(saving_folder, f'{base_name}_{i:04d}_metadata.yml')
        np.savetxt(data_file, data.m_as('V'), header=header)
        with open(metadata_file, 'w') as f:
            f.write(yaml.dump(self.config, default_flow_style=False))

    def finalize(self):
        """ Finalize the experiment, closing the communication with the device and stopping the scan """
        print('Finalizing Experiment')
        self.stop_scan()
        while self.is_running:
            sleep(.1)