from native import RosenblattNeuronSerializer
from ui import Application, MainWindow


if __name__ == "__main__":
    SIZE = 64

    app = Application()
    model_serializer = RosenblattNeuronSerializer(SIZE**2, bias=0)

    main_window = MainWindow(
        serializer=model_serializer,
        shape=(SIZE, SIZE),
        no_paint_millisecond=750,
        scale_factor=4,
        threshold=0.5,
        variants=(":)", ":("),
    )
    main_window.show()

    app.exec()
