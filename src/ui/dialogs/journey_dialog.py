# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : journey_dialog.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Journey data edition dialog (TSK12, FN024).

Displays the editable attributes of a journey (label and note) and returns
the values entered by the user. Reprise of planoscript's JourneyDialog.
"""
from typing import Optional

from PySide6.QtWidgets import QLineEdit

from core.models.data_model import Journey
from ui.dialogs.base_dialog import FormDialog


class JourneyDialog(FormDialog):
    """Journey edition dialog: lb, note."""

    def __init__(self, entity: Optional[Journey] = None, parent=None,
                 default_label: Optional[str] = None,
                 default_note: Optional[str] = None):
        super().__init__(parent)
        self.entity = entity
        self.default_label = default_label
        self.default_note = default_note
        self._setup_ui("Edit Journey" if self.entity else "New Journey", 525, 300)
        self._setup_content()

    def _setup_content(self):
        # Label field
        self.lb_edit = QLineEdit()
        if self.entity is not None:
            self.lb_edit.setText(getattr(self.entity, 'lb', ''))
        elif self.default_label:
            self.lb_edit.setText(self.default_label)
        self.form.addRow("Label:", self.lb_edit)

        # Note field (compact area)
        note = getattr(self.entity, 'note', None) or ""
        if self.entity is None and self.default_note:
            note = self.default_note
        self._add_note_field(note)

        # Inline validation message (hidden by default)
        self._add_error_label()

    def _validate(self):
        if not self.get_values()['lb']:
            self.error_label.setText("Label cannot be empty")
            return
        self.accept()

    def get_values(self) -> dict:
        """Return the values entered by the user: {'lb', 'note'}."""
        return {
            'lb': self.lb_edit.text().strip(),
            'note': self.note_edit.toPlainText()
        }
