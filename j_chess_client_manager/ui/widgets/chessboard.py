from typing import List, Tuple, Union, Optional

from asciimatics.constants import (
    COLOUR_GREEN, COLOUR_CYAN, COLOUR_BLACK, COLOUR_WHITE, COLOUR_BLUE, COLOUR_RED, COLOUR_YELLOW, COLOUR_MAGENTA,
    A_NORMAL, A_BOLD, A_UNDERLINE, A_REVERSE
)
from asciimatics.widgets import Widget, Frame

# noinspection PyProtectedMember
from j_chess_client_manager.clients import SuperProvider, _NoneProvider
from j_chess_client_manager.logging import SYSTEM_LOGGER

_none_provider = _NoneProvider()


class ChessBoard(Widget):

    def __init__(self, w_h_factor: float = 2):
        super().__init__("Chessboard", tab_stop=False)
        self.disabled = True
        self._w_h_factor = w_h_factor
        self._provider: Optional[SuperProvider] = None
        self._empty_board: List[List[str]] = [["" for _ in range(8)] for _ in range(8)]

    def _draw_square(self, frame: Frame, x: int, y: int, w: int, h: int, colour: int, bg: int):
        self._draw_path(frame=frame, path=[[(x, y), (x + w, y), (x + w, y + h), (x, y + h)]], colour=colour, bg=bg)

    def _draw_path(self, frame: Frame, path: List[List[Tuple[int, int]]], colour: int, bg: int):
        _x = self._x
        _y = self._y
        path = [[(x + _x, y + _y) for x, y in p] for p in path]
        frame.canvas.fill_polygon(path, colour=colour, bg=bg)

    @property
    def data_provider(self) -> Optional[SuperProvider]:
        if self._provider is None:
            return _none_provider
        return self._provider

    @data_provider.setter
    def data_provider(self, value: SuperProvider):
        self._provider = value

    def update(self, frame_no):
        frame = self.frame
        status_height = self._draw_status(frame=frame, margin=3)
        self._draw_chess_board(frame=frame, y_off=status_height)

    def _draw_status(self, frame: Frame, margin: int = 0) -> int:
        (colour, attr, background) = frame.palette["label"]
        attr_active_player = A_BOLD
        white_text = f"{self.data_provider.white_name} {self.data_provider.white_time}s"
        black_text = f"{self.data_provider.black_name} {self.data_provider.black_time}s"
        mid_text = f"Turn: {self.data_provider.turn()}"
        frame.canvas.paint(
            white_text, self._x + margin, self._y,
            colour, attr_active_player if self.data_provider.white_turn() else A_NORMAL, background
        )
        frame.canvas.paint(
            black_text, self._x + self.width - margin - len(black_text), self._y,
            colour, attr_active_player if not self.data_provider.white_turn() else A_NORMAL, background
        )
        frame.canvas.paint(
            mid_text, self._x + (self.width // 2) - (len(mid_text) // 2), self._y,
            colour, attr_active_player, background
        )
        return 1

    def _draw_chess_board(self, frame: Frame, colour_black: int = COLOUR_BLUE, colour_white: int = COLOUR_CYAN,
                          y_off: int = 0):

        current_board = None if self.data_provider is None else self.data_provider.board()
        if current_board is None:
            current_board = self._empty_board

        w, h = self.width, self._h - y_off

        board_h = h
        board_w = board_h * self._w_h_factor

        if board_w > w:
            board_w = w
            board_h = board_w // 2

        dx = int(1 * self._w_h_factor)
        dy = 1
        if dx < 1:
            dx = 1
            dy = int(1 / self._w_h_factor)

        tile_w = (board_w - 2 * dx) // 8
        tile_h = (board_h - 2 * dy) // 8

        board_w = tile_w * 8
        board_h = tile_h * 8

        offset_x = (w - board_w) // 2
        offset_y = (h - board_h) // 2 + y_off

        self._draw_square(frame=frame, x=offset_x - dx, y=offset_y - dy, w=board_w + 2 * dx, h=board_h + 2 * dy,
                          colour=COLOUR_GREEN, bg=COLOUR_BLACK)

        for x in range(8):
            for y in range(8):
                tile_colour = colour_white if (x + y) % 2 == 0 else colour_black
                _x, _y = offset_x + (x * tile_w), offset_y + y * tile_h
                self._draw_square(frame=frame, x=_x, y=_y, w=tile_w, h=tile_h, colour=tile_colour, bg=COLOUR_GREEN)
                frame.canvas.paint(
                    f"{chr(97 + x)}{8-y}", self._x + _x, self._y + _y, COLOUR_RED, A_BOLD, tile_colour
                )
                piece: str = current_board[y][x]
                if len(piece) == 1:
                    frame.canvas.paint(
                        piece.upper(), self._x + _x + tile_w//2, self._y + _y + tile_h//2,
                        COLOUR_BLACK if piece.islower() else COLOUR_WHITE, A_BOLD, tile_colour
                    )

        frame.canvas.paint(
            "Board: {}x{}; Tile: {}x{}".format(board_w, board_h, tile_w, tile_h),
            self._x + offset_x - dx, self._y + offset_y - dy, COLOUR_BLACK, A_NORMAL, COLOUR_GREEN
        )

    def reset(self):
        pass

    def process_event(self, event):
        return event

    def required_height(self, offset, width):
        return Widget.FILL_FRAME

    def value(self):
        return None
