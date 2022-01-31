from abc import ABC, abstractmethod
from typing import List, Tuple


class RefreshInitiator(ABC):

    @property
    @abstractmethod
    def need_refresh(self) -> bool:
        pass
