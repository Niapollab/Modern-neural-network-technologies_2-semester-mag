from core import ModelSerializer, Model
from typing import Sequence
from random import random


class RosenblattNeuron(Model):
    def predict(self, input: Sequence[float]) -> Sequence[float]:
        return [random()]

    def evaluate(
        self, input: Sequence[float], expected_output: Sequence[float]
    ) -> None:
        pass


class RosenblattNeuronSerializer(ModelSerializer[RosenblattNeuron]):
    def load(self, filename: str) -> RosenblattNeuron:
        return RosenblattNeuron()

    def save(self, filename: str, model: RosenblattNeuron) -> None:
        pass

    def build(self) -> RosenblattNeuron:
        return RosenblattNeuron()
