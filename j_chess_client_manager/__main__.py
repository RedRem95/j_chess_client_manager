"""Console script for j_chess_client_manager."""
from . import SYSTEM_LOGGER
import argparse
import sys
from typing import Any
import importlib

from asciimatics.screen import Screen
from asciimatics.exceptions import ResizeScreenError
from asciimatics.widgets.utilities import THEMES

from .ui import run_function_creator


def main():

    available_themes = list(THEMES.keys())
    default_theme = available_themes[0]

    parser = argparse.ArgumentParser(prog="j_chess_client_manager",
                                     description="Program to manage your clients and see their playstate")

    parser.add_argument("--theme", dest="theme", choices=available_themes, required=False, default=default_theme,
                        help=f"Set the theme used for the application [Default: \"{default_theme}\"]")
    parser.add_argument("--with-package", dest="package", type=str, nargs="+", required=False, default=tuple(),
                        help="Set package to be included. Should point to a package that then imports your AI so it can"
                             "be detected")

    args = parser.parse_args()

    for package in args.package:
        package: str
        import os
        import sys
        SYSTEM_LOGGER.info(os.getcwd())
        sys.path.append(os.getcwd())
        try:
            importlib.import_module(package)
            SYSTEM_LOGGER.info(f"Imported \"{package}\"")
        except ModuleNotFoundError:
            SYSTEM_LOGGER.info(f"Package \"{package}\" could not be imported")

    last_scene: Any = None

    while True:
        try:
            Screen.wrapper(run_function_creator(start_scene=last_scene, theme=args.theme),
                           catch_interrupt=False, arguments=[])
            return 0
        except KeyboardInterrupt:
            return 1
        except ResizeScreenError as e:
            last_scene = e.scene
            pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
