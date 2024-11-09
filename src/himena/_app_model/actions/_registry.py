from __future__ import annotations

from typing import TypeVar, Callable
from app_model.types import Action, SubmenuItem

from himena._utils import make_function_callback

_F = TypeVar("_F", bound=Callable)


class ActionList(list[Action]):
    def append_from_fn(
        self,
        id: str,
        title: str,
        icon: str | None = None,
        menus=None,
        enablement=None,
        keybindings=None,
        need_function_callback: bool = False,
    ) -> Callable[[_F], _F]:
        def inner(fn: _F) -> _F:
            if need_function_callback:
                callback = make_function_callback(fn, id)
            else:
                callback = fn
            action = Action(
                id=id,
                title=title,
                icon=icon,
                callback=callback,
                tooltip=fn.__doc__,
                menus=menus,
                keybindings=keybindings,
                enablement=enablement,
                icon_visible_in_menu=False,
            )
            self.append(action)
            return fn

        return inner


class SubmenuList(list[tuple[str, SubmenuItem]]):
    def append_from(
        self,
        id: str,
        submenu: str,
        title: str,
        enablement=None,
        group: str | None = None,
    ) -> SubmenuList:
        self.append(
            (
                id,
                SubmenuItem(
                    submenu=submenu, title=title, enablement=enablement, group=group
                ),
            )
        )
        return self


ACTIONS = ActionList()
SUBMENUS = SubmenuList()