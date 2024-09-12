from ui import Application, MainWindow


if __name__ == "__main__":
    app = Application()

    main_window = MainWindow()
    main_window.show()

    app.exec()
