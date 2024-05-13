import sys
import random
import json
from paho.mqtt import client as mqtt_client
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QHBoxLayout, QWidget, QPushButton,
                               QProgressBar, QLabel)
from PySide6.QtCore import QTimer, QThread, Signal
from PySide6.QtGui import QIcon
import pyqtgraph as pg
from qt_material import apply_stylesheet

# mqtt settings
broker = 'localhost'
port = 1883
topic = "python/mqtt"
client_id = f'subscribe-{random.randint(0, 100)}'

"""
    Use QThread to run MQTT client in the background, and allow gui to refresh without blocking
"""
class MQTTThread(QThread):
    data_received = Signal(dict)
    
    def __init__(self, client_id, broker, port, topic):
        super(MQTTThread, self).__init__()
        self.client = mqtt_client.Client(mqtt_client.CallbackAPIVersion.VERSION2, client_id)
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.start_time = None
        
    def run(self):
        self.client.connect(self.broker, self.port)
        self.client.loop_forever()
        
    def on_connect(self, client, userdata, flags, rc, properties):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.subscribe(self.topic)
            self.start_time = None
        else:
            print("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, msg):
        message_json = msg.payload.decode()
        message = json.loads(message_json)
        if self.start_time is None:
            self.start_time = message["time"]
        self.data_received.emit(message)   
                
    def start(self):
        # adjust reconnection to mqtt
        super().start()
        
    def terminate(self):
        # adjust disconnection to mqtt
        super().terminate() 
        
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowIcon(QIcon('kars.png'))       
        self.setWindowTitle("MQTT Subscriber Plotter") 
        # Widgets
        self.graphWidget1 = pg.PlotWidget()
        self.graphWidget2 = pg.PlotWidget()
        self.connectButton = QPushButton('Connect')
        self.connectButton.clicked.connect(self.run_mqtt)
        battery_layout, self.battery_widget = self.create_horizontal_layout("Battery Level", self.create_progress_bar())
        op_mode_layout, self.op_mode_widget = self.create_horizontal_layout("Operating Mode", QLabel("N/A", self))
        
        # Layouts
        self.layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        top_layout.addLayout(battery_layout)
        top_layout.addLayout(op_mode_layout)
        top_layout.setStretch(0, 1)
        top_layout.setStretch(1, 1)
        self.layout.addLayout(top_layout)
        self.layout.addWidget(self.graphWidget1)
        self.layout.addWidget(self.graphWidget2)
        self.layout.addWidget(self.connectButton)
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
                
        # Data
        self.start_time = None
        self.time = []
        self.velocity_x = []
        self.velocity_y = []
        self.position_x = []
        self.position_y = []

        # Plot elements
        pen_red = pg.mkPen(color=(255, 0, 0), width=3)
        pen_green = pg.mkPen(color=(0, 255, 0), width=3)
        self.data_line_velx = self.graphWidget1.plot(self.time, self.velocity_x, pen=pen_red)
        self.data_line_vely = self.graphWidget1.plot(self.time, self.velocity_y, pen=pen_green)
        self.graphWidget1.setYRange(-2, 2)
        self.graphWidget1.showGrid(x=True, y=True, alpha=0.3)
        
        pen_yellow = pg.mkPen(color=(255,255,51), width=3)
        self.data_line_pos = self.graphWidget2.plot(self.position_x, self.position_y, pen=pen_yellow)
        self.pos_end = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 255))
        self.graphWidget2.addItem(self.pos_end)
        self.graphWidget2.setXRange(-2, 2)
        self.graphWidget2.setYRange(-2, 2)
        self.graphWidget2.setAspectLocked(True, ratio=1)
        self.graphWidget2.showGrid(x=True, y=True, alpha=0.3)

        # MQTT thread
        self.mqtt_thread = MQTTThread(client_id, broker, port, topic)
        self.mqtt_thread.data_received.connect(self.update_data)
    
    # qt helper functions    
    def create_horizontal_layout(self, label_text, widget):
        label = QLabel(label_text, self)
        layout = QHBoxLayout()
        layout.addWidget(label)
        layout.addWidget(widget)
        return layout, widget
    
    def create_progress_bar(self):
        progress_bar = QProgressBar(self)
        progress_bar.setMaximum(100)
        return progress_bar
    
    def clear_data(self):
        self.time = []
        self.velocity_x = []
        self.velocity_y = []
        self.position_x = []
        self.position_y = []

        self.data_line_velx.clear()
        self.data_line_vely.clear()
        self.data_line_pos.clear()      
        
    def run_mqtt(self):
        if self.mqtt_thread.isRunning():
            self.mqtt_thread.terminate()
            self.connectButton.setText('Connect')
        else:
            self.mqtt_thread.start()
            self.clear_data()
            self.connectButton.setText('Disconnect')
                    
    def update_data(self, data):
        # called when new data is received via mqtt, and refreshes the gui data
        self.time.append((data["time"] - self.mqtt_thread.start_time) * 1000)
        self.position_x.append(data["position"]["x"])
        self.position_y.append(data["position"]["y"])
        self.velocity_x.append(data["velocity"]["x"])
        self.velocity_y.append(data["velocity"]["y"])
        
        # keep last 200 only
        self.time = self.time[-200:]
        self.velocity_x = self.velocity_x[-200:]
        self.velocity_y = self.velocity_y[-200:]
        self.position_x = self.position_x[-200:]
        self.position_y = self.position_y[-200:]
        
        # refresh gui data
        self.data_line_velx.setData(self.time, self.velocity_x)
        self.data_line_vely.setData(self.time, self.velocity_y)
        self.data_line_pos.setData(self.position_x, self.position_y)
        self.pos_end.setData([self.position_x[-1]], [self.position_y[-1]])
        
        self.battery_widget.setValue(data.get("battery", 80))
        self.op_mode_widget.setText(data.get("op_mode", "Normal"))
        
app = QApplication(sys.argv)
apply_stylesheet(app, theme='dark_red.xml')
main = MainWindow()
main.show()
sys.exit(app.exec())