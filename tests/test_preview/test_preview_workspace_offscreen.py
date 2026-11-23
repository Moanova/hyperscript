# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_preview_workspace_offscreen.py
# Version      : 1
# Date         : 2026-11-23
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen tests TSK38 (session 11): the "Preview" view integration.

- the "Preview" tab/page exists, the View menu entry is renamed (view_preview,
  view_export gone) and enabled with a project open; "Export Map" stays greyed;
- the page hosts a read-only PreviewWorkspace (QTextBrowser, links inert) plus
  the same FiltersSidePanel as "Journeys" (no block list), in a SidePanelSplitter;
- the preview is (re)generated on tab switch, on model change while the tab is
  active (map_modified), and on filter change while the tab is active;
- viewing the preview / toggling filters never marks the project as modified.
"""

import pytest

pytest.importorskip("PySide6")

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QUrl
except Exception as e:  # libGL missing, no display, ...
    pytest.skip(f"Qt not usable in this environment: {e}", allow_module_level=True)

from ui.main_window import MainWindow
from ui.views.preview_workspace import PreviewWorkspace
from ui.widgets.filters_side_panel import FiltersSidePanel, SidePanelSplitter
from core.models.data_model import Block, Participation
from core.services.journey_service import JourneyService
from core.services.transition_service import TransitionService
from usecases.agent_management.create_agent_usecase import CreateAgentUseCase


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(autouse=True)
def _isolated_user_state(tmp_path, monkeypatch):
    """Redirect user_state.json reads/writes to a temp file (the real one is
    tracked in git)."""
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


def test_preview_tab_page_and_menu_entries(qapp):
    """TSK38: "Preview" tab/page; View menu has view_preview (enabled with a
    project open, disabled without), view_export is gone; the file export
    "Export Map" stays greyed in the MVP."""
    mw = make_main_window()
    try:
        assert "Preview" in mw.view_pages
        assert mw.preview_page is mw.view_pages["Preview"]
        assert "Preview" in mw.tab_bar._tab_buttons
        assert "view_preview" in mw.menu_actions
        assert "view_export" not in mw.menu_actions
        assert mw.menu_actions["view_preview"].isEnabled()
        assert not mw.menu_actions["export_map"].isEnabled()
    finally:
        close_main_window(mw)
    mw_no_project = MainWindow()
    try:
        assert not mw_no_project.menu_actions["view_preview"].isEnabled()
        assert mw_no_project.preview_workspace is None
    finally:
        mw_no_project.close()


def test_preview_page_hosts_readonly_workspace_and_filters_panel(qapp):
    """TSK38: the "Preview" page hosts a SidePanelSplitter with the read-only
    PreviewWorkspace and a FiltersSidePanel without block list (same as
    "Journeys"); the preview is already rendered at project open."""
    mw = make_main_window()
    try:
        assert isinstance(mw.preview_workspace, PreviewWorkspace)
        assert isinstance(mw.preview_splitter, SidePanelSplitter)
        assert isinstance(mw.preview_panel, FiltersSidePanel)
        assert mw.preview_panel.show_block_list is False
        assert mw.preview_panel.block_list is None
        assert mw.preview_workspace.parentWidget() is mw.preview_splitter
        assert mw.preview_panel.parentWidget() is mw.preview_splitter
        assert mw.preview_workspace.isReadOnly()
        assert not mw.preview_workspace.openLinks()
        assert not mw.preview_workspace.openExternalLinks()
        assert mw.preview_workspace.placeholderText() == "Open a project to preview its reading."
        # initial reading preview (rendered at project open, tab not active yet)
        # note: toHtml() does not re-emit id attributes; assert on the plain text
        # (the raw HTML with the anchors is covered by the PreviewService tests)
        project = mw.project_service.current_project
        nm = project.narrative_maps[0]
        plain = mw.preview_workspace.toPlainText()
        assert project.lb in plain
        assert nm.journey[0].lb in plain
        start = next(b for b in nm.block if b.typ == "Start")
        assert f"{start.lb} ({start.typ})" in plain
    finally:
        close_main_window(mw)


def test_tab_switch_and_model_change_while_active_regenerate_preview(qapp):
    """TSK38: switching to the "Preview" tab regenerates the preview; a model
    change while the tab is active (map_modified) also regenerates it."""
    mw = make_main_window()
    try:
        mw.tab_bar.setCurrentTab("Preview")  # emits currentChanged -> _on_tab_changed
        assert mw.tab_bar.currentTab() == "Preview"
        project = mw.project_service.current_project
        nm = project.narrative_maps[0]
        plain = mw.preview_workspace.toPlainText()
        assert project.lb in plain
        assert nm.journey[0].lb in plain
        # model change while the "Preview" tab is active -> map_modified -> refresh
        CreateAgentUseCase(mw.project_service).execute(lb="Zoe Preview")
        assert "Zoe Preview" in mw.preview_workspace.toPlainText()
        # ...but not when another tab is active (no background work)
        mw.tab_bar.setCurrentTab("Agents")
        CreateAgentUseCase(mw.project_service).execute(lb="Bob Hidden")
        assert "Bob Hidden" not in mw.preview_workspace.toPlainText()
        mw.tab_bar.setCurrentTab("Preview")  # switch back regenerates
        assert "Bob Hidden" in mw.preview_workspace.toPlainText()
    finally:
        close_main_window(mw)


def test_filters_drive_the_preview_while_the_tab_is_active(qapp):
    """TSK38: while the "Preview" tab is active, the journey filter and the
    agent filter (side panel / Display menu) regenerate the preview dynamically
    (RG048/RG063/RG064)."""
    mw = make_main_window()
    try:
        project = mw.project_service.current_project
        nm = project.narrative_maps[0]
        j1 = nm.journey[0]
        mw.create_journey_usecase.execute()  # "Journey 2", not activated
        j2 = nm.journey[1]
        start = next(b for b in nm.block if b.typ == "Start")
        s1 = Block(id=nm.get_next_id('block'), lb="S1", typ="Scene")
        nm.block.append(s1)
        JourneyService.attach_block(nm, s1.id, j1.id)
        TransitionService.create_transition(nm, start.id, s1.id)
        agent = CreateAgentUseCase(mw.project_service).execute(lb="Solo")
        nm.participation.append(Participation(id=nm.get_next_id('participation'),
                                              block_id=start.id, agent_id=agent.id))
        mw.tab_bar.setCurrentTab("Preview")
        # journey filter off: both journeys rendered
        mw._set_journey_filter_active(False)
        plain = mw.preview_workspace.toPlainText()
        assert j1.lb in plain and j2.lb in plain
        # journey filter on: only the active journey
        mw._set_journey_filter_active(True)
        assert mw.journey_filter_active is True
        plain = mw.preview_workspace.toPlainText()
        assert j1.lb in plain
        assert j2.lb not in plain
        # agent filter on (while Preview active): only the blocks of the agent
        mw._set_agent_filter(agent.id)
        assert mw.agent_filter_agent_id == agent.id
        plain = mw.preview_workspace.toPlainText()
        assert f"{start.lb} ({start.typ})" in plain
        assert "S1 (Scene)" not in plain
        # agent filter off: all journey blocks visible again
        mw._set_agent_filter(None)
        plain = mw.preview_workspace.toPlainText()
        assert f"{start.lb} ({start.typ})" in plain
        assert "S1 (Scene)" in plain
    finally:
        close_main_window(mw)


def test_viewing_preview_and_filters_never_marks_modified(qapp):
    """TSK38 + RG047/RG048: watching the preview and toggling the filters is
    visual only - the project is not marked as modified."""
    mw = make_main_window()
    try:
        mw.project_service.set_modified(False)
        mw.tab_bar.setCurrentTab("Preview")
        mw._refresh_preview()
        mw._set_journey_filter_active(True)
        mw._set_agent_filter(None)
        mw._set_journey_filter_active(False)
        assert mw.project_service.is_modified is False
    finally:
        close_main_window(mw)


def test_internal_anchors_scroll_only_note_anchors_do_not_navigate(qapp):
    """TSK38: anchor clicks on #journey-*/#agent-*/#block-* scroll to the
    target (passive), #note-* anchors never navigate; the document is unchanged."""
    mw = make_main_window()
    try:
        mw.tab_bar.setCurrentTab("Preview")
        project = mw.project_service.current_project
        nm = project.narrative_maps[0]
        ws = mw.preview_workspace
        before = ws.toPlainText()
        start = next(b for b in nm.block if b.typ == "Start")
        ws._on_anchor_clicked(QUrl(f"#block-{start.id}"))
        ws._on_anchor_clicked(QUrl(f"#journey-{nm.journey[0].id}"))
        ws._on_anchor_clicked(QUrl("#note-block-999"))
        assert ws.toPlainText() == before
        assert project.lb in before
    finally:
        close_main_window(mw)
