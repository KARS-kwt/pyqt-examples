import cv2
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtCore import QTimer

"""
This Python script demonstrates how to capture video from a webcam using OpenCV and display it in a Qt application. 

The video modes are as follows:
- 'color': The video is displayed in color.
- 'gray': The video is converted to grayscale using OpenCV's cvtColor function with the COLOR_BGR2GRAY flag.
- 'bw': The video is converted to black & white. This mode is not fully implemented in the provided code excerpt.
"""

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(1000.0 / 30) # 30 fps
        
        layout = QVBoxLayout()
        
        self.label = QLabel()
        layout.addWidget(self.label)
        
        self.color_button = QPushButton('Color')
        self.color_button.clicked.connect(lambda: self.set_mode('color'))
        layout.addWidget(self.color_button)
        
        self.gray_button = QPushButton('Gray')
        self.gray_button.clicked.connect(lambda: self.set_mode('gray'))
        layout.addWidget(self.gray_button)
        
        self.bw_button = QPushButton('B/W')
        self.bw_button.clicked.connect(lambda: self.set_mode('bw'))
        layout.addWidget(self.bw_button)
        
        self.setLayout(layout)
        
        self.mode = 'color'
        
        
    def set_mode(self, mode):
        self.mode = mode
        
        
    def update_frame(self):
        ret, frame = self.cap.read()

        if ret:
            if self.mode == 'gray':
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                image_format = QImage.Format_Grayscale8
            elif self.mode == 'bw':
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                _, frame = cv2.threshold(frame, 128, 255, cv2.THRESH_BINARY)
                image_format = QImage.Format_Grayscale8
            else: 
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image_format = QImage.Format_RGB888
            # Convert from OpenCV to QImage format
            image = QImage(frame, frame.shape[1], frame.shape[0], frame.strides[0], image_format)
            self.label.setPixmap(QPixmap.fromImage(image))

app = QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())