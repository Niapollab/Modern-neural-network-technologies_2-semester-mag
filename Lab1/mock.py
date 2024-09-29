from core import ModelSerializer, Model
from typing import Sequence
from random import random


class RosenblattNeuron(Model):
    def predict(self, input: Sequence[float]) -> Sequence[float]:
        return [random()]

    def evaluate(
        self, input: Sequence[float], expected_output: Sequence[float]
    ) -> None:
        raise NotImplementedError()


class RosenblattNeuronSerializer(ModelSerializer[RosenblattNeuron]):
    def load(self) -> RosenblattNeuron:
        raise NotImplementedError()

    def save(self, model: RosenblattNeuron) -> None:
        raise NotImplementedError()

    def build(self) -> RosenblattNeuron:
        return RosenblattNeuron()
