# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : agent_selection_dialog.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Agent selection dialog (TSK18, FN031).

Lists the agents of the project; Ok returns the selected agent (Ok disabled
until an agent is selected). Used by the Edit/Copy/Delete/Associate entries
of "Project > Agents" while the "Agents" view (TSK19) does not exist yet.
Same pattern as JourneySelectionDialog (TSK12); reprise of planoscript's
AgentSelectionDialog. Use get_selected_agent() after exec() == Accepted.
"""
from typing import List, Optional

from core.models.data_model import Agent
from ui.dialogs.base_dialog import SelectionDialog


class AgentSelectionDialog(SelectionDialog):
    """Single-choice agent selection dialog."""

    def __init__(self, agents: List[Agent], parent=None, title: str = "Select Agent"):
        super().__init__(agents, parent=parent, title=title)

    def _item_text(self, agent: Agent) -> str:
        return f"{agent.lb} ({agent.typ})"

    def get_selected_agent(self) -> Optional[Agent]:
        """Return the selected Agent, or None if there is no selection."""
        return self.get_selected()
