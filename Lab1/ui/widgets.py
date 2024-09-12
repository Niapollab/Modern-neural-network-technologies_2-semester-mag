from PyQt6.QtWidgets import QWidget, QMainWindow, QHBoxLayout


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Rosenblatt Neuron Emulator")
        self.setFixedSize(600, 300)

        layout = QHBoxLayout()

        widget = QWidget()
        widget.setLayout(layout)

        self.setCentralWidget(widget)
