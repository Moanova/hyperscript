# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : update_relationship_usecase.py
# Version      : 1
# Date         : 2026-11-19
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from datetime import datetime
from typing import Optional

from core.models.data_model import Relationship
from core.services.project_service import ProjectService
from core.services.relationship_service import RelationshipService


class UpdateRelationshipUseCase:
    """FN034/SU011 (TSK20): edit a relationship - type, anchor block, note,
    content (the agent pair is fixed at creation). Returns None when the new
    anchor block already holds a relationship for the same pair (RG035)."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, relationship: Relationship, typ: Optional[str] = None,
                block_id: Optional[int] = None, note: Optional[str] = None,
                content: Optional[str] = None) -> Optional[Relationship]:
        # None means "unchanged"; pass "" to clear a field
        """Apply the relationship updates; return it, or None when refused."""
        narrative_map = self.project_service.current_project.narrative_maps[0]  # MVP: single map
        if typ is not None:
            if not RelationshipService.validate_type(typ):  # FN037
                raise ValueError(f"Invalid relationship type: {typ}. "
                                 f"Must be one of: {RelationshipService.relationship_types()}")
            relationship.typ = typ
        if block_id is not None and block_id != relationship.block_id:
            existing = RelationshipService.find_relationship(
                narrative_map, block_id, relationship.agent_1_id, relationship.agent_2_id)
            if existing is not None and existing.id != relationship.id:
                return None  # RG035: the (block, pair) is already used
            relationship.block_id = block_id
        if note is not None:
            relationship.note = note if note.strip() else None
        if content is not None:
            relationship.content = content if content.strip() else None
        relationship.modification_date_time = datetime.now()
        self.project_service.set_modified(True)
        return relationship
