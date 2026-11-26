# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : block_dialog.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Block edition dialog (TSK12, FN015/RG042; TSK39 session 12: FN030).

Edits a narrative block (fusion of planoscript's ComponentDialog and
RelationDialog, adapted to the single typed Block):
- "Label", "Note", "Content" (FN015); the type is immutable (RG029: chosen
  at creation) and is not a row of the dialog (TSK16), only the window title
  recalls it;
- "Journeys": multiple-choice list of the map's journeys (RG042: the list
  cannot be emptied - a block cannot be detached from its last journey;
  disabled when the map has a single journey);
- "Agents": multiple-choice list of the project's agents (FN030, TSK39
  session 12) - the participating agents are checked; the checked set is
  applied by the caller through the participation use cases. The structured
  condition fields (FN035) were removed in session 12 to simplify the model.

get_values() returns {'lb', 'note', 'content', 'journey_ids', 'agent_ids'}.
"""
from typing import List

from PySide6.QtWidgets import QLineEdit, QListWidget, QListWidgetItem
from PySide6.QtCore import Qt

from core.models.data_model import Block
from ui.dialogs.base_dialog import FormDialog


class BlockDialog(FormDialog):
    """Edition dialog of a narrative block."""

    JOURNEYS_LIST_MAX_HEIGHT_PX = 120

    def __init__(self, block: Block, journeys: List, attached_journey_ids,
                 agents: List = (), participating_agent_ids=(), parent=None):
        """
        Args:
            block: the Block entity being edited
            journeys: list of the Journey entities of the map
            attached_journey_ids: ids of the journeys the block is currently
                attached to (checked in the list)
            agents: list of the project's Agent entities
            participating_agent_ids: ids of the agents currently participating
                in the block (checked in the list)
        """
        super().__init__(parent)
        self.block = block
        self._journeys = list(journeys)
        self._attached = set(attached_journey_ids or [])
        self._agents = list(agents)
        self._participating = set(participating_agent_ids or [])
        self._setup_ui(f"Edit Block ({self.block.typ})")
        self._setup_content()

    def _setup_content(self):
        # Label field
        self.lb_edit = QLineEdit()
        self.lb_edit.setText(getattr(self.block, 'lb', '') or '')
        self.form.addRow("Label:", self.lb_edit)

        # Note field (compact area, summary notes)
        self._add_note_field(getattr(self.block, 'note', None) or "")

        # Content field (larger area, narrative content)
        self._add_content_field(getattr(self.block, 'content', None) or "")

        # Journeys multiple-choice list (RG042)
        self.journeys_list = QListWidget()
        for journey in self._journeys:
            item = QListWidgetItem(journey.lb)
            item.setData(Qt.ItemDataRole.UserRole, journey.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked
                               if journey.id in self._attached
                               else Qt.CheckState.Unchecked)
            self.journeys_list.addItem(item)
        self.journeys_list.setMaximumHeight(self.JOURNEYS_LIST_MAX_HEIGHT_PX)
        if len(self._journeys) <= 1 or self.block.typ == "Start":
            # RG042: disabled when the map has a single journey;
            # RG068: the Start block's attachments are never editable
            self.journeys_list.setEnabled(False)
        self.form.addRow("Journeys:", self.journeys_list)

        # Agents multiple-choice list (FN030, TSK39 session 12): same pattern
        # as the journey attachments - the participating agents are checked
        self.agents_list = QListWidget()
        for agent in sorted(self._agents, key=lambda a: (a.lb, a.id)):
            item = QListWidgetItem(f"{agent.lb} ({agent.typ})")
            item.setData(Qt.ItemDataRole.UserRole, agent.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Checked
                               if agent.id in self._participating
                               else Qt.CheckState.Unchecked)
            self.agents_list.addItem(item)
        self.agents_list.setMaximumHeight(self.JOURNEYS_LIST_MAX_HEIGHT_PX)
        self.form.addRow("Agents:", self.agents_list)

        # Inline validation message (hidden by default)
        self._add_error_label()

    def _validate(self):
        if not self.get_values()['lb']:
            self.error_label.setText("Label cannot be empty")
            return
        if self.journeys_list.isEnabled() and not self.get_journey_ids():
            self.error_label.setText("A block must belong to at least one journey")  # RG042
            return
        self.accept()

    def get_journey_ids(self) -> List[int]:
        """Return the ids of the checked journeys."""
        ids = []
        for i in range(self.journeys_list.count()):
            item = self.journeys_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                ids.append(item.data(Qt.ItemDataRole.UserRole))
        return ids

    def get_agent_ids(self) -> List[int]:
        """Return the ids of the checked agents (FN030)."""
        ids = []
        for i in range(self.agents_list.count()):
            item = self.agents_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                ids.append(item.data(Qt.ItemDataRole.UserRole))
        return ids

    def get_values(self) -> dict:
        """Return the values entered by the user."""
        return {
            'lb': self.lb_edit.text().strip(),
            'note': self.note_edit.toPlainText(),
            'content': self.content_edit.toPlainText(),
            'journey_ids': self.get_journey_ids(),
            'agent_ids': self.get_agent_ids(),
        }
