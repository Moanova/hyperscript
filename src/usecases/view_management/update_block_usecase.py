# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : update_block_usecase.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from typing import Optional, List, Dict, Any

from core.models.data_model import CONDITION_KINDS, Block
from core.services.project_service import ProjectService
from core.services.journey_service import JourneyService
from core.services.journey_sequence_service import JourneySequenceService


class UpdateBlockUseCase:
    """FN015: edit a block's editable attributes (label, note, narrative
    content). The type is not modifiable (RG029). A structured condition is
    accepted only for Condition blocks (FN035). journey_ids replaces the
    block's journey attachments and cannot be empty (RG042)."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, block: Block, lb: Optional[str] = None, note: Optional[str] = None,
                content: Optional[str] = None, condition: Optional[Dict[str, Any]] = None,
                journey_ids: Optional[List[int]] = None) -> Block:
        # None means "unchanged"; pass "" to clear a field
        if lb is not None:
            block.lb = lb
        if note is not None:
            block.note = note
        if content is not None:
            block.content = content
        if block.typ == "Condition":  # FN035: unique support of the structured condition
            if condition is not None and condition.get("kind") not in CONDITION_KINDS:
                raise ValueError(f"Invalid condition kind: {condition.get('kind')}. "
                                 f"Must be one of: {CONDITION_KINDS}")
            block.condition = condition
        elif condition is not None:
            raise ValueError("A structured condition is only allowed on a Condition block")
        if journey_ids is not None:  # RG042
            narrative_map = self.project_service.current_project.narrative_maps[0]
            JourneyService.set_block_attachments(narrative_map, block.id, journey_ids)
            JourneySequenceService.recompute_all(narrative_map)  # RG044
        self.project_service.set_modified(True)
        return block
