from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QWidget, QFrame
from camera_widget import CameraWidget
from info_panel import InfoPanel
from arduino_reader import ArduinoReader

class MainWindow(QMainWindow):
    """
    Главное окно приложения: слева камера, справа панель с данными и кнопкой.
    """
    def __init__(self, serial_port):
        super().__init__()
        self.setWindowTitle("EmPolimer | Камера и показания Arduino")

        # Главный layout: камера + вертикальная линия + инфо-панель
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)

        self.camera = CameraWidget()
        self.info_panel = InfoPanel()
        main_layout.addWidget(self.camera, stretch=4)

        # Вертикальный разделитель
        vline = QFrame()
        vline.setFrameShape(QFrame.Shape.VLine)
        vline.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(vline)

        main_layout.addWidget(self.info_panel, stretch=1)
        self.setCentralWidget(main_widget)
        self.setMinimumSize(900, 500)
        self.showMaximized()

        # Подключаем ArduinoReader (поток)
        self.arduino = ArduinoReader(serial_port)
        self.arduino.data_updated.connect(self.info_panel.update_values)
        self.arduino.connected.connect(lambda: self.info_panel.set_connected(True))
        self.arduino.disconnected.connect(lambda: self.info_panel.set_connected(False))
        self.info_panel.set_connected(False)

        # Кнопка управления лентой
        self.info_panel.led_btn.clicked.connect(self.toggle_led)

    def toggle_led(self, checked):
        """
        Отправляет команду на Arduino: включить или выключить ленту.
        """
        if checked:
            self.info_panel.led_btn.setText("Выключить фитоленту")
            self.arduino.send_command("LED_ON")
        else:
            self.info_panel.led_btn.setText("Включить фитоленту")
            self.arduino.send_command("LED_OFF")

    def closeEvent(self, event):
        """
        Завершение работы — останавливаем поток Arduino.
        """
        self.arduino.stop()
        event.accept()
