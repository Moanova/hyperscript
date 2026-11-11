# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : duplicate_block_usecase.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from core.models.data_model import Block
from core.services.project_service import ProjectService
from core.services.journey_service import JourneyService
from core.services.journey_sequence_service import JourneySequenceService


class DuplicateBlockUseCase:
    """FN016: duplicate a block - distinct label ('{lb} (copy)', the application
    is unilingual English), new identifier, same type/note/content/condition.
    The copy is attached like a new block (RG040). The Start block cannot be
    duplicated (RG025)."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, block: Block, filter_active: bool = False) -> Block:
        if block.typ == "Start":
            raise ValueError("The Start block cannot be duplicated")  # RG025
        narrative_map = self.project_service.current_project.narrative_maps[0]  # MVP: single map
        copy = Block(
            id=narrative_map.get_next_id('block'),
            lb=f"{block.lb} (copy)",
            typ=block.typ,
            note=block.note,
            content=block.content,
            condition=dict(block.condition) if block.condition else None,
        )
        narrative_map.block.append(copy)
        JourneyService.attach_new_block(narrative_map, copy.id, filter_active)  # RG040
        JourneySequenceService.recompute_all(narrative_map)  # RG044
        self.project_service.set_modified(True)
        return copy
