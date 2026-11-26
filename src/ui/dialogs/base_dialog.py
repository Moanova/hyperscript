# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : base_dialog.py
# Version      : 1
# Date         : 2026-11-26
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Shared base classes for the app dialogs (TSK45).

- FormDialog: entity edition dialogs - vertical layout, form, Ok/Cancel
  buttons, inline error label, note/content fields. Ok runs _validate()
  (default: accept; subclasses override to validate first).
- SelectionDialog: single-choice list dialogs - list, Ok disabled until a
  selection is made, Cancel.

The public attribute names used by callers and tests are kept: layout,
form, list_widget, ok_button, error_label, note_edit, content_edit.
"""
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QListWidget, QTextEdit,
    QPushButton, QHBoxLayout, QLabel, QSizePolicy
)
from PySide6.QtCore import Qt

from config.config_loader import get as _get_config
from ui.utils import theme

# Standard dialog button widths (config.json)
BUTTON_WIDTH_PX = _get_config("dialog_button_width_px", 100)
WIDE_BUTTON_WIDTH_PX = _get_config("dialog_wide_button_width_px", 120)


class FormDialog(QDialog):
    """Base class of the entity edition dialogs (form + Ok/Cancel)."""

    NOTE_MAX_HEIGHT_PX = _get_config("dialog_note_max_height_px", 60)
    CONTENT_MIN_HEIGHT_PX = _get_config("dialog_content_min_height_px", 160)
    MIN_WIDTH_PX = _get_config("dialog_form_min_width_px", 525)
    MIN_HEIGHT_PX = _get_config("dialog_form_min_height_px", 420)

    def _setup_ui(self, title: str) -> None:
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(self.MIN_WIDTH_PX, self.MIN_HEIGHT_PX)
        self.layout = QVBoxLayout(self)
        self.setStyleSheet(theme.DIALOG_STYLESHEET)
        self.form = QFormLayout()
        self.form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.layout.addLayout(self.form, stretch=1)
        self.layout.setAlignment(self.form, Qt.AlignTop)
        self._add_buttons()

    def _add_buttons(self) -> None:
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        ok_button = QPushButton("Ok")
        ok_button.clicked.connect(self._validate)
        ok_button.setFixedWidth(BUTTON_WIDTH_PX)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setFixedWidth(BUTTON_WIDTH_PX)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        self.layout.addLayout(button_layout)

    def _add_error_label(self) -> None:
        """Inline validation message (hidden by default), below the form."""
        self.error_label = QLabel("")
        self.error_label.setStyleSheet(f"color: {theme.ERROR_COLOR};")
        self.layout.addWidget(self.error_label)

    def _add_note_field(self, text: str) -> None:
        """Compact note field (summary notes)."""
        self.note_edit = QTextEdit()
        self.note_edit.setPlainText(text)
        self.note_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.note_edit.setMaximumHeight(self.NOTE_MAX_HEIGHT_PX)
        self.form.addRow("Note:", self.note_edit)

    def _add_content_field(self, text: str) -> None:
        """Larger content field (narrative content)."""
        self.content_edit = QTextEdit()
        self.content_edit.setPlainText(text)
        self.content_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.content_edit.setMinimumHeight(self.CONTENT_MIN_HEIGHT_PX)
        self.form.addRow("Content:", self.content_edit)

    def _validate(self) -> None:
        """Default Ok behavior: accept. Override to validate first."""
        self.accept()


class SelectionDialog(QDialog):
    """Base class of the single-choice selection dialogs."""

    MIN_WIDTH_PX = _get_config("selection_dialog_min_width_px", 400)
    MIN_HEIGHT_PX = _get_config("selection_dialog_min_height_px", 400)

    def __init__(self, items: list, parent=None, title: str = "Select"):
        super().__init__(parent)
        self._items = list(items)
        self._setup_ui(title)
        self._refresh_list()

    def _setup_ui(self, title: str) -> None:
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(self.MIN_WIDTH_PX, self.MIN_HEIGHT_PX)
        self.layout = QVBoxLayout(self)
        self.setStyleSheet(theme.DIALOG_STYLESHEET)

        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._selection_changed)
        self.layout.addWidget(self.list_widget, stretch=1)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setFixedWidth(BUTTON_WIDTH_PX)
        self.ok_button.setEnabled(False)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setFixedWidth(BUTTON_WIDTH_PX)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(cancel_button)
        self.layout.addLayout(button_layout)

    def _refresh_list(self) -> None:
        self.list_widget.clear()
        for item in self._items:
            self.list_widget.addItem(self._item_text(item))

    def _item_text(self, item) -> str:
        """List row text of an item (overridden by subclasses)."""
        return str(item)

    def _selection_changed(self, current_row: int) -> None:
        self.ok_button.setEnabled(0 <= current_row < len(self._items))

    def get_selected(self) -> Optional[object]:
        """Return the selected item, or None if there is no selection."""
        row = self.list_widget.currentRow()
        if 0 <= row < len(self._items):
            return self._items[row]
        return None
