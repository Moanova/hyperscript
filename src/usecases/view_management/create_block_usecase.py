# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : create_block_usecase.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from core.models.data_model import BLOCK_TYPES, Block
from core.services.project_service import ProjectService
from core.services.journey_service import JourneyService
from core.services.journey_sequence_service import JourneySequenceService


class CreateBlockUseCase:
    """FN014: create a narrative block. The type is chosen at creation and
    immutable afterwards (RG029); the Start type cannot be created manually
    (RG025). The block is attached to the active journey if the journey filter
    is active, to the default journey otherwise (RG040)."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, typ: str, lb: str = None, filter_active: bool = False) -> Block:
        narrative_map = self.project_service.current_project.narrative_maps[0]  # MVP: single map
        if typ not in BLOCK_TYPES or typ == "Start":
            raise ValueError(f"Cannot create a block of type {typ!r} manually")  # RG025
        block = Block(id=narrative_map.get_next_id('block'), lb=lb or typ, typ=typ)
        narrative_map.block.append(block)
        JourneyService.attach_new_block(narrative_map, block.id, filter_active)  # RG040
        JourneySequenceService.recompute_all(narrative_map)  # RG044
        self.project_service.set_modified(True)
        return block
