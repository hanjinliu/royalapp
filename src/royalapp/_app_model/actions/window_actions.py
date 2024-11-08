import logging
from app_model.types import (
    KeyBindingRule,
    KeyCode,
    KeyMod,
    KeyChord,
    StandardKeyBinding,
)
from royalapp._descriptors import SaveToPath
from royalapp.consts import MenuId, StandardTypes
from royalapp.widgets import MainWindow
from royalapp.types import ClipboardDataModel, WindowState, WidgetDataModel
from royalapp._app_model._context import AppContext as _ctx
from royalapp._app_model.actions._registry import ACTIONS, SUBMENUS


_LOGGER = logging.getLogger(__name__)

EDIT_GROUP = "00_edit"
STATE_GROUP = "01_state"
MOVE_GROUP = "02_move"
EXIT_GROUP = "99_exit"
_CtrlK = KeyMod.CtrlCmd | KeyCode.KeyK


@ACTIONS.append_from_fn(
    id="close-window",
    title="Close window",
    icon="material-symbols:tab-close-outline",
    menus=[
        {"id": MenuId.WINDOW, "group": EXIT_GROUP},
        {"id": MenuId.WINDOW_TITLE_BAR, "group": EXIT_GROUP},
    ],
    keybindings=[StandardKeyBinding.Close],
    enablement=_ctx.has_sub_windows,
)
def close_current_window(ui: MainWindow) -> None:
    """Close the selected sub-window."""
    i_tab = ui.tabs.current_index
    if i_tab is None:
        return None
    i_window = ui.tabs[i_tab].current_index
    if i_window is None:
        return None
    _LOGGER.info(f"Closing window {i_window} in tab {i_tab}")
    ui.tabs[i_tab][i_window]._close_me(ui, ui._instructions.confirm)


@ACTIONS.append_from_fn(
    id="close-all-window",
    title="Close all windows in tab",
    menus=[{"id": MenuId.WINDOW, "group": EXIT_GROUP}],
    enablement=_ctx.has_sub_windows,
)
def close_all_windows_in_tab(ui: MainWindow) -> None:
    """Close all sub-windows in the current tab."""
    if area := ui.tabs.current():
        win_modified = [win for win in area if win.is_modified]
        if len(win_modified) > 0 and ui._instructions.confirm:
            _modified_msg = "\n".join([f"- {win.title}" for win in win_modified])
            if not ui.exec_confirmation_dialog(
                f"Some windows are modified:\n{_modified_msg}\nClose without saving?"
            ):
                return None
        area.clear()


@ACTIONS.append_from_fn(
    id="duplicate-window",
    title="Duplicate window",
    enablement=_ctx.is_active_window_exportable,
    menus=[
        {"id": MenuId.WINDOW, "group": EDIT_GROUP},
        {"id": MenuId.WINDOW_TITLE_BAR, "group": EDIT_GROUP},
    ],
    keybindings=[KeyBindingRule(primary=KeyMod.CtrlCmd | KeyMod.Shift | KeyCode.KeyD)],
    need_function_callback=True,
)
def duplicate_window(model: WidgetDataModel) -> WidgetDataModel:
    """Duplicate the selected sub-window."""
    if model.title is not None:
        if (
            (last_part := model.title.rsplit(" ", 1)[-1]).startswith("[")
            and last_part.endswith("]")
            and last_part[1:-1].isdigit()
        ):
            nth = int(last_part[1:-1])
            model.title = model.title.rsplit(" ", 1)[0] + f" [{nth + 1}]"
        else:
            model.title = model.title + " [1]"
    return model


@ACTIONS.append_from_fn(
    id="rename-window",
    title="Rename window",
    menus=[
        {"id": MenuId.WINDOW, "group": EDIT_GROUP},
        {"id": MenuId.WINDOW_TITLE_BAR, "group": EDIT_GROUP},
    ],
    enablement=_ctx.has_sub_windows,
    keybindings=[KeyBindingRule(primary=KeyChord(_CtrlK, KeyCode.F2))],
)
def rename_window(ui: MainWindow) -> None:
    """Rename the title of the window."""
    i_tab = ui.tabs.current_index
    if i_tab is None:
        return None
    if (i_win := ui._backend_main_window._current_sub_window_index()) is not None:
        ui._backend_main_window._rename_window_at(i_tab, i_win)


