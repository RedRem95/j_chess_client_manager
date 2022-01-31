from abc import ABC, abstractmethod
from typing import List, Tuple


class Piece(ABC):

    @classmethod
    @abstractmethod
    def _paths(cls) -> List[List[Tuple[float, float]]]:
        pass

    @classmethod
    def path(cls, w: int, h: int, dx: int = 0, dy: int = 0) -> List[List[Tuple[int, int]]]:
        return [
            [(int(w_f * w) + dx, int(h_f * h) + dy) for w_f, h_f in x] for x in cls._paths()
        ]


class Pawn(Piece):

    @classmethod
    def _paths(cls) -> List[List[Tuple[float, float]]]:
        return [
            [(0.33, 0.9), (0.66, 0.9), (0.66, 0.2), (0.33, 0.2)]
        ]
