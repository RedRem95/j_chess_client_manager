from abc import ABC, abstractmethod
from enum import Enum
from typing import Type, Optional, List, Tuple

from j_chess_lib.ai import AI

from .metrics import MetricProvider
from .board import BoardProvider
from .tournament import TournamentParticipator
from .refresh import RefreshInitiator


class ClientTypes(Enum):
    AI = 0
    Spectator = 1
    Unknown = None

    def __str__(self, question_tag_len: int = 1):
        if self == self.Unknown:
            return "?" * question_tag_len
        if self == self.Spectator:
            return "Spec"
        return self.name

    @classmethod
    def max_len(cls):
        return max(len(str(x)) for x in cls)

    def fixed_represent(self):
        max_len = self.max_len()
        return f"[{self.__str__(question_tag_len=max_len):^{max_len}s}]"

    def get_class(self) -> Optional[Type]:
        if self == self.AI:
            return AI
        return None


class Typeable:

    def get_client_type(self) -> ClientTypes:
        for possible_type in ClientTypes:
            possible_type: ClientTypes
            needed_class = possible_type.get_class()
            if needed_class is not None and isinstance(self, needed_class):
                return possible_type
        return ClientTypes.Unknown


class SuperProvider(BoardProvider, TournamentParticipator, Typeable, ABC):
    pass


class _NoneProvider(SuperProvider):
    def metrics(self) -> List[Tuple[Tuple[str, str], int]]:
        return []

    @property
    def fen(self) -> Optional[str]:
        return None

    @property
    def white_name(self):
        return "---"

    @property
    def black_name(self):
        return "---"

    @property
    def white_time(self):
        return -1

    @property
    def black_time(self):
        return -1

    @property
    def need_refresh(self) -> bool:
        return False
