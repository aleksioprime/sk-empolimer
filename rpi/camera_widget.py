# camera_widget.py
from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
from picamera2 import Picamera2

class CameraWidget(QLabel):
    """
    Виджет для показа live-видео с PiCamera2.
    """
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.picam = Picamera2()
        config = self.picam.create_preview_configuration(
            main={"format": "RGB888", "size": (640, 480)}
        )
        self.picam.configure(config)
        self.picam.start()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        """
        Захватывает изображение с камеры и выводит на QLabel.
        """
        frame = self.picam.capture_array("main")
        if frame is not None:
            rgb = frame[..., ::-1]
            h, w, ch = frame.shape
            img = QImage(rgb.tobytes(), w, h, ch * w, QImage.Format_RGB888)
            pix = QPixmap.fromImage(img)
            self.setPixmap(pix.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))

    def resizeEvent(self, event):
        """
        При изменении размера окна — подгоняем изображение.
        """
        self.update_frame()
        super().resizeEvent(event)
