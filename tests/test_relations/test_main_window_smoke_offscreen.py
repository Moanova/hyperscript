# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_main_window_smoke_offscreen.py
# Version      : 1
# Date         : 2026-11-19
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen smoke test for MainWindow project opening (TSK27 regression).

Regression: _init_workspace used self.relationships_page, which did not exist
(pages "Relationships"/"Export" were only stored in view_pages) -> AttributeError
on project open AND on new project creation. This test creates a project through
MainWindow and checks that all three workspaces are built and hosted in their
pages. Skipped when Qt/libGL is unavailable (sandbox) - to run on the dev
workstation.
"""

import pytest

pytest.importorskip("PySide6")

try:
    from PySide6.QtWidgets import QApplication, QDialog
except Exception as e:  # libGL missing, no display, ...
    pytest.skip(f"Qt not usable in this environment: {e}", allow_module_level=True)

import ui.main_window as mw_module
from ui.main_window import MainWindow
from ui.widgets.filters_side_panel import FiltersSidePanel  # TSK33
from core.services.journey_sequence_service import JourneySequenceService
from usecases.view_management import CreateBlockUseCase, CreateTransitionUseCase
from usecases.agent_management import CreateAgentUseCase
from usecases.relationship_management import CreateRelationshipUseCase  # TSK34


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def test_create_project_builds_all_workspaces(qapp):
    mw = MainWindow()
    try:
        mw._create_project()  # FN005: create + open + _init_workspace
        assert mw.project_opened is True
        assert mw.journeys_workspace is not None
        assert mw.agents_workspace is not None
        assert mw.relationships_workspace is not None
        # each workspace is hosted in its page
        assert mw.journeys_workspace.parentWidget() is not None
        assert mw.relationships_workspace.parentWidget() is mw.relationships_page
        # TSK33: the "Journeys" page hosts the shared filters side panel, without block list
        assert mw.journeys_splitter is not None
        assert isinstance(mw.journeys_panel, FiltersSidePanel)
        assert mw.journeys_panel.block_list is None
        assert mw.journeys_workspace.parentWidget() is mw.journeys_splitter
        # the Relationships view defaults to the Start anchor block (RG068/RG069)
        nm = mw._current_narrative_map()
        start = next(b for b in nm.block if b.typ == "Start")
        assert mw.relationships_workspace.get_anchor_block_id() == start.id
        # the block list of the side panel contains the Start block
        assert start.id in mw.relationships_workspace._block_ids
        # TSK30 (1.1): the default active view on project creation is "Agents"
        assert mw.tab_bar.currentTab() == "Agents"
        assert mw.pages.currentWidget() is mw.view_pages["Agents"]
    finally:
        mw._teardown_workspace()
        mw.close()


def test_relationships_journey_filter_requested_activates_journey(qapp):
    """TSK30 (4.1): the side panel journey combo emits the chosen journey id;
    the MainWindow handler activates that journey (FN026) and enables the
    filter (FN029); None = "All journeys" disables the filter."""
    mw = MainWindow()
    try:
        mw._create_project()
        mw._new_journey()  # second journey (FN023, via the real menu path)
        nm = mw._current_narrative_map()
        j2 = nm.journey[-1]
        received = []
        mw.relationships_workspace.journey_filter_requested.connect(
            lambda jid: received.append(jid))
        # choosing the second journey in the panel activates it + filter on
        mw.relationships_workspace.journey_combo.setCurrentIndex(2)
        assert received[-1] == j2.id
        assert nm.get_active_journey() is j2
        assert mw.journey_filter_active is True
        # "All journeys" disables the filter (active journey unchanged)
        mw._on_journey_filter_requested(None)  # TSK33: handler shared by both panels
        assert mw.journey_filter_active is False
        assert nm.get_active_journey() is j2
    finally:
        mw._teardown_workspace()
        mw.project_service.set_modified(False)  # avoid the quit confirmation dialog
        mw.close()


def test_relationship_cell_actions_prefilled_and_card_in_single_cell(qapp, monkeypatch):
    """TSK32: the cell context-menu actions work without exec(): empty cell ->
    New... pre-filled with the pair + the current anchor block (dialog mocked);
    the card then appears in the single active upper-triangle cell only; a
    filled cell edits that relationship entity directly."""
    mw = MainWindow()
    try:
        mw._create_project()
        service = mw.project_service
        nm = mw._current_narrative_map()
        start = next(b for b in nm.block if b.typ == "Start")
        s1 = CreateBlockUseCase(service).execute("Scene", lb="S1")
        CreateTransitionUseCase(service).execute(start.id, s1.id)
        JourneySequenceService.recompute_all(nm)  # RG044
        alpha = CreateAgentUseCase(service).execute(lb="Alpha")
        zoo = CreateAgentUseCase(service).execute(lb="Zoo")
        ws = mw.relationships_workspace
        ws.refresh()  # agents created after _init_workspace: rebuild the matrix order
        captured = {}

        class FakeDialog:
            def __init__(self, agents, narrative_map, parent=None, entity=None,
                         default_agent_1_id=None, default_agent_2_id=None, default_block_id=None):
                captured.update(a1=default_agent_1_id, a2=default_agent_2_id,
                                block=default_block_id, entity=entity)

            def exec(self):
                return QDialog.DialogCode.Accepted

            def get_values(self):
                return {"agent_1_id": captured["a1"], "agent_2_id": captured["a2"],
                        "typ": "friend", "block_id": captured["block"], "note": "", "content": ""}

        monkeypatch.setattr(mw_module, "RelationshipDialog", FakeDialog)
        # order [alpha, zoo] -> cell (0, 1) is the single active cell of the pair
        mw._new_relationship_prefilled(ws.agent_id_at_row(0), ws.agent_id_at_col(1))
        assert captured["a1"] == alpha.id and captured["a2"] == zoo.id
        assert captured["block"] == start.id  # current anchor block pre-filled
        assert len(nm.relationship) == 1
        rel = nm.relationship[0]
        assert {rel.agent_1_id, rel.agent_2_id} == {alpha.id, zoo.id}
        # the card appears in the single active cell (0, 1) only
        assert ws._cells[(0, 1)].card is not None
        assert ws._cells[(1, 0)].card is None  # lower triangle: inactive
        # filled cell -> Edit acts directly on that relationship entity
        mw._edit_relationship_entity(rel)
        assert captured["entity"] is rel
    finally:
        mw._teardown_workspace()
        mw.project_service.set_modified(False)  # avoid the quit confirmation dialog
        mw.close()


def test_window_initial_geometry_without_fixed_minimum(qapp):
    """TSK34 (retour 4): planoscript pattern - initial geometry 1280x720 via
    setGeometry, NO fixed minimum size (the views drive the effective min)."""
    mw = MainWindow()
    try:
        assert mw.geometry().width() == 1280 and mw.geometry().height() == 720
        assert mw.minimumSize().width() < 1280
        assert mw.minimumSize().height() < 720
    finally:
        mw.close()


def test_delete_relationship_entity_refreshes_without_error(qapp, monkeypatch):
    """TSK34 (retour 3): deleting a relationship from a filled cell refreshes
    the matrix without AttributeError; the card is removed from the scene."""
    mw = MainWindow()
    try:
        mw._create_project()
        service = mw.project_service
        nm = mw._current_narrative_map()
        start = next(b for b in nm.block if b.typ == "Start")
        s1 = CreateBlockUseCase(service).execute("Scene", lb="S1")
        CreateTransitionUseCase(service).execute(start.id, s1.id)
        JourneySequenceService.recompute_all(nm)  # RG044
        alpha = CreateAgentUseCase(service).execute(lb="Alpha")
        zoo = CreateAgentUseCase(service).execute(lb="Zoo")
        rel = CreateRelationshipUseCase(service).execute(alpha.id, zoo.id, "friend", s1.id)
        ws = mw.relationships_workspace
        ws.refresh()
        ws.set_anchor_block(s1.id)
        assert ws._cells[(0, 1)].card is not None

        class FakeMessageBox:
            class StandardButton:
                Yes = 1
                No = 2

            @staticmethod
            def question(*args, **kwargs):
                return FakeMessageBox.StandardButton.Yes

        monkeypatch.setattr(mw_module, "QMessageBox", FakeMessageBox)
        mw._delete_relationship_entity(rel)  # must not raise (was AttributeError)
        assert not nm.relationship
        assert ws._cells[(0, 1)].card is None
    finally:
        mw._teardown_workspace()
        mw.project_service.set_modified(False)  # avoid the quit confirmation dialog
        mw.close()
