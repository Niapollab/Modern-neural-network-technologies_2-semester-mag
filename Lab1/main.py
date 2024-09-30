from mock import RosenblattNeuronSerializer
from ui import Application, MainWindow


if __name__ == "__main__":
    app = Application()
    model_serializer = RosenblattNeuronSerializer()

    main_window = MainWindow(
        serializer=model_serializer,
        shape=(64, 64),
        no_paint_millisecond=750,
        scale_factor=4,
        threshold=0.5,
        variants=(":)", ":("),
    )
    main_window.show()

    app.exec()
