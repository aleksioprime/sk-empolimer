from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap

def make_metric(icon_path, label_text, value_text, color):
    """
    Функция-утилита для крупного показателя с иконкой.
    """
    h = QHBoxLayout()
    icon = QLabel()
    pix = QPixmap(icon_path)
    icon.setPixmap(pix.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))
    icon.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
    h.addWidget(icon)
    v = QVBoxLayout()
    lbl = QLabel(label_text)
    lbl.setFont(QFont('Arial', 12))
    val = QLabel(value_text)
    val.setFont(QFont('Arial', 26, QFont.Bold))
    val.setStyleSheet(f"color: {color};")
    v.addWidget(lbl)
    v.addWidget(val)
    h.addLayout(v)
    h.addStretch()
    return h, val

class InfoPanel(QWidget):
    """
    Красивая правая панель с крупными показателями и иконками.
    """
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)
        layout.setSpacing(18)

        # Крупные показатели
        self.temp_layout, self.temp_val = make_metric("temp.png", "Температура", "— °C", "#FF5252")
        self.hum_layout, self.hum_val = make_metric("hum.png", "Влажность", "— %", "#43A047")
        self.bat_layout, self.bat_val = make_metric("bat.png", "Батарея", "— В", "#FFB300")

        layout.addLayout(self.temp_layout)
        layout.addLayout(self.hum_layout)
        layout.addLayout(self.bat_layout)

        # Кнопка-фитолента
        self.led_btn = QPushButton("Включить фитоленту")
        self.led_btn.setFont(QFont('Arial', 14))
        self.led_btn.setCheckable(True)
        self.led_btn.setMinimumHeight(40)
        self.led_btn.setStyleSheet("""
            QPushButton { background: #1976D2; color: white; border-radius: 18px; }
            QPushButton:checked { background: #388E3C; }
        """)
        layout.addWidget(self.led_btn)
        layout.addSpacing(12)

        # Статус Arduino с иконкой
        self.status_icon = QLabel()
        self.status_icon.setPixmap(QPixmap("arduino.png").scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.status_text = QLabel("Arduino не найдена")
        self.status_text.setFont(QFont('Arial', 11))
        status_row = QHBoxLayout()
        status_row.addWidget(self.status_icon)
        status_row.addWidget(self.status_text)
        status_row.addStretch()
        layout.addLayout(status_row)

        self.setLayout(layout)
        self.setMinimumWidth(230)

    def update_values(self, t, h, batt):
        self.temp_val.setText(f"{t:.1f} °C" if t == t else "— °C")
        self.hum_val.setText(f"{h:.1f} %" if h == h else "— %")
        self.bat_val.setText(f"{batt:.2f} В" if batt == batt else "— В")

    def set_connected(self, connected: bool):
        if connected:
            self.status_icon.setPixmap(QPixmap("arduino.png").scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.status_text.setText("Arduino подключена")
            self.status_text.setStyleSheet("color: green;")
        else:
            self.status_icon.setPixmap(QPixmap("arduino_off.png").scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            self.status_text.setText("Arduino не найдена")
            self.status_text.setStyleSheet("color: red;")
