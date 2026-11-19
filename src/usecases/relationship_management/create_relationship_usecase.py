# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : create_relationship_usecase.py
# Version      : 1
# Date         : 2026-11-19
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from typing import Optional

from core.models.data_model import Relationship
from core.services.project_service import ProjectService
from core.services.participation_service import ParticipationService
from core.services.relationship_service import RelationshipService


class CreateRelationshipUseCase:
    """FN034/RG035 (TSK20): create a typed, non-directed, binary relationship
    between two distinct agents, anchored to exactly one block.

    The agent pair is stored canonically sorted (TSK25). Returns None when a
    relationship already exists for the (block, agent pair) - RG035 unique
    block/relationship link, hardened session 06. Raises ValueError on invalid
    input (unknown agent/block, invalid type, self-pair)."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, agent_1_id: int, agent_2_id: int, typ: str, block_id: int,
                note: Optional[str] = None, content: Optional[str] = None) -> Optional[Relationship]:
        project = self.project_service.current_project
        if project is None:
            return None
        narrative_map = project.narrative_maps[0]  # MVP: single map
        RelationshipService.check_pair(agent_1_id, agent_2_id)  # RG035: distinct agents
        if ParticipationService.get_agent(project, agent_1_id) is None \
                or ParticipationService.get_agent(project, agent_2_id) is None:
            raise ValueError("Unknown agent id")
        if ParticipationService.get_block(narrative_map, block_id) is None:
            raise ValueError("Unknown block id")
        if not RelationshipService.validate_type(typ):  # FN037
            raise ValueError(f"Invalid relationship type: {typ}. "
                             f"Must be one of: {RelationshipService.relationship_types()}")
        if RelationshipService.find_relationship(
                narrative_map, block_id, agent_1_id, agent_2_id) is not None:
            return None  # RG035: duplicate (block, pair) refused
        relationship = Relationship(
            id=narrative_map.get_next_id('relationship'),
            block_id=block_id,
            agent_1_id=agent_1_id,
            agent_2_id=agent_2_id,  # canonical sorted storage in Relationship.__post_init__ (TSK25)
            typ=typ,
            note=(note if note and note.strip() else None),
            content=(content if content and content.strip() else None),
        )
        narrative_map.relationship.append(relationship)
        self.project_service.set_modified(True)
        return relationship
