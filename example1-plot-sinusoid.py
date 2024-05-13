from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import QTimer
import pyqtgraph as pg
import sys
from random import randint

class MainWindow(QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()

        self.widget = QWidget()
        self.layout = QVBoxLayout()
        
        self.graphWidget1 = pg.PlotWidget()
        self.graphWidget2 = pg.PlotWidget()
        self.button = QPushButton("Start")
        self.button.clicked.connect(self.toggle_plot)
        
        # self.setCentralWidget(self.graphWidget)
        self.layout.addWidget(self.graphWidget1)
        self.layout.addWidget(self.graphWidget2)
        self.layout.addWidget(self.button)
        
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.x = list(range(100))  # 100 time points
        self.y = [randint(0,100) for _ in range(100)]  # 100 data points

        self.graphWidget1.setBackground('w')
        self.graphWidget2.setBackground('w')

        pen = pg.mkPen(color=(255, 0, 0))
        self.data_line1 =  self.graphWidget1.plot(self.x, self.y, pen=pen)
        self.data_line2 =  self.graphWidget2.plot(self.x, self.y, pen=pen)

        self.timer = QTimer()
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.update_plot_data)
        # self.timer.start()
    
    def toggle_plot(self):
        if self.timer.isActive():
            self.timer.stop()
            self.button.setText('Start')
        else:
            self.timer.start()
            self.button.setText('Stop')
            
    def update_plot_data(self):
        self.x = self.x[1:]  
        self.x.append(self.x[-1] + 1) 

        self.y = self.y[1:]  
        self.y.append(randint(0,100)) 

        self.data_line1.setData(self.x, self.y)  
        self.data_line2.setData(self.x, self.y)  

app = QApplication(sys.argv)
main = MainWindow()
main.show()
app.exec()