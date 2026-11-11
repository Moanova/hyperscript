# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : delete_journey_usecase.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""FN027: delete a journey of the current narrative map.

RG024: the last journey of the map cannot be deleted (the UI shows an
explanatory message). RG034: the attachments of blocks that belonged only to
the deleted journey are reassigned to the default journey (no orphan block).
RG039: if the deleted journey was the default, the oldest remaining journey
becomes the new default; if it was the active one, the default becomes active.
Blocks are never deleted by a journey deletion.
"""
from typing import Optional, Dict, List

from core.models.data_model import Journey
from core.services.project_service import ProjectService
from core.services.journey_service import JourneyService
from core.services.journey_sequence_service import JourneySequenceService


class DeleteJourneyUseCase:

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, journey: Journey) -> Optional[Dict]:
        if not self.project_service.current_project:
            return None
        narrative_map = self.project_service.current_project.narrative_maps[0]  # MVP: single map
        if journey not in narrative_map.journey:
            return None

        # RG024: the last journey of the map cannot be deleted
        if len(narrative_map.journey) <= 1:
            return {'success': False, 'reason': 'last_journey', 'entity_id': journey.id}

        # RG039: if the deleted journey was the default, the oldest remaining
        # journey becomes the new default
        if journey.default:
            new_default = min((j for j in narrative_map.journey if j is not journey),
                              key=lambda j: j.id)
            new_default.default = True
        else:
            new_default = JourneyService.get_default_journey(narrative_map)

        # RG034: reassign to the default journey the attachments of blocks that
        # belonged only to the deleted journey (no orphan block)
        removed_nodes: List = []
        switched_nodes: List = []
        for node in [n for n in narrative_map.journey_node if n.journey_id == journey.id]:
            others = [n for n in narrative_map.journey_node
                      if n.block_id == node.block_id and n.journey_id != journey.id]
            if others:
                narrative_map.journey_node.remove(node)
                removed_nodes.append(node)
            else:
                node.journey_id = new_default.id
                switched_nodes.append(node)

        narrative_map.journey.remove(journey)
        JourneySequenceService.recompute_all(narrative_map)  # RG044

        # RG039: if the deleted journey was the active one, the default becomes active
        if narrative_map.active_journey_id == journey.id:
            narrative_map.active_journey_id = new_default.id

        self.project_service.set_modified(True)
        return {
            'success': True,
            'entity_id': journey.id,
            'removed_nodes': removed_nodes,
            'switched_nodes': switched_nodes,
            'new_default': new_default if journey.default else None,
        }
