from abc import ABC, abstractmethod
from typing import List, Tuple


class MetricProvider(ABC):

    @abstractmethod
    def metrics(self) -> List[Tuple[Tuple[str, str], int]]:
        pass
