# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : relationship_selection_dialog.py
# Version      : 1
# Date         : 2026-11-19
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Relationship selection dialog (TSK20, FN034).

Lists the relationships of the narrative map ("A <-> B @ block (journeys of
the anchor block)" - TSK39 1.11: the journey(s) in which the relationship
exists are shown in parentheses instead of the relationship type); Ok
returns the selected relationship (Ok disabled until a selection is made).
Used by the Edit.../Delete... entries of "Project > Relationships". Same
pattern as AgentSelectionDialog (TSK18). Use get_selected_relationship()
after exec() == Accepted.
"""
from typing import List, Optional

from core.models.data_model import NarrativeMap, Project, Relationship
from core.services.journey_service import JourneyService
from core.services.participation_service import ParticipationService
from ui.dialogs.base_dialog import SelectionDialog


class RelationshipSelectionDialog(SelectionDialog):
    """Single-choice relationship selection dialog."""

    def __init__(self, relationships: List[Relationship], project: Project,
                 narrative_map: NarrativeMap, parent=None, title: str = "Select Relationship"):
        self._project = project
        self._narrative_map = narrative_map
        super().__init__(relationships, parent=parent, title=title)

    def _item_text(self, rel: Relationship) -> str:
        a = ParticipationService.get_agent(self._project, rel.agent_1_id)
        b = ParticipationService.get_agent(self._project, rel.agent_2_id)
        block = ParticipationService.get_block(self._narrative_map, rel.block_id)
        a_lb = a.lb if a else f"#{rel.agent_1_id}"
        b_lb = b.lb if b else f"#{rel.agent_2_id}"
        block_lb = block.lb if block else f"#{rel.block_id}"
        # TSK39 (1.11): the journey(s) of the anchor block in parentheses,
        # instead of the relationship type
        journeys = {j.id: j for j in self._narrative_map.journey}
        journey_ids = JourneyService.attachment_journey_ids(self._narrative_map, rel.block_id)
        journey_lbs = ", ".join(journeys[jid].lb for jid in journey_ids if jid in journeys)
        return f"{a_lb} <-> {b_lb} @ {block_lb} ({journey_lbs})"

    def get_selected_relationship(self) -> Optional[Relationship]:
        """Return the selected Relationship, or None if there is no selection."""
        return self.get_selected()
