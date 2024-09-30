from core import Model, ModelSerializer
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtBoundSignal, pyqtSignal
from PyQt6.QtGui import (
    QImage,
    QPen,
    QPainter,
    QMouseEvent,
    QPaintEvent,
    QShortcut,
    QKeySequence
)
from PyQt6.QtWidgets import (
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QGroupBox,
    QLabel,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
)
from typing import Sequence
from core.history import History


class Canvas(QWidget):
    BLACK = 0xFF000000
    WHITE = 0xFFFFFFFF

    __changed: pyqtSignal = pyqtSignal()
    __mouse_move: pyqtSignal = pyqtSignal(QPoint)

    __shape: tuple[int, int]
    __scale_factor: float
    __timer: QTimer
    __position: QPoint | None
    __scaled_image: QImage
    __history: History[QImage]

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

        undo_shrotcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undo_shrotcut.activated.connect(self.__undo)

        redo_shrotcut = QShortcut(QKeySequence("Ctrl+Y"), self)
        redo_shrotcut.activated.connect(self.__redo)

        self.clear()

    @property
    def changed(self) -> pyqtBoundSignal:
        return self.__changed

    @property
    def mouse_move(self) -> pyqtBoundSignal:
        return self.__mouse_move

    @property
    def image(self) -> QImage:
        return self.__scaled_image.scaled(
            *self.__shape, Qt.AspectRatioMode.KeepAspectRatio
        )

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

        self.__history.current = new_image
        self.__scaled_image = self.__upscale(new_image)

        self.update()

    def clear(self) -> None:
        self.__scaled_image = QImage(self.size(), QImage.Format.Format_Mono)
        self.__scaled_image.fill(Canvas.WHITE)

        self.__history = History(self.image)
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
        painter.drawImage(self.rect(), self.__scaled_image)

    def __undo(self) -> None:
        self.__scaled_image = self.__upscale(self.__history.undo())
        self.update()

    def __redo(self) -> None:
        self.__scaled_image = self.__upscale(self.__history.redo())
        self.update()

    def __timeout(self) -> None:
        self.__timer.stop()

        image = self.image
        self.__history.current = image
        self.__scaled_image = self.__upscale(image)

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
        painter = QPainter(self.__scaled_image)
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
    __canvas: Canvas
    __current_canvas: int

    def __init__(self, canvas: Canvas) -> None:
        super().__init__()
        self.setTitle("Canvas")

        self.__current_canvas = 0
        self.__info = QLabel()
        self.__canvas = canvas

        clean_button = QPushButton("Clean")
        clean_button.clicked.connect(canvas.clear)

        main_layout = QVBoxLayout()
        layout = QHBoxLayout()

        layout.addWidget(self.__info)
        layout.addWidget(clean_button)

        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(canvas)
        main_layout.addLayout(layout)

        self.setLayout(main_layout)

        open_shrotcut = QShortcut(QKeySequence("Ctrl+O"), self)
        open_shrotcut.activated.connect(self.__open)

        save_shrotcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_shrotcut.activated.connect(self.__save)

        canvas.mouse_move.connect(self.__mouse_move_in_canvas)
        self.__mouse_move_in_canvas(QPoint(0, 0))

    def __mouse_move_in_canvas(self, point: QPoint) -> None:
        self.__info.setText(f"x: {point.x()}, y: {point.y()}")

    def __open(self) -> None:
        fullpath, *_ = QFileDialog.getOpenFileName(
            self, "Open Canvas", "", "PNG (*.png)"
        )
        if not fullpath:
            return

        self.__canvas.load(fullpath)

    def __save(self) -> None:
        filename = f"Canvas {self.__current_canvas + 1}"
        fullpath, *_ = QFileDialog.getSaveFileName(
            self, "Save Canvas", filename, "PNG (*.png)"
        )
        if not fullpath:
            return

        self.__current_canvas += 1
        self.__canvas.image.save(fullpath)


class ModelInfo(QGroupBox):
    __serializer: ModelSerializer
    __current_model: int
    __threshold: float
    __variants: tuple[str, str]
    __model: Model
    __raw_info: QLabel
    __last_input: Sequence[float]
    __last_prediction: float
    __correct_button: QPushButton
    __incorrect_button: QPushButton

    def __init__(
        self,
        serializer: ModelSerializer,
        threshold: float,
        variants: tuple[str, str],
    ) -> None:
        super().__init__()
        self.setTitle("Model")

        self.__threshold = threshold
        self.__variants = variants
        self.__current_model = 0

        self.__serializer = serializer
        self.__model = serializer.build()

        self.__info = QLabel()
        self.__info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        font = self.__info.font()
        font.setPointSize(72)
        self.__info.setFont(font)

        self.__raw_info = QLabel()
        self.__raw_info.setFixedHeight(25)
        self.__raw_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__last_prediction = 0.0
        self.__update_prediction()

        main_layout = QVBoxLayout()
        layout = QHBoxLayout()

        self.__correct_button = QPushButton("✓")
        self.__incorrect_button = QPushButton("X")

        self.__correct_button.clicked.connect(self.__evaluate_correct)
        self.__incorrect_button.clicked.connect(self.__evaluate_incorrect)

        for button in (self.__correct_button, self.__incorrect_button):
            button.setFixedHeight(30)
            button.setEnabled(False)

        layout.addWidget(self.__correct_button)
        layout.addWidget(self.__incorrect_button)

        main_layout.addWidget(self.__info)
        main_layout.addWidget(self.__raw_info)
        main_layout.addLayout(layout)

        open_shrotcut = QShortcut(QKeySequence("Ctrl+Shift+O"), self)
        open_shrotcut.activated.connect(self.__open)

        save_shrotcut = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        save_shrotcut.activated.connect(self.__save)

        self.setLayout(main_layout)

    @property
    def output(self) -> float:
        return 1.0 if self.__last_prediction >= self.__threshold else 0.0

    @property
    def variant(self) -> str:
        return (
            self.__variants[1]
            if self.__last_prediction >= self.__threshold
            else self.__variants[0]
        )

    def predict(self, input: Sequence[float]) -> None:
        self.__correct_button.setEnabled(True)
        self.__incorrect_button.setEnabled(True)

        prediction, *_ = self.__model.predict(input)

        self.__last_input = input
        self.__last_prediction = prediction

        self.__update_prediction()

    def __update_prediction(self) -> None:
        self.__info.setText(f"{self.variant}")
        self.__raw_info.setText(f"Prediction: {self.__last_prediction:.2f}")

    def __evaluate_correct(self) -> None:
        expected_output = self.output
        self.__model.evaluate(self.__last_input, [expected_output])

        self.predict(self.__last_input)

    def __evaluate_incorrect(self) -> None:
        expected_output = 1.0 - self.output
        self.__model.evaluate(self.__last_input, [expected_output])

        self.predict(self.__last_input)

    def __open(self) -> None:
        fullpath, *_ = QFileDialog.getOpenFileName(
            self, "Open Model", "", "Model (*.mdl)"
        )
        if not fullpath:
            return

        self.__model = self.__serializer.load(fullpath)

    def __save(self) -> None:
        filename = f"Model {self.__current_model + 1}"
        fullpath, *_ = QFileDialog.getSaveFileName(
            self, "Save Model", filename, "Model (*.mdl)"
        )
        if not fullpath:
            return

        self.__current_model += 1
        self.__serializer.save(fullpath, self.__model)


class MainWindow(QMainWindow):
    __canvas: Canvas
    __model_info: ModelInfo
    __shape: tuple[int, int]

    def __init__(
        self,
        serializer: ModelSerializer,
        shape: tuple[int, int],
        no_paint_millisecond: int,
        scale_factor: float,
        threshold: float,
        variants: tuple[str, str],
    ) -> None:
        super().__init__()
        self.setWindowTitle("Rosenblatt Neuron Emulator")

        self.__model_info = ModelInfo(serializer, threshold, variants)
        self.__canvas = Canvas(shape, no_paint_millisecond, scale_factor)
        self.__canvas.changed.connect(self.__predict)

        layout = QHBoxLayout()
        layout.addWidget(CanvasWithInfo(self.__canvas))
        layout.addWidget(self.__model_info)

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)

    def __predict(self) -> None:
        self.__model_info.predict(self.__canvas.features)
