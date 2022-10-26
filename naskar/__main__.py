from .gui.qt import MainWindow
import sys
from PyQt6.QtWidgets import QMainWindow, QApplication

app = QApplication(sys.argv)
w = MainWindow()
win = QMainWindow()
win.setWindowTitle("Counterfeit Abhijit")
win.setCentralWidget(w)
win.show()
app.exec()

