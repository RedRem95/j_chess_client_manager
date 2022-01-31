from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Optional


class BoardProvider(ABC):

    @property
    @abstractmethod
    def fen(self) -> Optional[str]:
        pass

    # rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2

    def board(self) -> List[List[str]]:
        fen = self.fen
        if fen is None or len(fen) <= 0:
            return [["" for _ in range(8)] for _ in range(8)]
        ret: List[List[str]] = [[]]
        board = self.fen.split(" ")[0]
        for c in board:
            try:
                n = int(c)
                for _ in range(n):
                    ret[-1].append("")
            except ValueError:
                if c == "/":
                    ret.append([])
                else:
                    ret[-1].append(c)

        return ret

    def turn(self) -> int:
        try:
            return int(self.fen.split(" ")[-1])
        except (ValueError, AttributeError, KeyError):
            return -1

    def white_turn(self) -> bool:
        try:
            return self.fen.split(" ")[1].lower() == "w"
        except (ValueError, AttributeError, KeyError):
            return True

    def castling(self) -> Dict[str, Dict[str, bool]]:
        try:
            castling = self.fen.split(" ")[2]
            return {
                "w": {"k": "K" in castling, "q": "Q" in castling},
                "b": {"k": "k" in castling, "q": "q" in castling}
            }
        except (ValueError, AttributeError, KeyError):
            return {
                "w": {"k": False, "q": False},
                "b": {"k": False, "q": False}
            }

    def en_passant(self) -> Optional[str]:
        try:
            en_passant = self.fen.split(" ")[3]
            return None if en_passant == "-" else en_passant.strip()
        except (ValueError, AttributeError, KeyError):
            return ""

    def half_moves_since_pawn(self) -> int:
        try:
            return int(self.fen.split(" ")[4])
        except (ValueError, AttributeError, KeyError):
            return -1

    @property
    @abstractmethod
    def white_name(self):
        pass

    @property
    @abstractmethod
    def black_name(self):
        pass

    @property
    @abstractmethod
    def white_time(self):
        pass

    @property
    @abstractmethod
    def black_time(self):
        pass
