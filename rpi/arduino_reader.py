# arduino_reader.py
from PyQt5.QtCore import pyqtSignal, QObject
import threading
import serial
import time

class ArduinoReader(QObject):
    """
    Считывает данные с Arduino в отдельном потоке.
    Автоматически переподключается при обрыве.
    """
    data_updated = pyqtSignal(float, float, float)  # temp, hum, battery
    disconnected = pyqtSignal()
    connected = pyqtSignal()

    def __init__(self, port, baudrate=9600, reconnect_interval=3):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.reconnect_interval = reconnect_interval
        self._stop = threading.Event()
        self._ser = None
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()

    def run(self):
        """
        Главный цикл: пытается подключиться и читать данные.
        """
        while not self._stop.is_set():
            try:
                self._ser = serial.Serial(self.port, self.baudrate, timeout=2)
                self.connected.emit()
                while not self._stop.is_set():
                    line = self._ser.readline().decode(errors='ignore').strip()
                    # Ждём строки вида: DATA;...;temp;hum;battery
                    if line.startswith("DATA;"):
                        try:
                            parts = line.split(";")
                            temp = float(parts[2]) if parts[2] != "?" else float('nan')
                            hum = float(parts[3]) if parts[3] != "?" else float('nan')
                            battery = float(parts[4]) if parts[4] != "?" else float('nan')
                            self.data_updated.emit(temp, hum, battery)
                        except Exception:
                            pass
            except serial.SerialException:
                self.disconnected.emit()
                time.sleep(self.reconnect_interval)
            finally:
                if self._ser:
                    try: self._ser.close()
                    except: pass
                self._ser = None

    def send_command(self, cmd):
        """
        Отправить строковую команду на Arduino (например, LED_ON).
        """
        if self._ser and self._ser.is_open:
            try:
                self._ser.write((cmd + '\n').encode())
            except Exception:
                pass

    def stop(self):
        self._stop.set()
