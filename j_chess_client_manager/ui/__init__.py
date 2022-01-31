from typing import Callable, Any, List, Optional

from asciimatics.exceptions import StopApplication, ResizeScreenError
from asciimatics.scene import Scene
from asciimatics.screen import Screen
from asciimatics.effects import Print, BannerText
from asciimatics.renderers import StaticRenderer, ColourImageFile

from j_chess_client_manager.ui.frames.main_frame import MainFrame
from j_chess_client_manager.ui.frames.client_view import ClientView


def setup_scenes(screen: Screen, theme: str) -> List[Scene]:
    scenes = []

    mf = MainFrame(screen=screen, theme=theme)

    scenes.append(
        Scene([mf], -1, name="Main")
    )
    scenes.append(
        Scene([ClientView(screen=screen, ai_adder=mf.add_ai, theme=theme)], -1, name="Add Client")
    )

    return scenes


def run_function_creator(start_scene: Any, theme: str = "default") -> Callable[[Screen], None]:

    def run(screen: Screen):
        scenes = setup_scenes(screen=screen, theme=theme)

        screen.play(scenes, stop_on_resize=True, repeat=False, start_scene=start_scene)

    return run
