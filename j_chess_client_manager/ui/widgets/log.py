import queue
from typing import List, Tuple, Set
import logging
import time

from asciimatics.widgets import Widget, Frame
from asciimatics.constants import (
    COLOUR_GREEN, COLOUR_CYAN, COLOUR_BLACK, COLOUR_WHITE, COLOUR_BLUE, COLOUR_RED, COLOUR_YELLOW, COLOUR_MAGENTA,
    A_NORMAL, A_BOLD, A_UNDERLINE, A_REVERSE
)
from asciimatics.widgets.utilities import _split_text

from j_chess_client_manager.logging import LOG_QUEUE


_LOG_LIST: List[Tuple[str, logging.LogRecord]] = []


def _update_log_list():
    while not LOG_QUEUE.empty():
        try:
            _LOG_LIST.append(LOG_QUEUE.get())
        except queue.Empty:
            break

def _get_logs(*codes: str) -> List[Tuple[str, logging.LogRecord]]:
    if codes is None or len(codes) <= 0:
        return _LOG_LIST
    return [x for x in _LOG_LIST if x[0] in codes]

def _get_codes() -> Set[str]:
    return {x[0] for x in _LOG_LIST}


class LogList(Widget):

    def __init__(self, name, height: int = 15):
        super().__init__(name, tab_stop=False)
        self._height = height
        self._fmt = '{time} [{code:^4s}-{levelname:^8s}] - {message}'
        self.date_fmt = "%Y-%m-%d %H:%M:%S"

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value: int):
        self._height = value

    def update(self, frame_no):
        _update_log_list()
        frame: Frame = self.frame
        print_logs = _get_logs()
        (colour, attr, background) = frame.palette["label"]
        frame.canvas.paint(f"Logs [{len(print_logs)}]", self._x, self._y, colour, A_UNDERLINE, background)
        print_records = print_logs[-(self._height - 1):]
        log_offset = 4

        for i, (code, record) in enumerate(print_records):
            record: logging.LogRecord
            t = time.strftime(self.date_fmt, time.localtime(record.created))
            line = _split_text(self._fmt.format(time=t, code=code, levelname=record.levelname, message=record.message),
                               width=self.width - log_offset, height=1, unicode_aware=True)[0]
            frame.canvas.paint(line, self._x + log_offset, self._y + i + 1, colour, A_NORMAL, background)

    def reset(self):
        pass

    def process_event(self, event):
        return event

    def required_height(self, offset, width):
        return self.height

    def value(self):
        return self._logs