@ACTIONS.append_from_fn(
    id="copy-path-to-clipboard",
    title="Copy path to clipboard",
    menus=[
        {"id": MenuId.WINDOW, "group": EDIT_GROUP},
        {"id": MenuId.WINDOW_TITLE_BAR, "group": EDIT_GROUP},
    ],
    enablement=_ctx.has_sub_windows,
    keybindings=[
        KeyBindingRule(primary=KeyChord(_CtrlK, KeyMod.CtrlCmd | KeyCode.KeyC))
    ],
)
def copy_path_to_clipboard(ui: MainWindow) -> ClipboardDataModel:
    """Copy the path of the current window to the clipboard."""
    if window := ui.current_window:
        if isinstance(sv := window.save_behavior, SaveToPath):
            return ClipboardDataModel(value=sv.path, type=StandardTypes.TEXT)
    return None


@ACTIONS.append_from_fn(
    id="copy-data-to-clipboard",
    title="Copy data to clipboard",
    menus=[
        {"id": MenuId.WINDOW, "group": EDIT_GROUP},
        {"id": MenuId.WINDOW_TITLE_BAR, "group": EDIT_GROUP},
    ],
    enablement=_ctx.has_sub_windows | _ctx.is_active_window_exportable,
)
def copy_data_to_clipboard(ui: MainWindow) -> ClipboardDataModel:
    """Copy the data of the current window to the clipboard."""
    if window := ui.current_window:
        return window.to_model().to_clipboard_data_model()
    return None


@ACTIONS.append_from_fn(
    id="minimize-window",
    title="Minimize window",
    menus=[
        {"id": MenuId.WINDOW, "group": STATE_GROUP},
        {"id": MenuId.WINDOW_TITLE_BAR, "group": STATE_GROUP},
    ],
    enablement=_ctx.has_sub_windows,
)
def minimize_current_window(ui: MainWindow) -> None:
    """Minimize the window"""
    if window := ui.current_window:
        window.state = WindowState.MIN


@ACTIONS.append_from_fn(
    id="maximize-window",
    title="Maximize window",
    menus=[
        {"id": MenuId.WINDOW, "group": STATE_GROUP},
        {"id": MenuId.WINDOW_TITLE_BAR, "group": STATE_GROUP},
    ],
    enablement=_ctx.has_sub_windows,
)
def maximize_current_window(ui: MainWindow) -> None:
    if window := ui.current_window:
        window.state = WindowState.MAX


@ACTIONS.append_from_fn(
    id="toggle-full-screen",
    title="Toggle full screen",
    menus=[
        {"id": MenuId.WINDOW, "group": STATE_GROUP},
        {"id": MenuId.WINDOW_TITLE_BAR, "group": STATE_GROUP},
    ],
    keybindings=[KeyBindingRule(primary=KeyCode.F11)],
    enablement=_ctx.has_sub_windows,
)
def toggle_full_screen(ui: MainWindow) -> None:
    if window := ui.current_window:
        if window.state is WindowState.MAX:
            window.state = WindowState.NORMAL
        else:
            window.state = WindowState.MAX


@ACTIONS.append_from_fn(
    id="unset-anchor",
    title="Unanchor window",
    menus=[MenuId.WINDOW_ANCHOR, MenuId.WINDOW_TITLE_BAR_ANCHOR],
    enablement=_ctx.has_sub_windows,
)
def unset_anchor(ui: MainWindow) -> None:
    """Unset the anchor of the window if exists."""
    if window := ui.current_window:
        window.anchor = None


@ACTIONS.append_from_fn(
    id="anchor-window-top-left",
    title="Anchor window to top-left corner",
    menus=[MenuId.WINDOW_ALIGN, MenuId.WINDOW_TITLE_BAR_ANCHOR],
    enablement=_ctx.has_sub_windows,
)
def anchor_at_top_left(ui: MainWindow) -> None:
    """Anchor the window at the top-left corner of the current window position."""
    if window := ui.current_window:
        window.anchor = "top-left"


@ACTIONS.append_from_fn(
    id="anchor-window-top-right",
    title="Anchor window to top-right corner",
    menus=[MenuId.WINDOW_ALIGN, MenuId.WINDOW_TITLE_BAR_ANCHOR],
    enablement=_ctx.has_sub_windows,
)
def anchor_at_top_right(ui: MainWindow) -> None:
    """Anchor the window at the top-right corner of the current window position."""
    if window := ui.current_window:
        window.anchor = "top-right"


