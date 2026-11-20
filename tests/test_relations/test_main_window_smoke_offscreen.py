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
    from PySide6.QtWidgets import QApplication
except Exception as e:  # libGL missing, no display, ...
    pytest.skip(f"Qt not usable in this environment: {e}", allow_module_level=True)

from ui.main_window import MainWindow


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
        mw._on_relationships_journey_filter_requested(None)
        assert mw.journey_filter_active is False
        assert nm.get_active_journey() is j2
    finally:
        mw._teardown_workspace()
        mw.project_service.set_modified(False)  # avoid the quit confirmation dialog
        mw.close()
