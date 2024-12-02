"""
Main Window
===========
This is the central code for the user interface of Python for the Lab. The design of the window is specifcied in its
own .ui file, generated with Qt Designer.

"""

from pathlib import Path

import pyqtgraph as pg
from PyQt5 import uic
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMainWindow

pg.setConfigOption("background", "w")
pg.setConfigOption("foreground", "k")


class MainWindow(QMainWindow):
    """Main Window for the user interface

    Parameters
    ----------
    experiment : Experiment
        Experiment model, can be left empty just for testing. Should be instantiated and initialized before passing it.

    Attributes
    ----------
    experiment : Experiment
        The experiment object
    plot_widget : pg.PlotWidget
        Widget to hold the plot
    plot : pg.PlotWidget.plotItem
        The real plot that can be updated with new data
    start_button : QPushButton
        The start button
    """

    def __init__(self, experiment=None):
        super().__init__()
        self.experiment = experiment
        self.setWindowTitle("Scan Window")

        base_dir = Path(__file__).parent
        ui_file = base_dir / "GUI" / "main_window.ui"
        uic.loadUi(ui_file, self)

        # self.plot_widget = pg.PlotWidget(
        #     title="Plotting I vs V", labels={"left": "Current", "bottom": "Voltage"}
        # )

        pen = pg.mkPen(cosmetic=False, width=0.02, color="black")
        self.plot = self.plot_widget.plot([0], [0], pen=pen, title='I vs V')

        plot_item = self.plot_widget.getPlotItem()
        plot_item.setXRange(0, 3.3)
        plot_item.setYRange(0, 1)

        self.start_button.clicked.connect(self.start_scan)
        self.stop_button.clicked.connect(self.stop_scan)
        self.actionSave.triggered.connect(self.experiment.save_data)

        self.start_line.setText(self.experiment.config["Scan"]["start"])
        self.stop_line.setText(self.experiment.config["Scan"]["stop"])
        self.num_steps_line.setText(str(self.experiment.config["Scan"]["num_steps"]))
        self.delay_line.setText(self.experiment.config["Scan"]["delay"])
        self.out_channel_line.setText(
            str(self.experiment.config["Scan"]["channel_out"])
            )
        self.in_channel_line.setText(str(self.experiment.config["Scan"]["channel_in"]))

        self.gui_timer = QTimer()
        self.plot_timer = QTimer()

        self.plot_timer.timeout.connect(self.update_plot)
        self.gui_timer.start(50)
        self.gui_timer.timeout.connect(self.update_gui)

    def update_plot(self):
        """ This method is called periodically via a QTimer. It updates the plot to show what is currently available
        in the experiment data. If the acquisition is over, the timer is stopped (this prevents wasting computation
        resources updating a plot that does not change).

        """
        self.plot.setData(
            self.experiment.scan_range[: self.experiment.current_scan_index].m_as("V"),
            self.experiment.scan_data[: self.experiment.current_scan_index].m_as("V"),
            )

        if not self.experiment.is_running:
            self.plot_timer.stop()

    def start_scan(self):
        """ Wrapper that updates the values from the UI (start, stop, num_steps, delay, channel_in, channel_out)
        before starting the scan.

        .. Warning:: There is a bug in this code (left for students to find out and sort it). If a user changes the
            values on the UI and presses "start" again, the metadata will store the new values, not the proper ones.
        """
        start = self.start_line.text()
        stop = self.stop_line.text()
        num_steps = int(self.num_steps_line.text())
        delay = self.delay_line.text()
        channel_in = int(self.in_channel_line.text())
        channel_out = int(self.out_channel_line.text())

        self.experiment.config["Scan"].update(
            {
                "start": start,
                "stop": stop,
                "num_steps": num_steps,
                "channel_in": channel_in,
                "channel_out": channel_out,
                "delay": delay,
                }
            )
        self.experiment.start_scan()
        self.plot_widget.setLabel('bottom', f"Port: {self.experiment.config['Scan']['channel_out']}", units="V")
        self.plot_widget.setLabel('left', f"Port: {self.experiment.config['Scan']['channel_in']}", units="V")

        self.plot_timer.start(50)

    def update_gui(self):
        """ It is called on a timer to display the latest values of the applied voltage and the measured voltage.
        """
        self.out_line.setText(f"{self.experiment.voltage_out:3.2f}")
        self.measured_line.setText(f"{self.experiment.last_measured_value:3.2f}")

        if self.experiment.is_running:
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)

        else:
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)

    def stop_scan(self):
        """ Stops the scan. It is wrapping the :func:`~PFTL.model.experiment.Experiment.stop_scan` method. The only
        reason to
        do it this way is in
        case stopping a scan requires more work, for example stopping timers to prevent useless updates, etc.
        """
        self.experiment.stop_scan()
        print("UI: Stopping Scan")