@ACTIONS.append_from_fn(
    id="anchor-window-bottom-left",
    title="Anchor window to bottom-left corner",
    menus=[MenuId.WINDOW_ALIGN, MenuId.WINDOW_TITLE_BAR_ANCHOR],
    enablement=_ctx.has_sub_windows,
)
def anchor_at_bottom_left(ui: MainWindow) -> None:
    """Anchor the window at the bottom-left corner of the current window position."""
    if window := ui.current_window:
        window.anchor = "bottom-left"


@ACTIONS.append_from_fn(
    id="anchor-window-bottom-right",
    title="Anchor window to bottom-right corner",
    menus=[MenuId.WINDOW_ALIGN, MenuId.WINDOW_TITLE_BAR_ANCHOR],
    enablement=_ctx.has_sub_windows,
)
def anchor_at_bottom_right(ui: MainWindow) -> None:
    """Anchor the window at the bottom-right corner of the current window position."""
    if window := ui.current_window:
        window.anchor = "bottom-right"


@ACTIONS.append_from_fn(
    id="minimize-other-windows",
    title="Minimize other windows",
    menus=[
        {"id": MenuId.WINDOW, "group": STATE_GROUP},
        {"id": MenuId.WINDOW_TITLE_BAR, "group": STATE_GROUP},
    ],
    enablement=_ctx.has_sub_windows,
)
def minimize_others(ui: MainWindow):
    """Minimize all sub-windows except the current one."""
    if area := ui.tabs.current():
        cur_window = area.current()
        for window in area:
            if cur_window is window:
                continue
            window.state = WindowState.MIN


@ACTIONS.append_from_fn(
    id="show-all-windows",
    title="Show all windows",
    menus=[{"id": MenuId.WINDOW, "group": STATE_GROUP}],
    enablement=_ctx.has_sub_windows,
)
def show_all_windows(ui: MainWindow):
    """Show all sub-windows in the current tab."""
    if area := ui.tabs.current():
        for window in area:
            if window.state is WindowState.MIN:
                window.state = WindowState.NORMAL


@ACTIONS.append_from_fn(
    id="full-screen-in-new-tab",
    title="Full screen in new tab",
    enablement=_ctx.has_sub_windows,
    menus=[
        {"id": MenuId.WINDOW, "group": STATE_GROUP},
        {"id": MenuId.WINDOW_TITLE_BAR, "group": STATE_GROUP},
    ],
)
def full_screen_in_new_tab(ui: MainWindow) -> None:
    """Move the selected sub-window to a new tab and make it full screen."""
    if area := ui.tabs.current():
        index = area.current_index
        if index is None:
            return
        window = area.pop(index)
        ui.add_tab(window.title)
        new_window = ui.tabs[-1].add_widget(window.widget, title=window.title)
        new_window.state = WindowState.FULL


@ACTIONS.append_from_fn(
    id="window-expand",
    title="Expand (+20%)",
    enablement=_ctx.has_sub_windows,
    menus=[MenuId.WINDOW_RESIZE, MenuId.WINDOW_TITLE_BAR_RESIZE],
    keybindings=[StandardKeyBinding.ZoomIn],
)
def window_expand(ui: MainWindow) -> None:
    """Expand (increase the size of) the current window."""
    if window := ui.current_window:
        window._set_rect(window.rect.resize_relative(1.2, 1.2))


@ACTIONS.append_from_fn(
    id="window-shrink",
    title="Shrink (-20%)",
    enablement=_ctx.has_sub_windows,
    menus=[MenuId.WINDOW_RESIZE, MenuId.WINDOW_TITLE_BAR_RESIZE],
    keybindings=[StandardKeyBinding.ZoomOut],
)
def window_shrink(ui: MainWindow) -> None:
    """Shrink (reduce the size of) the current window."""
    if window := ui.current_window:
        window._set_rect(window.rect.resize_relative(1 / 1.2, 1 / 1.2))


_CtrlAlt = KeyMod.CtrlCmd | KeyMod.Alt


@ACTIONS.append_from_fn(
    id="align-window-left",
    title="Align window to left",
    enablement=_ctx.has_sub_windows,
    menus=[MenuId.WINDOW_ALIGN, MenuId.WINDOW_TITLE_BAR_ALIGN],
    keybindings=[KeyBindingRule(primary=_CtrlAlt | KeyCode.LeftArrow)],
)
def align_window_left(ui: MainWindow) -> None:
    """Align the window to the left edge of the tab area."""
    if window := ui.current_window:
        window._set_rect(window.rect.align_left())


