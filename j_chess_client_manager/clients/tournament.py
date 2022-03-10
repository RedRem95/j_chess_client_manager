from abc import ABC
from typing import Optional


class TournamentParticipator(ABC):

    @property
    def tournament_code(self) -> Optional[str]:
        return None
