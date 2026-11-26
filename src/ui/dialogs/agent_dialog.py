# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : agent_dialog.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Agent creation/edition dialog (TSK18, FN031, SU008).

Edits the editable attributes of a project agent: label, type
(Character/Artefact - unlike the block, the agent type stays editable),
note and narrative content. Works in both modes:
- creation: entity is None, the label field is prefilled with
  default_label (editable);
- edition: entity is an Agent, the form is prefilled from the entity.

The dialog never writes the model (RG058): get_values() returns the entered
values and the caller applies the use case. Reprise of planoscript's
AgentDialog with AGENT_TYPES from the hyperscript data model.
"""
from typing import Optional

from PySide6.QtWidgets import QLineEdit, QComboBox

from core.models.data_model import AGENT_TYPES, Agent
from ui.dialogs.base_dialog import FormDialog


class AgentDialog(FormDialog):
    """Agent data edition dialog (creation when entity is None)."""

    def __init__(self, entity: Optional[Agent] = None, parent=None, default_label: Optional[str] = None):
        super().__init__(parent)
        self.entity = entity
        self.default_label = default_label
        self._setup_ui("Edit Agent" if self.entity else "New Agent")
        self._setup_content()

    def _setup_content(self):
        # Label field
        self.lb_edit = QLineEdit()
        if self.entity is not None:
            self.lb_edit.setText(getattr(self.entity, 'lb', ''))
        elif self.default_label:
            self.lb_edit.setText(self.default_label)
        self.form.addRow("Label:", self.lb_edit)

        # Type field (editable for agents, FN031)
        self.typ_combo = QComboBox()
        self.typ_combo.addItems(AGENT_TYPES)
        entity_typ = getattr(self.entity, 'typ', AGENT_TYPES[0]) if self.entity is not None else AGENT_TYPES[0]
        index = self.typ_combo.findText(entity_typ)
        if index >= 0:
            self.typ_combo.setCurrentIndex(index)
        self.form.addRow("Type:", self.typ_combo)

        # Note field (compact area, summary notes)
        self._add_note_field(getattr(self.entity, 'note', None) or "" if self.entity else "")

        # Content field (larger area, narrative content)
        self._add_content_field(getattr(self.entity, 'content', None) or "" if self.entity else "")

        # Inline validation message (hidden by default)
        self._add_error_label()

    def _validate(self):
        if not self.get_values()['lb']:
            self.error_label.setText("Label cannot be empty")
            return
        self.accept()

    def get_values(self) -> dict:
        """Return the values entered by the user ('lb', 'typ', 'note', 'content')."""
        return {
            'lb': self.lb_edit.text().strip(),
            'typ': self.typ_combo.currentText(),
            'note': self.note_edit.toPlainText(),
            'content': self.content_edit.toPlainText(),
        }
