# Application  : Hyperscript
# Script       : test_tsk40_offscreen.py
# Version      : 1
# Date         : 2026-11-26
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen tests for TSK40 (session 12 TSC corrections).

Side panel: section labels renamed - "Journey" -> "Journey Filter",
"Agent" -> "Agent Filter", "Blocks" -> "Block Sequence" (Relationships view;
filter zones only in Journeys/Preview). Block list label rule 2.4 inverted:
"All journeys" -> lb (journeys...), a specific journey filtered -> lb (typ).
"""

import pytest

pytest.importorskip("PySide6")

try:
    from PySide6.QtWidgets import QApplication, QLabel
except Exception as e:  # libGL missing, no display, ...
    pytest.skip(f"Qt not usable in this environment: {e}", allow_module_level=True)

from ui.main_window import MainWindow


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(autouse=True)
def _isolated_user_state(tmp_path, monkeypatch):
    import config.user_state_loader as usl
    monkeypatch.setattr(usl, "_STATE_PATH", str(tmp_path / "user_state.json"))
    monkeypatch.setattr(usl, "_state", {})


def make_main_window():
    mw = MainWindow()
    mw._create_project()
    return mw


def close_main_window(mw):
    mw._teardown_workspace()
    mw.project_service.set_modified(False)
    mw.close()


def _label_texts(panel):
    return [lbl.text() for lbl in panel.findChildren(QLabel)]


# ---------------------------------------------------------------------
# TSK40: renommages des sections du panneau latéral
# ---------------------------------------------------------------------
def test_tsk40_panel_section_labels_renamed(qapp):
    mw = make_main_window()
    try:
        # vue "Relationships" : les 3 zones avec les nouveaux libellés
        rel_texts = _label_texts(mw.relationships_workspace.panel)
        assert "Journey Filter" in rel_texts
        assert "Agent Filter" in rel_texts
        assert "Block Sequence" in rel_texts
        assert "Journey" not in rel_texts
        assert "Agent" not in rel_texts
        assert "Blocks" not in rel_texts
        # vues "Journeys" et "Preview" : zones filtres renommées, pas de liste
        for panel in (mw.journeys_panel, mw.preview_panel):
            texts = _label_texts(panel)
            assert "Journey Filter" in texts
            assert "Agent Filter" in texts
            assert "Block Sequence" not in texts
    finally:
        close_main_window(mw)


# ---------------------------------------------------------------------
# TSK40: règle 2.4 inversée - parcours sur "All journeys", type si filtré
# ---------------------------------------------------------------------
def test_tsk40_2_4_label_journeys_on_all_journeys_type_when_filtered(qapp):
    mw = make_main_window()
    try:
        ws = mw.relationships_workspace
        nm = mw._current_narrative_map()
        start = next(b for b in nm.block if b.typ == "Start")
        j = nm.get_active_journey()
        ws.refresh()
        # "All journeys" (filtre inactif) -> parcours entre parenthèses
        labels = [ws.block_list.item(i).text() for i in range(ws.block_list.count())]
        assert f"{start.lb} ({j.lb})" in labels
        assert f"{start.lb} ({start.typ})" not in labels
        # parcours précis filtré -> type entre parenthèses à la place
        mw._set_journey_filter_active(True)
        labels = [ws.block_list.item(i).text() for i in range(ws.block_list.count())]
        assert f"{start.lb} ({start.typ})" in labels
        assert f"{start.lb} ({j.lb})" not in labels
        mw._set_journey_filter_active(False)
        labels = [ws.block_list.item(i).text() for i in range(ws.block_list.count())]
        assert f"{start.lb} ({j.lb})" in labels
    finally:
        close_main_window(mw)
