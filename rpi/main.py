from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
import sys
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="/dev/ttyUSB0", help="Serial port Arduino (default: /dev/ttyACM0)")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    window = MainWindow(args.port)
    window.show()
    sys.exit(app.exec())
