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

from core.models.data_model import Journey
from ui.dialogs.base_dialog import SelectionDialog


class JourneySelectionDialog(SelectionDialog):
    """Single-choice journey selection dialog."""

    def __init__(self, journeys: List[Journey], parent=None, title: str = "Select Journey"):
        super().__init__(journeys, parent=parent, title=title)
        # A journey is always selected at opening
        self.list_widget.setCurrentRow(0)  # fires _selection_changed

    def _item_text(self, journey: Journey) -> str:
        return journey.lb

    def get_selected_journey(self) -> Optional[Journey]:
        """Return the selected Journey, or None if there is no selection."""
        return self.get_selected()
