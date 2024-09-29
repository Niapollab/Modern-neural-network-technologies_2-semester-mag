from core import Model, ModelSerializer
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QImage, QPen, QPainter
from PyQt6.QtGui import QMouseEvent, QPaintEvent
from PyQt6.QtWidgets import (
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QGroupBox,
    QLabel,
    QHBoxLayout,
    QPushButton,
)
from typing import Sequence


class Canvas(QWidget):
    BLACK = 0xFF000000
    WHITE = 0xFFFFFFFF

    __changed: pyqtSignal = pyqtSignal()
    __mouse_move: pyqtSignal = pyqtSignal(QPoint)

    __shape: tuple[int, int]
    __scale_factor: float
    __timer: QTimer
    __position: QPoint | None
    __image: QImage

    def __init__(
        self, shape: tuple[int, int], no_paint_millisecond: int, scale_factor: float
    ) -> None:
        super().__init__()
        self.setMouseTracking(True)

        self.__shape = shape
        width, height = shape
        self.setFixedSize(int(width * scale_factor), int(height * scale_factor))

        self.__position = None
        self.__scale_factor = scale_factor

        self.__timer = QTimer(self)
        self.__timer.setInterval(no_paint_millisecond)
        self.__timer.timeout.connect(self.__timeout)

        self.clear()

    @property
    def changed(self) -> pyqtBoundSignal:
        return self.__changed

    @property
    def mouse_move(self) -> pyqtBoundSignal:
        return self.__mouse_move

    @property
    def image(self) -> QImage:
        return self.__image.scaled(*self.__shape, Qt.AspectRatioMode.KeepAspectRatio)

    @property
    def features(self) -> Sequence[float]:
        image = self.image
        return [
            1.0 if image.pixel(x, y) == Canvas.BLACK else 0.0
            for y in range(image.height())
            for x in range(image.width())
        ]

    def load(self, filename: str) -> None:
        new_image = QImage(filename)
        width, height = self.__shape

        if new_image.width() != width or new_image.height() != height:
            raise ValueError(f'Invalid shape "{self.__shape}" for image "{filename}".')

        if new_image.format() != QImage.Format.Format_Mono:
            raise ValueError(
                f'Invalid image format "{new_image.format()}" for image "{filename}".'
            )

        self.__image = self.__upscale(new_image)
        self.update()

    def clear(self) -> None:
        self.__image = QImage(self.size(), QImage.Format.Format_Mono)
        self.__image.fill(Canvas.WHITE)
        self.update()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.buttons() is Qt.MouseButton.LeftButton:
            self.__position = event.position().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.buttons() is Qt.MouseButton.LeftButton:
            self.__position = None

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        next_position = event.position().toPoint()

        x, y = next_position.x(), next_position.y()
        if x >= 0 and y >= 0 and x < self.width() and y < self.height():
            self.__mouse_move.emit(next_position)

        if self.__position is None or event.buttons() != Qt.MouseButton.LeftButton:
            self.__position = None
            return

        self.__draw(self.__position, next_position)

        self.__position = next_position
        self.__timer.start()

        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.drawImage(self.rect(), self.__image)

    def __timeout(self) -> None:
        self.__timer.stop()

        self.__image = self.__upscale(self.image)
        self.update()

        self.__changed.emit()

    def __upscale(self, image: QImage) -> QImage:
        width, height = self.__shape
        return image.scaled(
            int(width * self.__scale_factor),
            int(height * self.__scale_factor),
            Qt.AspectRatioMode.KeepAspectRatio,
        )

    def __draw(self, from_point: QPoint, to_point: QPoint) -> None:
        painter = QPainter(self.__image)
        painter.setPen(
            QPen(
                Canvas.BLACK,
                self.__scale_factor,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
                Qt.PenJoinStyle.RoundJoin,
            )
        )
        painter.drawLine(from_point, to_point)


class CanvasWithInfo(QGroupBox):
    __info: QLabel

    def __init__(self, canvas: Canvas) -> None:
        super().__init__()
        self.setTitle("Canvas")

        canvas.mouse_move.connect(self.__mouse_move_in_canvas)

        self.__info = QLabel()
        clean_button = QPushButton("Clean")
        clean_button.clicked.connect(canvas.clear)

        main_layout = QVBoxLayout()
        layout = QHBoxLayout()

        layout.addWidget(self.__info)
        layout.addWidget(clean_button)

        main_layout.addWidget(canvas)
        main_layout.addLayout(layout)

        self.setLayout(main_layout)
        self.__mouse_move_in_canvas(QPoint(0, 0))

    def __mouse_move_in_canvas(self, point: QPoint) -> None:
        self.__info.setText(f"x: {point.x()}, y: {point.y()}")


class MainWindow(QMainWindow):
    __canvas: Canvas
    __model: Model
    __serializer: ModelSerializer
    __shape: tuple[int, int]

    def __init__(
        self,
        serializer: ModelSerializer,
        shape: tuple[int, int],
        no_paint_millisecond: int,
        scale_factor: float,
    ) -> None:
        super().__init__()
        self.setWindowTitle("Rosenblatt Neuron Emulator")

        self.__shape = shape
        self.__serializer = serializer
        self.__model = serializer.build()

        self.__canvas = Canvas(self.__shape, no_paint_millisecond, scale_factor)
        self.__canvas.changed.connect(self.__predict)

        layout = QVBoxLayout()
        layout.addWidget(CanvasWithInfo(self.__canvas))

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def __predict(self) -> None:
        prediction, *_ = self.__model.predict(self.__canvas.features)
        print(f"Prediction: {prediction}")
