# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : relationship_dialog.py
# Version      : 1
# Date         : 2026-11-19
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Relationship creation/edition dialog (TSK20, FN034, SU011).

Edits a relationship: the two agents (fixed at creation - disabled on
edition), the type (combo fed from the configuration list, FN037), the anchor
block (combo ordered by minimum rank across all journeys, ties by id - RG069),
note and narrative content.
- creation: entity is None;
- edition: entity is a Relationship, the form is prefilled from it.

The dialog never writes the model (RG058): get_values() returns the entered
values and the caller applies the use case. Pattern of AgentDialog (TSK18).
"""
from typing import List, Optional

from PySide6.QtWidgets import QComboBox

from core.models.data_model import Agent, NarrativeMap, Relationship
from core.services.relationship_service import RelationshipService
from ui.dialogs.base_dialog import FormDialog


class RelationshipDialog(FormDialog):
    """Relationship data edition dialog (creation when entity is None)."""

    def __init__(self, agents: List[Agent], narrative_map: NarrativeMap,
                 entity: Optional[Relationship] = None, parent=None,
                 default_agent_1_id: Optional[int] = None,
                 default_agent_2_id: Optional[int] = None,
                 default_block_id: Optional[int] = None):
        super().__init__(parent)
        self.entity = entity
        self._agents = list(agents)
        self._narrative_map = narrative_map
        # TSK29: pre-fill on creation from a matrix cell (pair + anchor block)
        self._default_agent_1_id = default_agent_1_id
        self._default_agent_2_id = default_agent_2_id
        self._default_block_id = default_block_id
        self._setup_ui("Edit Relationship" if self.entity else "New Relationship", 525, 460)
        self._setup_content()

    def _setup_content(self):
        # Agent 1 / Agent 2 combos (fixed on edition: the pair is set at creation)
        self.agent_1_combo = QComboBox()
        self.agent_2_combo = QComboBox()
        for combo in (self.agent_1_combo, self.agent_2_combo):
            for agent in self._agents:
                combo.addItem(f"{agent.lb} ({agent.typ})", agent.id)
        if self.entity is not None:
            self._set_combo_value(self.agent_1_combo, self.entity.agent_1_id)
            self._set_combo_value(self.agent_2_combo, self.entity.agent_2_id)
            self.agent_1_combo.setEnabled(False)
            self.agent_2_combo.setEnabled(False)
        else:
            if self._default_agent_1_id is not None:
                self._set_combo_value(self.agent_1_combo, self._default_agent_1_id)
            if self._default_agent_2_id is not None:
                self._set_combo_value(self.agent_2_combo, self._default_agent_2_id)
            elif len(self._agents) > 1:
                self.agent_2_combo.setCurrentIndex(1)
        self.form.addRow("Agent 1:", self.agent_1_combo)
        self.form.addRow("Agent 2:", self.agent_2_combo)

        # Type combo (configuration list, FN037)
        self.typ_combo = QComboBox()
        self.typ_combo.addItems(RelationshipService.relationship_types())
        if self.entity is not None:
            index = self.typ_combo.findText(self.entity.typ)
            if index >= 0:
                self.typ_combo.setCurrentIndex(index)
        self.form.addRow("Type:", self.typ_combo)

        # Anchor block combo (ordered by minimum rank across all journeys, RG069)
        self.block_combo = QComboBox()
        self._block_ids = RelationshipService.ordered_anchor_block_ids(self._narrative_map)
        blocks = {b.id: b for b in self._narrative_map.block}
        for block_id in self._block_ids:
            block = blocks[block_id]
            self.block_combo.addItem(f"{block.lb} ({block.typ})", block_id)
        if self.entity is not None:
            self._set_combo_value(self.block_combo, self.entity.block_id)
        elif self._default_block_id is not None:
            self._set_combo_value(self.block_combo, self._default_block_id)
        self.form.addRow("Anchor block:", self.block_combo)

        # Note field (compact area, summary notes)
        self._add_note_field(getattr(self.entity, 'note', None) or "" if self.entity else "")

        # Content field (larger area, narrative content)
        self._add_content_field(getattr(self.entity, 'content', None) or "" if self.entity else "")

        # Inline validation message (hidden by default)
        self._add_error_label()

    def _set_combo_value(self, combo: QComboBox, value: int):
        index = combo.findData(value)
        if index >= 0:
            combo.setCurrentIndex(index)

    def _validate(self):
        if self.entity is None and self.agent_1_combo.currentData() == self.agent_2_combo.currentData():
            self.error_label.setText("The two agents must be distinct (RG035)")
            return
        if not self.typ_combo.currentText():
            self.error_label.setText("Type cannot be empty")
            return
        self.accept()

    def get_values(self) -> dict:
        """Return the entered values ('agent_1_id', 'agent_2_id', 'typ',
        'block_id', 'note', 'content')."""
        return {
            'agent_1_id': self.agent_1_combo.currentData(),
            'agent_2_id': self.agent_2_combo.currentData(),
            'typ': self.typ_combo.currentText(),
            'block_id': self.block_combo.currentData(),
            'note': self.note_edit.toPlainText(),
            'content': self.content_edit.toPlainText(),
        }
