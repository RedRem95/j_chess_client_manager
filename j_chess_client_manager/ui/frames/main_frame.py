import queue
from typing import List, Tuple, Optional

from asciimatics.exceptions import NextScene, StopApplication
from asciimatics.widgets import (
    Frame, ListBox, Widget, Button, Layout, Divider, MultiColumnListBox, Label, VerticalDivider, TextBox
)
from asciimatics.parsers import AnsiTerminalParser

from j_chess_client_manager.ui.widgets.chessboard import ChessBoard
from j_chess_client_manager.ui.widgets.log import LogList
from j_chess_client_manager.clients import SuperProvider


class MainFrame(Frame):
    def __init__(self, screen, theme: str = "default"):
        super(MainFrame, self).__init__(screen=screen, height=screen.height, width=screen.width,
                                        on_load=self._on_load,
                                        hover_focus=True,
                                        can_scroll=False,
                                        has_border=True,
                                        title="♛ J-Chess Client-Manager 🤖")

        self.set_theme(theme=theme)

        self._ais: List[SuperProvider] = [
            # wrap_ai(base_ai=SampleAI, init_values={"white_name": "Gray"}),
            # wrap_ai(base_ai=SampleAI, init_values={})
        ]

        # Initialize widgets
        self._ai_list = ListBox(
            Widget.FILL_FRAME,
            options=[],
            name="AIs",
            add_scroll_bar=True,
            on_change=self._on_pick,
            on_select=self._edit)
        self._chessboard = ChessBoard()
        self._edit_button = Button("Edit", self._edit)
        self._delete_button = Button("Delete", self._delete)
        self._metrics = MultiColumnListBox(
            Widget.FILL_FRAME,
            columns=["33%", "67%"],
            titles=["Metric", "Value"],
            add_scroll_bar=True,
            options=[],
            parser=AnsiTerminalParser(),
            space_delimiter="|",
        )
        self._metrics._is_tab_stop = False
        self._logs = LogList(name="LogList", height=15)

        # Add widgets to layout
        main_layout = Layout([49, 1, 100, 1, 49], fill_frame=True)
        log_layout = Layout([100], fill_frame=False)
        button_layout = Layout([1, 1, 1, 1], fill_frame=False)
        self.add_layout(main_layout)
        self.add_layout(log_layout)
        self.add_layout(button_layout)

        main_layout.add_widget(Label("Connected clients"), 0)
        main_layout.add_widget(Label("Metrics", align=">"), 4)
        main_layout.add_widget(Divider(), 0)
        main_layout.add_widget(Divider(), 4)
        main_layout.add_widget(self._ai_list, 0)
        main_layout.add_widget(self._chessboard, 2)
        main_layout.add_widget(self._metrics, 4)
        main_layout.add_widget(VerticalDivider(), 1)
        main_layout.add_widget(VerticalDivider(), 3)

        log_layout.add_widget(Divider())
        log_layout.add_widget(self._logs)

        button_layout.add_widget(Divider(), 0)
        button_layout.add_widget(Divider(), 1)
        button_layout.add_widget(Divider(), 2)
        button_layout.add_widget(Divider(), 3)
        button_layout.add_widget(Button("Add", self._add), 0)
        button_layout.add_widget(self._edit_button, 1)
        button_layout.add_widget(self._delete_button, 2)
        button_layout.add_widget(Button("Quit", self._quit), 3)
        self.fix()
        self._on_pick()
        self._set_ais()

    def add_ai(self, new_ai: SuperProvider):
        self._ais.append(new_ai)
        self._set_ais()

    def _set_ais(self):
        def get_name(_x):
            try:
                return _x.name
            except AttributeError:
                return _x.__class__.__name__
        def get_tournament_code(_x: SuperProvider):
            try:
                return f" [{_x.tournament_code}]" if _x.tournament_code else ""
            except AttributeError:
                return ""
        self._ai_list.options = [
            (f"{x.get_client_type().fixed_represent()} {get_name(x)}{get_tournament_code(x)}", x) for x in self._ais
        ]

    @property
    def current_client(self) -> Optional[SuperProvider]:
        return self._ai_list.value

    def _set_metrics(self, metrics: List[Tuple[Tuple[str, str], int]]):
        self._metrics.options = metrics

    def _on_pick(self):
        val: SuperProvider = self.current_client
        self._edit_button.disabled = True
        self._delete_button.disabled = val is None

        self._set_metrics([] if val is None else [(tuple(str(y) for y in x), i) for i, x in enumerate(val.metrics())])
        self._chessboard.data_provider = val

    def _update(self, frame_no):
        super()._update(frame_no)

    def _on_load(self, new_value=None):
        pass

    def _add(self):
        raise NextScene("Add Client")

    def _edit(self):
        pass

    def _delete(self):
        pass

    @staticmethod
    def _quit():
        raise StopApplication("User pressed quit")
