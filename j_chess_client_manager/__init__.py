"""Top-level package for j-chess client manager."""
from j_chess_client_manager.logging import SYSTEM_LOGGER
from j_chess_lib import __version__ as __lib__version__, __schema_version__, __author__ as __lib__author__

__author__ = """RedRem95"""
__email__ = 'redrem@botschmot.de'
__version__ = '0.3.2'
__project_name__ = "J-Chess Client Manager"

SYSTEM_LOGGER.info(f"Running \"{__project_name__}\" Version {__version__} by {__author__}")
SYSTEM_LOGGER.info(f"Using \"j_chess_lib\" Version {__lib__version__} by {__lib__author__} "
                   f"with schema version {__schema_version__}")
