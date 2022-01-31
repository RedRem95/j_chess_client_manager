import logging
from logging import LogRecord
from logging.handlers import QueueHandler
import queue
from typing import Tuple

from j_chess_lib import logger as _lib_logger

_lib_logger.handlers = []


class _CustomQueueHandler(QueueHandler):

    def __init__(self, code: str, log_queue):
        super().__init__(log_queue)
        self._code = code

    def enqueue(self, record: LogRecord) -> None:
        self.queue.put((self._code, record))


LOG_QUEUE = queue.Queue()


def get_log_handler(code: str) -> logging.Handler:
    """
    Return a handler pushing to the log queue so it can be displayed in the UI

    Parameters
    ----------
    code: str
        Symbols to identify this handler in the UI. Should be at max 4 symbols

    Returns
    -------
    New handler
    """
    new_handler = _CustomQueueHandler(code=code, log_queue=LOG_QUEUE)
    new_handler.setLevel(logging.INFO)
    return new_handler


_lib_logger.addHandler(get_log_handler("LIB"))
_lib_logger.setLevel(logging.DEBUG)

UI_LOGGER = logging.getLogger("Manager-UI")
UI_LOGGER.addHandler(get_log_handler("UI"))
UI_LOGGER.setLevel(logging.DEBUG)

SYSTEM_LOGGER = logging.getLogger("Backend-System")
SYSTEM_LOGGER.addHandler(get_log_handler("SYS"))
SYSTEM_LOGGER.setLevel(logging.DEBUG)

