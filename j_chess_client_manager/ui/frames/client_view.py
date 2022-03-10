from enum import Enum
import inspect
from typing import Dict, Callable, Any
from uuid import uuid4, UUID

import pyperclip
from asciimatics.exceptions import NextScene, ResizeScreenError, StopApplication, InvalidFields, Highlander
from asciimatics.screen import Screen
from asciimatics.widgets import (
    Frame, Layout, Text, TextBox, Button, DropdownList, RadioButtons, Label, Divider, PopUpDialog, CheckBox
)
from j_chess_lib.ai import AI, StoreAI, DumbAI
from j_chess_lib.ai.Sample import SampleAI
from j_chess_lib.client import Client
from j_chess_lib.communication import Connection

from j_chess_client_manager.ui.utilities import get_widget_by_parameter, get_all_ais
from j_chess_client_manager.clients.ai_wrapper import wrap_ai
from j_chess_client_manager.clients import SuperProvider
from j_chess_client_manager.ui.widgets.log import LogList
from j_chess_client_manager.logging import SYSTEM_LOGGER


class ClientTypes(Enum):
    AI = 0
    Spectator = 1


IP_VALIDATOR = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
PORT_VALIDATOR = r"^([0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])$"


class ClientView(Frame):

    def __init__(self, screen, ai_adder: Callable[[SuperProvider], None], theme: str = "green"):
        height = min(max(screen.height * 2 // 3, 30), screen.height)
        width = min(max(screen.width * 2 // 3, 100), screen.width)
        super(ClientView, self).__init__(screen, height, width, hover_focus=True, title=f"Add new client +🤖")
        self._ai_adder = ai_adder
        self._convertors: Dict[str, Callable[[Any], Any]] = {}

        self.set_theme(theme=theme)

        self._type_selector = RadioButtons(options=[(x.name, x) for x in sorted(ClientTypes, key=lambda x: x.value)],
                                           label="Select the type of client to create",
                                           name="TypeSelector",
                                           on_change=self._select_type)
        self._ok_button = Button("OK", self._ok)
        self._logs = LogList(name="LogList", height=15)

        # Create the form for displaying the list of contacts.
        selection_layout = Layout([100], fill_frame=False)
        self._type_layout = Layout([100], fill_frame=False)
        self._tournament_selection_layout = Layout([100], fill_frame=False)
        self._tournament_layout = Layout([100], fill_frame=False)
        self._component_selection_layout = Layout([100], fill_frame=False)
        self._component_layout = Layout([100], fill_frame=True)
        self.add_layout(selection_layout)
        self.add_layout(self._type_layout)
        self.add_layout(self._tournament_selection_layout)
        self.add_layout(self._tournament_layout)
        self.add_layout(self._component_selection_layout)
        self.add_layout(self._component_layout)
        selection_layout.add_widget(self._type_selector)

        message_layout = Layout([100], fill_frame=False)
        bottom_layout = Layout([1, 1, 1, 1], fill_frame=False)
        self.add_layout(message_layout)
        self.add_layout(bottom_layout)
        message_layout.add_widget(Label("Use \"<<None>>\" if you want to pass none in any text field", align="^"), 0)
        message_layout.add_widget(Divider())
        message_layout.add_widget(self._logs)
        for _ in range(4):
            bottom_layout.add_widget(Divider(), _)
        bottom_layout.add_widget(self._ok_button, 0)
        bottom_layout.add_widget(Button("Cancel", self._cancel), 3)

        self.fix()

    def _build_ai_ui(self):
        self._ok_button.disabled = True

        self._type_layout.add_widget(Divider())

        for param in inspect.signature(Connection).parameters.values():
            widget, widget_converter = get_widget_by_parameter(name_base="Connection", parameter=param)
            self._convertors[widget.name] = widget_converter
            self._type_layout.add_widget(widget)

        self._type_layout.add_widget(Divider())

        tournament_selector = [None]

        def tournament_selection():
            self._tournament_layout.clear_widgets()
            selected_tournament = tournament_selector[0].value
            _editable = False
            if selected_tournament == 0:
                return
            elif selected_tournament == 1:
                _tournament_code = str(uuid4())
                try:
                    pyperclip.copy(_tournament_code)
                    self.scene.add_effect(PopUpDialog(
                        screen=self.screen,
                        text=f"Created tournament code {_tournament_code} and copied it to your clipboard",
                        buttons=["Ok"],
                        on_close=None)
                    )
                except pyperclip.PyperclipException as e:
                    self.scene.add_effect(PopUpDialog(
                        screen=self.screen,
                        text=f"Created tournament code {_tournament_code} but could not copy it to your clipboard.\n"
                             f"{e}",
                        buttons=["Ok"],
                        on_close=None)
                    )
                _editable = False
            else:
                _tournament_code = "Enter Code here"
                _editable = True

            def _validator(_uuid):
                # noinspection PyBroadException
                try:
                    _ = UUID(_uuid)
                    if _.version != 4:
                        raise Exception()
                except Exception:
                    return False
                return True

            tc_widget = Text(label="Tournament code", name="Client__Tournament_code", readonly=not _editable,
                             validator=_validator)
            tc_widget.value = _tournament_code
            self._tournament_layout.add_widget(tc_widget)
            self._tournament_layout.add_widget(Divider())
            self.fix()

        tournament_selector[0] = RadioButtons(
            options=[("Quick play", 0), ("Enter tournament code", 2), ("Generate tournament code", 1)],
            label="Tournament?",
            name="Client__Tournament_selection",
            on_change=tournament_selection
        )

        self._tournament_selection_layout.add_widget(tournament_selector[0])
        self._tournament_selection_layout.add_widget(Divider())

        available_ais = get_all_ais()
        # SYSTEM_LOGGER.info(f"Found {len(available_ais)} AI classes")

        if len(available_ais) > 0:

            ai_selector = [None]

            def setup_components():
                self._component_layout.clear_widgets()

                selected_ai = ai_selector[0].value
                if selected_ai is None:
                    self._component_layout.add_widget(Label("Please select your AI-Class above"))
                    self._ok_button.disabled = True
                else:
                    ai_parameters = inspect.signature(selected_ai).parameters.values()
                    if len(ai_parameters) > 0:
                        for ai_param in ai_parameters:
                            ai_widget, ai_widget_converter = get_widget_by_parameter(name_base=selected_ai.__name__,
                                                                                     parameter=ai_param)
                            self._convertors[ai_widget.name] = ai_widget_converter

                            self._component_layout.add_widget(ai_widget)
                    else:
                        self._component_layout.add_widget(Label("It seems like your AI does not want any parameters"
                                                                ". You are good to go. :)"))
                    self._ok_button.disabled = False

                self.fix()

            ai_selector[0] = DropdownList([("Select Here", None)] + [(x.__name__, x) for x in available_ais],
                                          label="Select your AI", name="AI__class", on_change=setup_components)
            setup_components()

            # noinspection PyTypeChecker
            self._component_selection_layout.add_widget(ai_selector[0])
            self._component_selection_layout.add_widget(Divider())
        else:
            self._component_selection_layout.add_widget(Label("You have to provide at least one implemented AI-class.\n"
                                                              "Maybe you forgot to include the package its in? If so"
                                                              "use --with-package to point to it"))

    def _build_spectator_ui(self):
        self._type_layout.add_widget(Label("Spectators are not yet supported... :("))
        self._ok_button.disabled = True

    def _select_type(self):
        self._type_layout.clear_widgets()
        self._tournament_selection_layout.clear_widgets()
        self._component_selection_layout.clear_widgets()
        self._tournament_layout.clear_widgets()
        self._component_layout.clear_widgets()
        t = self._type_selector.value
        if t == ClientTypes.AI:
            self._build_ai_ui()
        elif t == ClientTypes.Spectator:
            self._build_spectator_ui()

        self.fix()

    def reset(self):
        super(ClientView, self).reset()

    def _build_ai(self):
        from pprint import pformat
        connection_prefix = "Connection__"
        connection_parameters = {
            k[len(connection_prefix):]: self._convertors[k](v) for k, v in self.data.items() if
            str(k).startswith(connection_prefix)
        }
        ai_class = self.data["AI__class"]
        ai_parameter = {
            k[len(ai_class.__name__) + 2:]: self._convertors[k](v) for k, v in self.data.items() if
            str(k).startswith(ai_class.__name__)
        }
        connection = Connection(**connection_parameters)

        tournament_code = None if \
            self.data["Client__Tournament_selection"] <= 0 else \
            self.data["Client__Tournament_code"]

        ai = wrap_ai(ai_class, init_values=ai_parameter, need_update=self._invalidate_frame,
                     tournament_code=tournament_code)
        SYSTEM_LOGGER.info(f"Created connection {connection}; Created AI {ai}")
        client = Client(connection=connection, ai=ai, tournament_code=tournament_code)
        client.start()
        SYSTEM_LOGGER.info(
            f"Started client {client}{'' if tournament_code is None else f' for tournament {tournament_code}'}"
        )
        self._ai_adder(ai)
        # raise Exception(f"{pformat(connection_parameters)}\n{ai_class}\n{pformat(ai_parameter)}")

    def _invalidate_frame(self, *args, **kwargs):
        screen: Screen = self.screen
        screen.force_update()

    def _ok(self):
        self.save()
        try:

            t = self.data["TypeSelector"]

            if t == ClientTypes.AI:
                self._build_ai()

            raise NextScene("Main")
        except (NextScene, ResizeScreenError, StopApplication, InvalidFields, Highlander) as e:
            raise e
        except Exception as e:
            from pprint import pformat
            self.scene.add_effect(PopUpDialog(
                screen=self.screen,
                text=f"Could not create new client.\n{type(e).__name__}: {e}",
                buttons=["Ok"],
                on_close=None)
            )
            raise e

    def _cancel(self, *args, **kwargs):
        self.reset()
        raise NextScene("Main")
