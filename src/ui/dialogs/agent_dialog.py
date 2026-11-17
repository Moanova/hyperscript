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

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QTextEdit, QPushButton, QHBoxLayout, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt

from core.models.data_model import AGENT_TYPES, Agent
from config.config_loader import get as _get_config
from ui.utils import theme


class AgentDialog(QDialog):
    """Agent data edition dialog (creation when entity is None)."""

    NOTE_MAX_HEIGHT_PX = _get_config("dialog_note_max_height_px", 60)
    CONTENT_MIN_HEIGHT_PX = _get_config("dialog_content_min_height_px", 160)

    def __init__(self, entity: Optional[Agent] = None, parent=None, default_label: Optional[str] = None):
        super().__init__(parent)
        self.entity = entity
        self.default_label = default_label
        self._setup_ui()
        self._setup_content()

    def _setup_ui(self):
        self.setWindowTitle("Edit Agent" if self.entity else "New Agent")
        self.setModal(True)
        self.setMinimumSize(525, 420)
        self.layout = QVBoxLayout(self)
        self.setStyleSheet(theme.DIALOG_STYLESHEET)
        self.form = QFormLayout()
        self.form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.layout.addLayout(self.form, stretch=1)
        self.layout.setAlignment(self.form, Qt.AlignTop)
        self._add_buttons()

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
        self.note_edit = QTextEdit()
        self.note_edit.setPlainText(getattr(self.entity, 'note', None) or "" if self.entity else "")
        self.note_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.note_edit.setMaximumHeight(self.NOTE_MAX_HEIGHT_PX)
        self.form.addRow("Note:", self.note_edit)

        # Content field (larger area, narrative content)
        self.content_edit = QTextEdit()
        self.content_edit.setPlainText(getattr(self.entity, 'content', None) or "" if self.entity else "")
        self.content_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.content_edit.setMinimumHeight(self.CONTENT_MIN_HEIGHT_PX)
        self.form.addRow("Content:", self.content_edit)

        # Inline validation message (hidden by default)
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {theme.ERROR_COLOR};")
        self.layout.addWidget(self.error_label)

    def _add_buttons(self):
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(self._validate)
        ok_button.setFixedWidth(100)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setFixedWidth(100)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        self.layout.addLayout(button_layout)

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