@ACTIONS.append_from_fn(
    id="align-window-right",
    title="Align window to right",
    enablement=_ctx.has_sub_windows,
    menus=[MenuId.WINDOW_ALIGN, MenuId.WINDOW_TITLE_BAR_ALIGN],
    keybindings=[KeyBindingRule(primary=_CtrlAlt | KeyCode.RightArrow)],
)
def align_window_right(ui: MainWindow) -> None:
    """Align the window to the right edge of the tab area."""
    if window := ui.current_window:
        window._set_rect(window.rect.align_right(ui.area_size))


@ACTIONS.append_from_fn(
    id="align-window-top",
    title="Align window to top",
    enablement=_ctx.has_sub_windows,
    menus=[MenuId.WINDOW_ALIGN, MenuId.WINDOW_TITLE_BAR_ALIGN],
    keybindings=[KeyBindingRule(primary=_CtrlAlt | KeyCode.UpArrow)],
)
def align_window_top(ui: MainWindow) -> None:
    """Align the window to the top edge of the tab area."""
    if window := ui.current_window:
        window._set_rect(window.rect.align_top(ui.area_size))


@ACTIONS.append_from_fn(
    id="align-window-bottom",
    title="Align window to bottom",
    enablement=_ctx.has_sub_windows,
    menus=[MenuId.WINDOW_ALIGN, MenuId.WINDOW_TITLE_BAR_ALIGN],
    keybindings=[KeyBindingRule(primary=_CtrlAlt | KeyCode.DownArrow)],
)
def align_window_bottom(ui: MainWindow) -> None:
    """Align the window to the bottom edge of the tab area."""
    if window := ui.current_window:
        window._set_rect(window.rect.align_bottom(ui.area_size))


@ACTIONS.append_from_fn(
    id="align-window-center",
    title="Align window to center",
    enablement=_ctx.has_sub_windows,
    menus=[MenuId.WINDOW_ALIGN, MenuId.WINDOW_TITLE_BAR_ALIGN],
    keybindings=[KeyBindingRule(primary=_CtrlAlt | KeyCode.Space)],
)
def align_window_center(ui: MainWindow) -> None:
    """Align the window to the center of the tab area."""
    if window := ui.current_window:
        window._set_rect(window.rect.align_center(ui.area_size))


@ACTIONS.append_from_fn(
    id="tile-windows",
    title="Tile windows",
    enablement=_ctx.has_sub_windows,
    menus=[MenuId.WINDOW_ALIGN],
)
def tile_windows(ui: MainWindow) -> None:
    """Tile all the windows."""
    if area := ui.tabs.current():
        area.tile_windows()


SUBMENUS.append_from(
    id=MenuId.WINDOW,
    submenu=MenuId.WINDOW_RESIZE,
    title="Resize",
    enablement=_ctx.has_sub_windows,
    group=MOVE_GROUP,
)
SUBMENUS.append_from(
    id=MenuId.WINDOW,
    submenu=MenuId.WINDOW_ALIGN,
    title="Align",
    enablement=_ctx.has_sub_windows,
    group=MOVE_GROUP,
)
SUBMENUS.append_from(
    id=MenuId.WINDOW,
    submenu=MenuId.WINDOW_ANCHOR,
    title="Anchor",
    enablement=_ctx.has_sub_windows,
    group=MOVE_GROUP,
)
SUBMENUS.append_from(
    id=MenuId.WINDOW_TITLE_BAR,
    submenu=MenuId.WINDOW_TITLE_BAR_RESIZE,
    title="Resize",
    enablement=_ctx.has_sub_windows,
    group=MOVE_GROUP,
)
SUBMENUS.append_from(
    id=MenuId.WINDOW_TITLE_BAR,
    submenu=MenuId.WINDOW_TITLE_BAR_ALIGN,
    title="Align",
    enablement=_ctx.has_sub_windows,
    group=MOVE_GROUP,
)
SUBMENUS.append_from(
    id=MenuId.WINDOW_TITLE_BAR,
    submenu=MenuId.WINDOW_TITLE_BAR_ANCHOR,
    title="Anchor",
    enablement=_ctx.has_sub_windows,
    group=MOVE_GROUP,
)
