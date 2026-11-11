# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : transition_dialog.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Transition edition dialog (TSK12, FN021).

Edits a transition's editable attribute: the free-text note only. A
transition carries no condition - the structured condition is carried by
the Condition block (FN035).

get_values() returns {'note': str}.
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QTextEdit,
    QPushButton, QHBoxLayout, QSizePolicy
)
from PySide6.QtCore import Qt

from core.models.data_model import Transition
from config.config_loader import get as _get_config
from ui.utils import theme


class TransitionDialog(QDialog):
    """Edition dialog of a transition (note only)."""

    NOTE_MAX_HEIGHT_PX = _get_config("dialog_note_max_height_px", 60)

    def __init__(self, transition: Transition, parent=None):
        super().__init__(parent)
        self.transition = transition
        self._setup_ui()
        self._setup_content()

    def _setup_ui(self):
        self.setWindowTitle("Edit Transition")
        self.setModal(True)
        self.setMinimumSize(525, 240)
        self.layout = QVBoxLayout(self)
        self.setStyleSheet(theme.DIALOG_STYLESHEET)
        self.form = QFormLayout()
        self.form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.layout.addLayout(self.form, stretch=1)
        self.layout.setAlignment(self.form, Qt.AlignTop)
        self._add_buttons()

    def _setup_content(self):
        self.note_edit = QTextEdit()
        self.note_edit.setPlainText(getattr(self.transition, 'note', None) or "")
        self.note_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.note_edit.setMaximumHeight(self.NOTE_MAX_HEIGHT_PX)
        self.form.addRow("Note:", self.note_edit)

    def _add_buttons(self):
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(self.accept)
        ok_button.setFixedWidth(100)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setFixedWidth(100)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        self.layout.addLayout(button_layout)

    def get_values(self) -> dict:
        """Return the values entered by the user: {'note': str}."""
        return {'note': self.note_edit.toPlainText()}
