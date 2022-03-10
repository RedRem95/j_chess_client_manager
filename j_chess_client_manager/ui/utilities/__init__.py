# noinspection PyUnresolvedReferences
from inspect import Parameter, _empty, isclass
from typing import Callable, Any, Tuple, List, Type, Set

from asciimatics.widgets import Text, Widget
from j_chess_lib.ai import AI


def all_subclasses(cls) -> Set[Type[AI]]:
    return set(cls.__subclasses__()).union([s for c in cls.__subclasses__() for s in all_subclasses(c)])


def get_all_ais() -> List[Type[AI]]:
    return sorted([x for x in all_subclasses(AI) if len(x.__abstractmethods__) == 0 and not x.__name__.startswith("_")],
                  key=lambda x: x.__name__)


def get_widget_by_parameter(
    name_base: str, parameter: Parameter, none_const: str = "<<None>>"
) -> Tuple[Widget, Callable[[Any], Any]]:
    name = parameter.name
    default = none_const if parameter.default is _empty or parameter.default is None else str(parameter.default)
    annotation: Any = parameter.annotation

    def annotation_convert(val: str):
        if val == none_const:
            return None
        return val

    if annotation is _empty:
        annotation = None
    else:
        if isclass(annotation):
            annotation_class = annotation

            def annotation_convert(val):
                if val == none_const:
                    return None
                # noinspection PyCallingNonCallable
                return annotation_class(val)

            annotation = annotation.__name__
        else:
            annotation = str(annotation)

    def validator(val: str):
        try:
            annotation_convert(val=val)
        except Exception as e:
            return False
        return True

    widget = Text(label=f"{name}{'' if annotation is None else f' [{annotation}]'}",
                  name=f"{name_base}__{name}", validator=validator)
    widget.value = default

    return widget, annotation_convert
