from PyQt6.QtWidgets import QApplication
import sys


class Application(QApplication):
    def __init__(self) -> None:
        super().__init__(sys.argv)
