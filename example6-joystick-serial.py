import sys
import pygame
import time
import serial
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QProgressBar, QWidget, QLabel
from PySide6.QtCore import QTimer, Qt
import random
import json

pygame.init()
pygame.joystick.init()

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()


        
        
        while True:
            try:
                self.joystick = pygame.joystick.Joystick(0)
                self.joystick.init()
                print("Joystick connected successfully.")
                break
            except pygame.error:
                print("Joystick not connected. Will try again in 10 seconds.")
                time.sleep(10)
        
        while True:
            try:
                self.serial_port = serial.Serial('/dev/ttyUSB0', 921600)
                break
            except:
                print("Serial port not connected. Will try again in 10 seconds.")
                time.sleep(10)
                
        self.layout = QVBoxLayout()
        
        self.throttle_layout = QHBoxLayout()
        self.left_bar = QProgressBar()
        self.left_bar.setOrientation(Qt.Vertical)
        self.throttle_layout.addWidget(self.left_bar)
        self.right_bar = QProgressBar()
        self.right_bar.setOrientation(Qt.Vertical)
        self.throttle_layout.addWidget(self.right_bar)
        self.layout.addLayout(self.throttle_layout)
        
        self.turbo_label = QLabel("Turbo Mode: OFF")
        self.layout.addWidget(self.turbo_label)

        self.heading_label = QLabel("Heading: 0°")
        self.layout.addWidget(self.heading_label)
        
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)
        
        self.joystick_timer = QTimer()
        self.joystick_timer.timeout.connect(self.update_bars)
        self.joystick_timer.start(20)
        
        self.heading_timer = QTimer()
        self.heading_timer.timeout.connect(self.update_heading)
        self.heading_timer.start(20)


    def update_bars(self):
        pygame.event.pump()

        left_y =  - self.joystick.get_axis(1) / 2 
        right_y = - self.joystick.get_axis(4) / 2
        r1_button = self.joystick.get_button(5)
        
        turbo_mode = (r1_button == 1)
        if turbo_mode:
            left_y *= 2
            right_y *= 2
            self.turbo_label.setText("Turbo Mode: ON")
        else:
            self.turbo_label.setText("Turbo Mode: OFF")
            
        # Scale from [-1, 1] to [0, 100]
        self.left_bar.setValue((left_y + 1) / 2 * 100)
        self.right_bar.setValue((right_y + 1) / 2 * 100)
        
        command = {
            "left_speed": left_y,
            "right_speed": right_y,
            "turbo": turbo_mode
        }
        json_command = json.dumps(command)
        # print(f"Sending to serial: {json_command}")
        self.serial_port.write((json_command + '\n').encode('utf-8'))
        
    def update_heading(self):
        if self.serial_port.in_waiting > 0:
            line = self.serial_port.readline().decode('utf-8').strip()
            try:
                heading_data = json.loads(line)
                heading = heading_data["heading"]
                self.heading_label.setText(f"Heading: {heading}°")
                # print(f"Received from serial: {json.dumps(heading_data)}")
            except:
                print("Invalid JSON:", line)
                return

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())