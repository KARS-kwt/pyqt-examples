import sys
import random
import json
from paho.mqtt import client as mqtt_client
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import QTimer, QThread, Signal
import pyqtgraph as pg

broker = 'localhost'
port = 1883
topic = "python/mqtt"
client_id = f'subscribe-{random.randint(0, 100)}'

class MQTTThread(QThread):
    data_received = Signal(dict)
    # data_available = Signal(bool)
    
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
        
        self.widget = QWidget()
        self.layout = QVBoxLayout()
        
        self.graphWidget1 = pg.PlotWidget()
        self.graphWidget2 = pg.PlotWidget()
        self.connectButton = QPushButton('Connect')
        self.connectButton.clicked.connect(self.run_mqtt)
        
        self.layout.addWidget(self.graphWidget1)
        self.layout.addWidget(self.graphWidget2)
        self.layout.addWidget(self.connectButton)
        
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        
        self.start_time = None
        self.time = []
        self.velocity_x = []
        self.velocity_y = []
        self.position_x = []
        self.position_y = []
        
        self.graphWidget1.setBackground('w')
        self.graphWidget2.setBackground('w')
        
        pen = pg.mkPen(color=(255, 0, 0))
        pen2 = pg.mkPen(color=(0, 255, 0))
        self.data_line_velx = self.graphWidget1.plot(self.time, self.velocity_x, pen=pen)
        self.data_line_vely = self.graphWidget1.plot(self.time, self.velocity_y, pen=pen2)
        self.data_line_pos = self.graphWidget2.plot(self.position_x, self.position_y, pen=pen)
        
        self.mqtt_thread = MQTTThread(client_id, broker, port, topic)
        self.mqtt_thread.data_received.connect(self.update_plot_data)
        
             
    def run_mqtt(self):
        if self.mqtt_thread.isRunning():
            self.mqtt_thread.terminate()
            self.connectButton.setText('Connect')
        else:
            self.mqtt_thread.start()
            self.connectButton.setText('Disconnect')
                    
    def update_plot_data(self, data):
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
        
        self.data_line_velx.setData(self.time, self.velocity_x)
        self.data_line_vely.setData(self.time, self.velocity_y)
        self.data_line_pos.setData(self.position_x, self.position_y)
        
app = QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec())