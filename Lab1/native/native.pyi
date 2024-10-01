from core import Model, ModelSerializer
from typing import Sequence

class RosenblattNeuron(Model):
    def __init__(self) -> None: ...
    def predict(self, input: Sequence[float]) -> Sequence[float]: ...
    def evaluate(
        self, input: Sequence[float], expected_output: Sequence[float]
    ) -> None: ...

class RosenblattNeuronSerializer(ModelSerializer[RosenblattNeuron]):
    def __init__(self) -> None: ...
    def load(self, filename: str) -> RosenblattNeuron: ...
    def save(self, filename: str, model: RosenblattNeuron) -> None: ...
    def build(self) -> RosenblattNeuron: ...
