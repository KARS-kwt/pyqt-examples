import sys
import json
import serial
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import QTimer, QThread, Signal
import pyqtgraph as pg


class SerialThread(QThread):
    data_received = Signal(dict)
    # data_available = Signal(bool)
    
    def __init__(self, port, baudrate):
        super(SerialThread, self).__init__()
        # self.ser = serial.Serial(port, baudrate)
        self.ser = serial.Serial()
        self.ser.port = port
        self.ser.baudrate = baudrate
        
        
    def run(self):
        while True:
            if self.ser.in_waiting:
                data = self.ser.readline().decode('utf-8')
                try:
                    data = json.loads(data)
                    self.data_received.emit(data)
                except json.JSONDecodeError:
                    print('Invalid JSON:', data)
                    continue
                
    def start(self):
        if not self.ser.is_open:
            self.ser.open()
        super().start()
        
    def terminate(self):
        self.ser.close() 
        super().terminate() 
        
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        
        self.graphWidget1 = pg.PlotWidget()
        self.graphWidget2 = pg.PlotWidget()
        # self.startButton = QPushButton('Start')
        # self.startButton.clicked.connect(self.toggle_plot)
        self.connectButton = QPushButton('Connect')
        self.connectButton.clicked.connect(self.connect_serial)
        
        self.layout.addWidget(self.graphWidget1)
        self.layout.addWidget(self.graphWidget2)
        self.layout.addWidget(self.connectButton)
        # self.layout.addWidget(self.startButton)
        
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        
        self.time = []
        self.velocity = []
        self.x = []
        self.y = []
        
        self.graphWidget1.setBackground('w')
        self.graphWidget2.setBackground('w')
        
        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line1 = self.graphWidget1.plot(self.x, self.y, pen=pen)
        self.data_line2 = self.graphWidget2.plot(self.x, self.y, pen=pen)
        
        self.serial_thread = SerialThread('COM4', 921600)
        # connect signal data_received to update_plot_data
        self.serial_thread.data_received.connect(self.update_plot_data)
        
        
    # def toggle_plot(self):
    #     if self.serial_thread.isRunning():
    #         self.button.setText('Start')
    #     else:
    #         self.button.setText('Stop')
     
    def connect_serial(self):
        if self.serial_thread.ser.is_open:
            self.serial_thread.terminate()
            self.connectButton.setText('Connect')
        else:
            self.serial_thread.start()
            self.connectButton.setText('Disconnect')
                    
    def update_plot_data(self, data):
        self.time.append(data["time"])
        self.velocity.append(data["velocity"])
        self.x.append(data["x"])
        self.y.append(data["y"])

        self.data_line1.setData(self.time, self.velocity)
        self.data_line2.setData(self.x, self.y)
        
app = QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec())