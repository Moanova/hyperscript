# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : journey_selection_dialog.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Journey selection dialog (TSK12, FN038/RG062 - "Set as Default...").

Lists the journeys of the narrative map; Ok returns the selected journey
(Ok disabled until a journey is selected), Cancel closes. A journey is
always selected at opening (row 0). Reprise of planoscript's
JourneySelectionDialog, with a configurable title.

Use get_selected_journey() after exec() == Accepted.
"""
from typing import List, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout
)

from core.models.data_model import Journey
from ui.utils import theme


class JourneySelectionDialog(QDialog):
    """Single-choice journey selection dialog."""

    def __init__(self, journeys: List[Journey], parent=None, title: str = "Select Journey"):
        super().__init__(parent)
        self._journeys = list(journeys)
        self._setup_ui(title)
        self._refresh_list()
        # A journey is always selected at opening
        self.list_widget.setCurrentRow(0)  # fires _selection_changed

    def _setup_ui(self, title: str):
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(400, 400)
        self.layout = QVBoxLayout(self)
        self.setStyleSheet(theme.DIALOG_STYLESHEET)

        self.list_widget = QListWidget()
        self.list_widget.currentRowChanged.connect(self._selection_changed)
        self.layout.addWidget(self.list_widget, stretch=1)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.ok_button = QPushButton("Ok")
        self.ok_button.clicked.connect(self.accept)
        self.ok_button.setFixedWidth(100)
        self.ok_button.setEnabled(False)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        cancel_button.setFixedWidth(100)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(cancel_button)
        self.layout.addLayout(button_layout)

    def _refresh_list(self):
        self.list_widget.clear()
        for journey in self._journeys:
            self.list_widget.addItem(journey.lb)

    def _selection_changed(self, current_row):
        has_selection = 0 <= current_row < len(self._journeys)
        self.ok_button.setEnabled(has_selection)

    def get_selected_journey(self) -> Optional[Journey]:
        """Return the selected Journey, or None if there is no selection."""
        row = self.list_widget.currentRow()
        if 0 <= row < len(self._journeys):
            return self._journeys[row]
        return None
