# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : transition_dialog.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Transition edition dialog (TSK12, FN021).

Edits a transition's editable attribute: the free-text note only (a
transition carries no structured condition - TSK39 session 12 removed the
condition fields from the model).

get_values() returns {'note': str}.
"""
from PySide6.QtWidgets import QTextEdit, QSizePolicy

from core.models.data_model import Transition
from config.config_loader import get as _get_config
from ui.dialogs.base_dialog import FormDialog


class TransitionDialog(FormDialog):
    """Edition dialog of a transition (note only)."""

    MIN_HEIGHT_PX = _get_config("transition_dialog_min_height_px", 240)

    def __init__(self, transition: Transition, parent=None):
        super().__init__(parent)
        self.transition = transition
        self._setup_ui("Edit Transition")
        self._setup_content()

    def _setup_content(self):
        self.note_edit = QTextEdit()
        self.note_edit.setPlainText(getattr(self.transition, 'note', None) or "")
        self.note_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.note_edit.setMaximumHeight(self.NOTE_MAX_HEIGHT_PX)
        self.form.addRow("Note:", self.note_edit)

    def get_values(self) -> dict:
        """Return the values entered by the user: {'note': str}."""
        return {'note': self.note_edit.toPlainText()}
