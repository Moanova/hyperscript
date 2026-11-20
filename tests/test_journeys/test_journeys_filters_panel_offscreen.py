# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_journeys_filters_panel_offscreen.py
# Version      : 1
# Date         : 2026-11-20
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen tests TSK33 (session 10): the "Journeys" view hosts the same
filters side panel as "Relationships" (Journey + Agent combos, mirrors of the
Display menu - choosing a journey activates it, TSK30 4.1) but WITHOUT the
block list; both panels stay in sync on filter changes and on journey/agent
CRUD.
"""

import pytest

pytest.importorskip("PySide6")

try:
    from PySide6.QtWidgets import QApplication, QDialog
    from PySide6.QtCore import Qt, QPointF, QEvent
    from PySide6.QtGui import QMouseEvent
except Exception as e:  # libGL missing, no display, ...
    pytest.skip(f"Qt not usable in this environment: {e}", allow_module_level=True)

import ui.main_window as mw_module
from ui.main_window import MainWindow
from ui.widgets.filters_side_panel import (
    FiltersSidePanel, SidePanelSplitter, SidePanelHandle, PANEL_WIDTH_PX, PANEL_MIN_WIDTH_PX,
)
from config.user_state_loader import get as get_user_state


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(autouse=True)
def _isolated_user_state(tmp_path, monkeypatch):
    """TSK35: redirect user_state.json reads/writes to a temp file (the real
    one is tracked in git)."""
    import config.user_state_loader as usl
    monkeypatch.setattr(usl, "_STATE_PATH", str(tmp_path / "user_state.json"))
    monkeypatch.setattr(usl, "_state", {})


def make_main_window():
    mw = MainWindow()
    mw._create_project()  # FN005: create + open + _init_workspace
    return mw


def close_main_window(mw):
    mw._teardown_workspace()
    mw.project_service.set_modified(False)  # avoid the quit confirmation dialog
    mw.close()


def combo_datas(combo):
    return [combo.itemData(i) for i in range(combo.count())]


def test_journeys_page_hosts_filters_panel_without_block_list(qapp):
    """TSK33: the "Journeys" page has a SidePanelSplitter with a
    FiltersSidePanel (show_block_list=False -> no block list, the area below
    the filters stays empty); "Relationships" keeps its block list."""
    mw = make_main_window()
    try:
        assert isinstance(mw.journeys_splitter, SidePanelSplitter)
        assert isinstance(mw.journeys_panel, FiltersSidePanel)
        assert mw.journeys_panel.show_block_list is False
        assert mw.journeys_panel.block_list is None
        assert mw.journeys_workspace.parentWidget() is mw.journeys_splitter
        assert mw.journeys_panel.parentWidget() is mw.journeys_splitter
        # the "Relationships" panel keeps its block list
        rel_panel = mw.relationships_workspace.panel
        assert isinstance(rel_panel, FiltersSidePanel)
        assert rel_panel.show_block_list is True
        assert rel_panel.block_list is not None
    finally:
        close_main_window(mw)


def test_panel_slot_keeps_its_width_on_resize(qapp):
    """TSK33 + TSK35: both map views get the side panel at side_panel_width_px
    (set via set_panel_width at init); on resize the slot keeps its width (the
    view absorbs the extra space) - no exposed splitter strip on the right."""
    mw = make_main_window()
    try:
        mw.resize(1280, 800)
        mw.show()
        qapp.processEvents()
        # activate the "Journeys" tab (default tab is "Agents", TSK30 1.1) so
        # the page's splitter is visible and gets its real width
        mw._on_tab_changed("Journeys")
        qapp.processEvents()
        sp = mw.journeys_splitter
        assert sp.sizes()[-1] == PANEL_WIDTH_PX
        panel = mw.journeys_panel
        assert panel.width() == PANEL_WIDTH_PX
        assert panel.x() + panel.width() == sp.width()
        mw._on_tab_changed("Relationships")
        qapp.processEvents()
        rel_sp = mw.relationships_workspace._splitter
        rel_sp.set_panel_width(PANEL_WIDTH_PX)
        qapp.processEvents()
        assert rel_sp.sizes()[-1] == PANEL_WIDTH_PX
        mw.hide()
    finally:
        close_main_window(mw)


def test_journeys_panel_journey_combo_activates_journey_and_syncs_panels(qapp):
    """TSK33 + TSK30 (4.1): choosing a journey in the "Journeys" panel combo
    activates it (FN026) and enables the filter (FN029); both panels' combos
    then show it (mirror of Display > Journey)."""
    mw = make_main_window()
    try:
        mw._new_journey()  # second journey (FN023, real menu path)
        nm = mw._current_narrative_map()
        j2 = nm.journey[-1]
        mw.journeys_panel.journey_combo.setCurrentIndex(2)  # items: All journeys, j1, j2
        assert nm.get_active_journey() is j2
        assert mw.journey_filter_active is True
        assert mw.journeys_panel.journey_combo.currentData() == j2.id
        assert mw.relationships_workspace.journey_combo.currentData() == j2.id
        mw.journeys_panel.journey_combo.setCurrentIndex(0)  # back to "All journeys"
        assert mw.journey_filter_active is False
        assert nm.get_active_journey() is j2  # the active journey is unchanged
    finally:
        close_main_window(mw)


def test_display_menu_filter_updates_both_panels(qapp):
    """TSK33: the Display menu path pushes the filter state to both side
    panels (journey + agent) and to the "Journeys" workspace."""
    mw = make_main_window()
    try:
        mw._new_journey()
        nm = mw._current_narrative_map()
        j2 = nm.journey[-1]
        mw._activate_journey(j2)  # Display > Journey path
        assert mw.journeys_panel.journey_combo.currentData() == j2.id
        assert mw.relationships_workspace.journey_combo.currentData() == j2.id
        agent = mw.create_agent_usecase.execute(lb="Zoo")
        mw._set_agent_filter(agent.id)  # Display > Agent path
        assert mw.journeys_workspace.agent_filter_agent_id == agent.id
        assert mw.journeys_panel.agent_combo.currentData() == agent.id
        assert mw.relationships_workspace.agent_combo.currentData() == agent.id
        mw._set_agent_filter(None)
        assert mw.journeys_panel.agent_combo.currentData() is None
        assert mw.relationships_workspace.agent_combo.currentData() is None
    finally:
        close_main_window(mw)


def test_journey_crud_resyncs_both_panels(qapp):
    """TSK33: a journey CRUD resyncs the journey combos of both panels."""
    mw = make_main_window()
    try:
        n0 = mw.journeys_panel.journey_combo.count()
        mw._new_journey()
        assert mw.journeys_panel.journey_combo.count() == n0 + 1
        assert combo_datas(mw.journeys_panel.journey_combo) == \
            combo_datas(mw.relationships_workspace.journey_combo)
    finally:
        close_main_window(mw)


def test_agent_crud_resyncs_both_panels(qapp, monkeypatch):
    """TSK33: an agent CRUD resyncs the agent combos of both panels (gap
    fixed: previously only the Display menu was rebuilt). Dialogs mocked."""
    mw = make_main_window()
    try:
        class FakeAgentDialog:
            def __init__(self, *args, **kwargs):
                pass

            def exec(self):
                return QDialog.DialogCode.Accepted

            def get_values(self):
                return {"lb": "NewGuy", "typ": "Character", "note": "", "content": ""}

        class FakeMessageBox:
            class StandardButton:
                Yes = 1
                No = 2

            @staticmethod
            def question(*args, **kwargs):
                return FakeMessageBox.StandardButton.Yes

        monkeypatch.setattr(mw_module, "AgentDialog", FakeAgentDialog)
        monkeypatch.setattr(mw_module, "QMessageBox", FakeMessageBox)
        n0 = mw.journeys_panel.agent_combo.count()
        mw._new_agent()  # FN031, real handler with mocked dialog
        project = mw.project_service.current_project
        new_agent = next(a for a in project.agent if a.lb == "NewGuy")
        assert mw.journeys_panel.agent_combo.count() == n0 + 1
        assert mw.relationships_workspace.agent_combo.count() == n0 + 1
        assert new_agent.id in combo_datas(mw.journeys_panel.agent_combo)
        assert combo_datas(mw.journeys_panel.agent_combo) == \
            combo_datas(mw.relationships_workspace.agent_combo)
        mw._delete_agent(agent=new_agent)  # FN031/RG033, confirmation mocked
        assert mw.journeys_panel.agent_combo.count() == n0
        assert mw.relationships_workspace.agent_combo.count() == n0
    finally:
        close_main_window(mw)


def test_journeys_grid_covers_visible_area_on_tab_show(qapp):
    """TSK34 (retour 2): the "Journeys" grid is redrawn when the tab is first
    shown (showEvent -> _draw_grid), no user action needed."""
    mw = make_main_window()
    try:
        mw.resize(1280, 800)
        mw.show()
        qapp.processEvents()
        mw._on_tab_changed("Journeys")
        qapp.processEvents()
        ws = mw.journeys_workspace
        rect = ws.mapToScene(ws.viewport().rect()).boundingRect()
        xs = [l.line().x1() for l in ws.grid_lines if l.line().x1() == l.line().x2()]
        ys = [l.line().y1() for l in ws.grid_lines if l.line().y1() == l.line().y2()]
        assert xs and ys
        assert min(xs) <= rect.left() and max(xs) >= rect.right()
        assert min(ys) <= rect.top() and max(ys) >= rect.bottom()
        mw.hide()
    finally:
        close_main_window(mw)


# ---------------------------------------------------------------------
# TSK35 (session 10): resizable + collapsible side panel
# ---------------------------------------------------------------------

def test_panel_resizable_width_persisted_and_synced_between_views(qapp):
    """TSK35: the side panel is resizable via the splitter; the width is
    emitted (panel_width_changed), clamped to the min, persisted at app level
    (user_state.json) and synced to the other map view."""
    mw = make_main_window()
    try:
        mw.resize(1280, 800)
        mw.show()
        qapp.processEvents()
        mw._on_tab_changed("Journeys")
        qapp.processEvents()
        sp_j = mw.journeys_splitter
        sp_r = mw.relationships_workspace._splitter
        received = []
        sp_j.panel_width_changed.connect(lambda w: received.append(w))
        sp_j.set_panel_width(320)
        assert sp_j.sizes()[-1] == 320
        assert mw.journeys_panel.width() == 320
        assert 320 in received
        # persisted at app level (user_state.json, redirected to tmp by the fixture)
        assert get_user_state("side_panel_width_px") == 320
        # synced to the "Relationships" view splitter (hidden: size clamped to
        # the splitter width, but the expanded width is synced...)
        assert sp_r._expanded_width == 320
        # ...and applied when that view becomes visible
        mw._on_tab_changed("Relationships")
        qapp.processEvents()
        assert sp_r.sizes()[-1] == 320
        # minimum width respected
        mw._on_tab_changed("Journeys")
        qapp.processEvents()
        sp_j.set_panel_width(10)
        assert sp_j.sizes()[-1] == PANEL_MIN_WIDTH_PX
        mw.hide()
    finally:
        close_main_window(mw)


def test_handle_click_collapses_and_expands_panel(qapp):
    """TSK35: the splitter handle is a custom chevron handle; a click without
    drag collapses the panel (slot 0, panel hidden), another click expands it
    back at the last width."""
    mw = make_main_window()
    try:
        mw.resize(1280, 800)
        mw.show()
        qapp.processEvents()
        mw._on_tab_changed("Journeys")
        qapp.processEvents()
        sp = mw.journeys_splitter
        sp.set_panel_width(260)
        handle = sp.handle(1)
        assert isinstance(handle, SidePanelHandle)
        assert sp.collapsed is False
        press = QMouseEvent(QEvent.Type.MouseButtonPress, QPointF(2, 100), QPointF(2, 100),
                            Qt.MouseButton.LeftButton, Qt.MouseButton.LeftButton,
                            Qt.KeyboardModifier.NoModifier)
        release = QMouseEvent(QEvent.Type.MouseButtonRelease, QPointF(2, 100), QPointF(2, 100),
                              Qt.MouseButton.LeftButton, Qt.MouseButton.NoButton,
                              Qt.KeyboardModifier.NoModifier)
        # click without drag -> collapse
        handle.mousePressEvent(press)
        handle.mouseReleaseEvent(release)
        assert sp.collapsed is True
        assert sp.sizes()[-1] == 0
        assert not mw.journeys_panel.isVisible()
        # second click -> expand back at the last width
        handle.mousePressEvent(press)
        handle.mouseReleaseEvent(release)
        assert sp.collapsed is False
        assert sp.sizes()[-1] == 260
        assert mw.journeys_panel.isVisible()
        mw.hide()
    finally:
        close_main_window(mw)
