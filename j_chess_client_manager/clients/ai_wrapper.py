from abc import ABC
from typing import Type, Any, Dict, Optional, Tuple, List, Union, Callable
from uuid import UUID

from j_chess_lib.ai import StoreAI, AI
from j_chess_lib.ai.container import GameState
from j_chess_lib.communication import MoveData, MatchStatusData, MatchFormatData

from . import SuperProvider
from j_chess_client_manager.logging import SYSTEM_LOGGER


def wrap_ai(
    base_ai: Type[AI], init_values: Dict[str, Any], need_update: Callable[[Union[AI, SuperProvider]], None] = None,
    tournament_code: Optional[str] = None
) -> Union[AI, SuperProvider]:
    if need_update is None:
        def need_update(*args, **kwargs):
            pass

    class _WrappedAI(SuperProvider, base_ai):

        @property
        def tournament_code(self) -> Optional[str]:
            return tournament_code

        def __init__(self, base_init_values: Dict[str, Any]):
            super(_WrappedAI, self).__init__(**base_init_values)
            self._need_refresh: bool = False
            self._fen = None
            self._enemy_name = None
            self._i_am_white = True
            self._your_time = -1
            self._enemy_time = -1

        @property
        def white_time(self) -> int:
            return self._your_time if self._i_am_white else self._enemy_time

        @property
        def black_time(self) -> int:
            return self._your_time if not self._i_am_white else self._enemy_time

        @property
        def fen(self) -> str:
            return self._fen

        def metrics(self) -> List[Tuple[str, Any]]:
            en_passant = self.en_passant()
            castling = self.castling()
            own_metrics = [
                ("Turn", str(self.turn())),
                ("Current player", "white" if self.white_turn() else "black"),
                ("En passant", "---" if en_passant is None else en_passant),
                ("Castling white", f"King: {castling['w']['k']}; Queen: {castling['w']['q']}"),
                ("Castling black", f"King: {castling['b']['k']}; Queen: {castling['b']['q']}"),
                ("Halfmove clock", f"{self.half_moves_since_pawn()}"),
            ]
            metrics = super().metrics()
            return own_metrics + metrics

        @property
        def white_name(self):
            return self.name if self._i_am_white else self._enemy_name

        @property
        def black_name(self):
            return self.name if not self._i_am_white else self._enemy_name

        def new_match(self, match_id: UUID, enemy: str, match_format: MatchFormatData):
            self._enemy_name = enemy
            ret = super(_WrappedAI, self).new_match(match_id=match_id, enemy=enemy, match_format=match_format)
            need_update(self)
            return ret

        def finalize_match(self, match_id: UUID, status: MatchStatusData, statistics: str):
            ret = super(_WrappedAI, self).finalize_match(match_id=match_id, status=status, statistics=statistics)
            need_update(self)
            return ret

        def new_game(self, game_id: UUID, match_id: UUID, white_player: str):
            self._i_am_white = white_player == self.name
            ret = super(_WrappedAI, self).new_game(game_id=game_id, match_id=match_id, white_player=white_player)
            need_update(self)
            return ret

        def finalize_game(self, game_id: UUID, match_id: UUID, winner: Optional[str], pgn: str):
            SYSTEM_LOGGER.info(f"Game ended. {winner} ({'you' if winner == self.name else 'not you'}) won")
            ret = super(_WrappedAI, self).finalize_game(game_id=game_id, match_id=match_id, winner=winner, pgn=pgn)
            need_update(self)
            return ret

        def get_move(self, game_id: UUID, match_id: UUID, game_state: GameState) -> MoveData:
            self._fen = game_state.board_state.fen
            self._your_time = game_state.your_time
            self._enemy_time = game_state.enemy_time
            ret = super(_WrappedAI, self).get_move(game_id=game_id, match_id=match_id, game_state=game_state)
            need_update(self)
            return ret

    return _WrappedAI(base_init_values=init_values)
