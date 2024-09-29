from collections import deque


class History[T]:
    __index: int
    __queue: deque

    def __init__(self, init_value: T) -> None:
        self.__index = 0
        self.__queue = deque([init_value])

    @property
    def current(self) -> T:
        return self.__queue[self.__index]

    @current.setter
    def current(self, value: T) -> None:
        self.__index += 1

        remove_count = len(self.__queue) - self.__index
        while remove_count > 0:
            self.__queue.pop()
            remove_count -= 1

        self.__queue.append(value)

    def undo(self) -> T:
        if self.__index > 0:
            self.__index -= 1

        return self.current

    def redo(self) -> T:
        if self.__index < len(self.__queue) - 1:
            self.__index += 1

        return self.current
