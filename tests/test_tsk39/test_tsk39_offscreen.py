# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_tsk39_offscreen.py
# Version      : 1
# Date         : 2026-11-26
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Offscreen tests for TSK39 (session 12 test feedback).

Menu général : 1.1 bascule Project > View ; 1.2/1.4/1.10 bascule vers la vue
cible après New/Copy ; 1.3/1.5/1.6/1.7 états d'activation selon la vue
"Journeys" active et la sélection ; 1.3 libellé « Add Participation » ;
1.8 dialogues New/Delete de parcours ; 1.9 journeys_copy supprimé.
Vue Relationships : 2.1 « View in Journeys view » grisé sur cellule vide ;
2.2 bascule effective ; 2.3 plus de carte fantôme après suppression d'agent ;
2.4 libellé du panneau selon le filtre parcours ; 1.11 parcours dans le
dialogue de sélection de relation.
Vue Journeys : 3.1 liste Agents du dialogue + application des participations ;
3.2 plus de champs condition ; 3.3 position du nouveau bloc dans la zone
visible.
"""

import pytest

pytest.importorskip("PySide6")

try:
    from PySide6.QtWidgets import QApplication, QDialog, QMenu
    from PySide6.QtCore import Qt, QPoint
except Exception as e:  # libGL missing, no display, ...
    pytest.skip(f"Qt not usable in this environment: {e}", allow_module_level=True)

import ui.main_window as mw_module
from ui.main_window import MainWindow
from ui.dialogs.block_dialog import BlockDialog
from ui.dialogs.relationship_selection_dialog import RelationshipSelectionDialog
from core.services.participation_service import ParticipationService
from core.services.journey_service import JourneyService
from usecases.view_management import CreateBlockUseCase
from usecases.agent_management import CreateAgentUseCase
from usecases.relationship_management import CreateRelationshipUseCase


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


class FakeJourneyDialog:
    def __init__(self, *args, **kwargs):
        pass

    def exec(self):
        return QDialog.DialogCode.Accepted

    def get_values(self):
        return {"lb": "Journey 2", "note": "n2"}


class FakeAgentDialog:
    def __init__(self, *args, **kwargs):
        pass

    def exec(self):
        return QDialog.DialogCode.Accepted

    def get_values(self):
        return {"lb": "NewGuy", "typ": "Character", "note": "", "content": ""}


class FakeRelationshipDialog:
    def __init__(self, agents, narrative_map, parent=None, entity=None,
                 default_agent_1_id=None, default_agent_2_id=None, default_block_id=None):
        self._agents = list(agents)
        self._a1 = default_agent_1_id if default_agent_1_id is not None else self._agents[0].id
        self._a2 = default_agent_2_id if default_agent_2_id is not None else self._agents[1].id
        self._block = default_block_id if default_block_id is not None else narrative_map.block[0].id

    def exec(self):
        return QDialog.DialogCode.Accepted

    def get_values(self):
        return {"agent_1_id": self._a1, "agent_2_id": self._a2,
                "typ": "friend", "block_id": self._block, "note": "", "content": ""}


class FakeMessageBox:
    class StandardButton:
        Yes = 1
        No = 2

    @staticmethod
    def question(*args, **kwargs):
        return FakeMessageBox.StandardButton.Yes

    @staticmethod
    def information(*args, **kwargs):
        pass


# ---------------------------------------------------------------------
# 1.1 Project > View switches the view (tab + stacked page)
# ---------------------------------------------------------------------
def test_1_1_view_menu_switches_tab_and_page(qapp):
    mw = make_main_window()
    try:
        assert mw.tab_bar.currentTab() == "Agents"  # default (TSK30 1.1)
        mw.menu_actions['view_journeys'].trigger()
        assert mw.tab_bar.currentTab() == "Journeys"
        assert mw.pages.currentWidget() is mw.view_pages["Journeys"]
        mw.menu_actions['view_relationships'].trigger()
        assert mw.tab_bar.currentTab() == "Relationships"
        assert mw.pages.currentWidget() is mw.view_pages["Relationships"]
        mw.menu_actions['view_preview'].trigger()
        assert mw.tab_bar.currentTab() == "Preview"
        assert mw.pages.currentWidget() is mw.view_pages["Preview"]
    finally:
        close_main_window(mw)


# ---------------------------------------------------------------------
# 1.2/1.4/1.10 bascule vers la vue cible après New/Copy
# ---------------------------------------------------------------------
def test_1_2_new_agent_switches_to_agents_view(qapp, monkeypatch):
    mw = make_main_window()
    try:
        monkeypatch.setattr(mw_module, "AgentDialog", FakeAgentDialog)
        mw._switch_view("Journeys")
        mw._new_agent()
        assert mw.tab_bar.currentTab() == "Agents"
        assert mw.pages.currentWidget() is mw.view_pages["Agents"]
    finally:
        close_main_window(mw)


def test_1_4_new_block_switches_to_journeys_view(qapp):
    mw = make_main_window()
    try:
        assert mw.tab_bar.currentTab() == "Agents"
        mw._create_new_block("Scene")
        assert mw.tab_bar.currentTab() == "Journeys"
        assert mw.pages.currentWidget() is mw.view_pages["Journeys"]
        nm = mw._current_narrative_map()
        assert sum(1 for b in nm.block if b.typ == "Scene") == 1
    finally:
        close_main_window(mw)


def test_1_10_new_relationship_switches_to_relationships_view(qapp, monkeypatch):
    mw = make_main_window()
    try:
        service = mw.project_service
        CreateAgentUseCase(service).execute(lb="Alpha")
        CreateAgentUseCase(service).execute(lb="Zoo")
        mw.relationships_workspace.refresh()
        monkeypatch.setattr(mw_module, "RelationshipDialog", FakeRelationshipDialog)
        mw._switch_view("Agents")
        mw._new_relationship()
        assert mw.tab_bar.currentTab() == "Relationships"
        assert len(mw._current_narrative_map().relationship) == 1
    finally:
        close_main_window(mw)


# ---------------------------------------------------------------------
# 1.3/1.5/1.6/1.7 états d'activation + libellé « Add Participation »
# ---------------------------------------------------------------------
def test_1_3_1_5_1_6_1_7_menu_states_follow_view_and_selection(qapp, monkeypatch):
    mw = make_main_window()
    try:
        service = mw.project_service
        CreateAgentUseCase(service).execute(lb="Alpha")
        mw._update_menu_state()
        # 1.3: libellé normalisé
        assert mw.menu_actions['agents_associate'].text() == "Add Participation"
        # sur la vue "Agents" (défaut) : Transitions + Blocks Edit/Delete + Add Participation grisés
        assert mw.tab_bar.currentTab() == "Agents"
        for key in ('transitions_new', 'transitions_edit', 'transitions_delete',
                    'blocks_edit', 'blocks_delete', 'agents_associate'):
            assert not mw.menu_actions[key].isEnabled(), key
        # vue Journeys active, aucune sélection
        mw._switch_view("Journeys")
        assert mw.menu_actions['transitions_new'].isEnabled()          # 1.6: menu Transitions actif en vue Journeys
        assert not mw.menu_actions['transitions_edit'].isEnabled()     # 1.7: pas de transition sélectionnée
        assert not mw.menu_actions['transitions_delete'].isEnabled()
        assert not mw.menu_actions['blocks_edit'].isEnabled()          # 1.5: pas de bloc sélectionné
        assert not mw.menu_actions['blocks_delete'].isEnabled()
        assert not mw.menu_actions['agents_associate'].isEnabled()     # 1.3: pas de bloc sélectionné
        # un bloc créé (et sélectionné) -> Blocks Edit/Delete + Add Participation actifs
        mw._create_new_block("Scene")
        assert mw.menu_actions['blocks_edit'].isEnabled()
        assert mw.menu_actions['blocks_delete'].isEnabled()
        assert mw.menu_actions['agents_associate'].isEnabled()
        assert not mw.menu_actions['transitions_edit'].isEnabled()
        # une transition créée (et sélectionnée) -> Transitions Edit/Delete actifs
        nm = mw._current_narrative_map()
        start = next(b for b in nm.block if b.typ == "Start")
        scene = next(b for b in nm.block if b.typ == "Scene")
        mw._on_transition_created(mw.journeys_workspace.find_block_node(start.id),
                                  mw.journeys_workspace.find_block_node(scene.id))
        assert mw.menu_actions['transitions_edit'].isEnabled()
        assert mw.menu_actions['transitions_delete'].isEnabled()
        assert not mw.menu_actions['blocks_edit'].isEnabled()  # la sélection est la transition
    finally:
        close_main_window(mw)


# ---------------------------------------------------------------------
# 1.8 dialogues New/Delete de parcours ; 1.9 journeys_copy supprimé
# ---------------------------------------------------------------------
def test_1_8_new_journey_opens_dialog_and_creates_with_entered_values(qapp, monkeypatch):
    mw = make_main_window()
    try:
        assert 'journeys_copy' not in mw.menu_actions  # 1.9
        monkeypatch.setattr(mw_module, "JourneyDialog", FakeJourneyDialog)
        n0 = len(mw._current_narrative_map().journey)
        mw._new_journey()
        nm = mw._current_narrative_map()
        assert len(nm.journey) == n0 + 1
        assert nm.journey[-1].lb == "Journey 2"  # valeur saisie dans le dialogue
        assert nm.journey[-1].note == "n2"
    finally:
        close_main_window(mw)


def test_1_8_delete_journey_selection_dialog_and_confirmation(qapp, monkeypatch):
    mw = make_main_window()
    try:
        monkeypatch.setattr(mw_module, "JourneyDialog", FakeJourneyDialog)
        mw._new_journey()  # 2 journeys
        nm = mw._current_narrative_map()
        assert len(nm.journey) == 2

        class FakeSelectionDialog:
            def __init__(self, journeys, parent=None, title=""):
                self._journeys = list(journeys)

            def exec(self):
                return QDialog.DialogCode.Accepted

            def get_selected_journey(self):
                return self._journeys[1]  # the second journey is chosen

        monkeypatch.setattr(mw_module, "JourneySelectionDialog", FakeSelectionDialog)
        monkeypatch.setattr(mw_module, "QMessageBox", FakeMessageBox)
        mw._delete_journey()
        assert len(nm.journey) == 1
        assert nm.journey[0].lb == "Journey 1"  # the chosen one was deleted
    finally:
        close_main_window(mw)


# ---------------------------------------------------------------------
# 2.1/2.2 menu contextuel « View in Journeys view » + bascule effective
# ---------------------------------------------------------------------
def _capture_context_menu(monkeypatch, mw, row, col):
    """Run the cell context menu without blocking: QMenu is replaced by a
    subclass whose exec() only records the menu (PySide6 does not allow
    patching exec on the QMenu class itself)."""
    captured = {}

    class FakeMenu(QMenu):
        def exec(self, pos=None):
            captured['menu'] = self
            return None

    monkeypatch.setattr(mw_module, "QMenu", FakeMenu)
    mw._show_relationships_context_menu(row, col, QPoint(0, 0))
    menu = captured['menu']
    return {a.text(): a for a in menu.actions()}


def test_2_1_view_in_journeys_greyed_on_empty_cell(qapp, monkeypatch):
    mw = make_main_window()
    try:
        service = mw.project_service
        alpha = CreateAgentUseCase(service).execute(lb="Alpha")
        zoo = CreateAgentUseCase(service).execute(lb="Zoo")
        ws = mw.relationships_workspace
        ws.refresh()
        actions = _capture_context_menu(monkeypatch, mw, 0, 1)  # empty cell (no relationship)
        assert "View in Journeys view" in actions
        assert not actions["View in Journeys view"].isEnabled()  # 2.1
        # a relationship anchored at the Start block for the pair -> cell filled
        monkeypatch.setattr(mw_module, "RelationshipDialog", FakeRelationshipDialog)
        mw._new_relationship_prefilled(alpha.id, zoo.id)
        actions = _capture_context_menu(monkeypatch, mw, 0, 1)
        assert actions["View in Journeys view"].isEnabled()
    finally:
        close_main_window(mw)


def test_2_2_view_in_journeys_actually_switches_the_page(qapp, monkeypatch):
    mw = make_main_window()
    try:
        service = mw.project_service
        alpha = CreateAgentUseCase(service).execute(lb="Alpha")
        zoo = CreateAgentUseCase(service).execute(lb="Zoo")
        ws = mw.relationships_workspace
        ws.refresh()
        monkeypatch.setattr(mw_module, "RelationshipDialog", FakeRelationshipDialog)
        mw._new_relationship_prefilled(alpha.id, zoo.id)
        mw._switch_view("Relationships")
        assert mw.pages.currentWidget() is mw.view_pages["Relationships"]
        mw._view_relationship_anchor_in_journeys(0, 1)
        # 2.2: the tab AND the stacked page switched (setCurrentTab emits currentChanged)
        assert mw.tab_bar.currentTab() == "Journeys"
        assert mw.pages.currentWidget() is mw.view_pages["Journeys"]
    finally:
        close_main_window(mw)


# ---------------------------------------------------------------------
# 2.3 suppression d'un agent -> plus de carte fantôme dans la matrice
# ---------------------------------------------------------------------
def test_2_3_deleted_agent_card_removed_from_matrix(qapp, monkeypatch):
    mw = make_main_window()
    try:
        service = mw.project_service
        alpha = CreateAgentUseCase(service).execute(lb="Alpha")
        zoo = CreateAgentUseCase(service).execute(lb="Zoo")
        ws = mw.relationships_workspace
        ws.refresh()
        assert alpha.id in ws._row_cards and alpha.id in ws._col_cards
        assert zoo.id in ws._row_cards
        monkeypatch.setattr(mw_module, "QMessageBox", FakeMessageBox)
        mw._delete_agent(agent=alpha)  # triggers refresh() via _update_menu_state
        assert alpha.id not in ws._order
        assert alpha.id not in ws._row_cards and alpha.id not in ws._col_cards
        from ui.nodes.matrix_agent_card import MatrixAgentCard
        remaining = [i for i in ws.scene.items() if isinstance(i, MatrixAgentCard)]
        assert all(c.entity.id in ws._order for c in remaining)
        assert all(c.entity.id != alpha.id for c in remaining)
        # release sur une carte fantôme : plus de ValueError (garde _on_card_released)
        ghost = MatrixAgentCard(alpha, 'row')
        ws._on_card_released(ghost, QPoint(0, 0))  # ne doit pas lever
    finally:
        close_main_window(mw)


# ---------------------------------------------------------------------
# 2.4 libellé du panneau latéral selon le filtre parcours
# (règle inversée par TSC séance 12 -> TSK40 : « All journeys » = parcours
# entre parenthèses, parcours filtré = type)
# ---------------------------------------------------------------------
def test_2_4_block_list_label_journeys_on_all_journeys_type_when_filtered(qapp):
    mw = make_main_window()
    try:
        ws = mw.relationships_workspace
        nm = mw._current_narrative_map()
        start = next(b for b in nm.block if b.typ == "Start")
        ws.refresh()
        # filtre inactif (« All journeys ») -> parcours entre parenthèses (TSK40)
        labels = [ws.block_list.item(i).text() for i in range(ws.block_list.count())]
        j = nm.get_active_journey()
        assert f"{start.lb} ({j.lb})" in labels
        # filtre sur le parcours actif -> type entre parenthèses à la place des parcours
        mw._set_journey_filter_active(True)
        labels = [ws.block_list.item(i).text() for i in range(ws.block_list.count())]
        assert f"{start.lb} ({start.typ})" in labels
        mw._set_journey_filter_active(False)
        labels = [ws.block_list.item(i).text() for i in range(ws.block_list.count())]
        assert f"{start.lb} ({j.lb})" in labels
    finally:
        close_main_window(mw)


# ---------------------------------------------------------------------
# 1.11 dialogue de sélection de relation : parcours au lieu du type
# ---------------------------------------------------------------------
def test_1_11_relationship_selection_dialog_shows_journeys_not_type(qapp):
    mw = make_main_window()
    try:
        service = mw.project_service
        nm = mw._current_narrative_map()
        project = service.current_project
        alpha = CreateAgentUseCase(service).execute(lb="Alpha")
        zoo = CreateAgentUseCase(service).execute(lb="Zoo")
        start = next(b for b in nm.block if b.typ == "Start")
        rel = CreateRelationshipUseCase(service).execute(alpha.id, zoo.id, "friend", start.id)
        assert rel is not None
        dialog = RelationshipSelectionDialog(nm.relationship, project, nm)
        text = dialog.list_widget.item(0).text()
        j = nm.journey[0]
        assert text == f"Alpha <-> Zoo @ {start.lb} ({j.lb})"  # parcours, pas le type
        assert "friend" not in text
    finally:
        close_main_window(mw)


# ---------------------------------------------------------------------
# 3.1 liste Agents du dialogue de bloc + application ; 3.2 plus de condition
# ---------------------------------------------------------------------
def test_3_1_3_2_block_dialog_agents_list_and_no_condition_fields(qapp):
    mw = make_main_window()
    try:
        service = mw.project_service
        nm = mw._current_narrative_map()
        project = service.current_project
        alpha = CreateAgentUseCase(service).execute(lb="Alpha")
        CreateAgentUseCase(service).execute(lb="Zoo")
        start = next(b for b in nm.block if b.typ == "Start")
        dialog = BlockDialog(start, nm.journey, JourneyService.attachment_journey_ids(nm, start.id),
                             agents=project.agent, participating_agent_ids=[alpha.id])
        # 3.2: plus de champs condition
        assert not hasattr(dialog, "condition_kind_combo")
        assert 'condition' not in dialog.get_values()
        # 3.1: liste Agents cochable, participants cochés
        assert dialog.agents_list.count() == 2
        checked = {dialog.agents_list.item(i).data(Qt.ItemDataRole.UserRole)
                   for i in range(dialog.agents_list.count())
                   if dialog.agents_list.item(i).checkState() == Qt.CheckState.Checked}
        assert checked == {alpha.id}
        dialog.agents_list.item(1).setCheckState(Qt.CheckState.Checked)
        assert set(dialog.get_agent_ids()) == {alpha.id, project.agent[1].id}
    finally:
        close_main_window(mw)


def test_3_1_edit_selected_block_applies_participations(qapp, monkeypatch):
    mw = make_main_window()
    try:
        service = mw.project_service
        nm = mw._current_narrative_map()
        alpha = CreateAgentUseCase(service).execute(lb="Alpha")
        zoo = CreateAgentUseCase(service).execute(lb="Zoo")
        scene = CreateBlockUseCase(service).execute("Scene", lb="S1")
        mw._create_new_block  # noqa - workspace exists
        # the block node must exist in the workspace: create it through the menu path
        mw._switch_view("Journeys")
        # select the scene block node (created via use case: add its node)
        from core.services.layout_service import LayoutService
        x, y = mw.journeys_workspace.next_free_creation_position()
        layout = LayoutService.create_node_layout(scene.id, scene.typ, x, y)
        mw.journeys_workspace.create_block_node(scene, layout, select=True)

        class FakeBlockDialog:
            def __init__(self, *args, **kwargs):
                pass

            def exec(self):
                return QDialog.DialogCode.Accepted

            def get_values(self):
                return {"lb": "S1", "note": "", "content": "",
                        "journey_ids": [nm.journey[0].id], "agent_ids": [alpha.id, zoo.id]}

        monkeypatch.setattr(mw_module, "BlockDialog", FakeBlockDialog)
        mw._edit_selected_block()
        parts = ParticipationService.get_block_participations(nm, scene.id)
        assert {p.agent_id for p in parts} == {alpha.id, zoo.id}
    finally:
        close_main_window(mw)


# ---------------------------------------------------------------------
# 3.3 position du nouveau bloc dans la zone visible courante
# ---------------------------------------------------------------------
def test_3_3_new_block_position_inside_visible_area(qapp, monkeypatch):
    """TSK39 (3.3): a user-created block is placed in the CURRENTLY VISIBLE
    area (follows the scrollbars), not anchored on the Start block when the
    user has scrolled elsewhere. The visible rect is fixed here (deterministic
    offscreen): far from the Start block at (80, 2020)."""
    from PySide6.QtCore import QRectF
    mw = make_main_window()
    try:
        ws = mw.journeys_workspace
        fake_visible = QRectF(1600, 1600, 632, 472)

        class _Poly:
            def boundingRect(self):
                return fake_visible

        monkeypatch.setattr(ws, "mapToScene", lambda rect: _Poly())
        from config.config_loader import get as _get_config
        w = _get_config("node_default_width", 80.0)
        h = _get_config("node_default_height", 40.0)
        x, y = ws.next_free_creation_position()
        assert fake_visible.left() <= x and x + w <= fake_visible.right()
        assert fake_visible.top() <= y and y + h <= fake_visible.bottom()
        # the Start block lies outside the visible area -> the position is the
        # first free cell of the visible area, not the Start-anchored fallback
        nm = mw._current_narrative_map()
        start_id = next(b.id for b in nm.block if b.typ == "Start")
        start = ws.find_block_node(start_id)
        assert start is not None
        sr, sp = start.rect(), start.pos()
        overlap = not (x + w <= sp.x() or sp.x() + sr.width() <= x
                       or y + h <= sp.y() or sp.y() + sr.height() <= y)
        assert not overlap
        assert (x, y) != (sp.x() + w + 80, sp.y())  # not the Start-anchored fallback
    finally:
        close_main_window(mw)
