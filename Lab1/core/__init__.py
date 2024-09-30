from abc import ABC, abstractmethod
from core.history import History
from typing import Sequence


class Predictor(ABC):
    @abstractmethod
    def predict(self, input: Sequence[float]) -> Sequence[float]:
        pass


class Evaluator(ABC):
    @abstractmethod
    def evaluate(
        self, input: Sequence[float], expected_output: Sequence[float]
    ) -> None:
        pass


class Model(Predictor, Evaluator):
    pass


class Loader[T](ABC):
    @abstractmethod
    def load(self, filename: str) -> T:
        pass


class Saver[T](ABC):
    @abstractmethod
    def save(self, filename: str, model: T) -> None:
        pass


class Factory[T](ABC):
    @abstractmethod
    def build(self) -> T:
        pass


class ModelSerializer[T](Loader[T], Saver[T], Factory[T]):
    pass


__all__ = [
    "Factory",
    "History",
    "Loader",
    "Model",
    "ModelSerializer",
    "Saver",
]
