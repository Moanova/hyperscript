# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : delete_relationship_usecase.py
# Version      : 1
# Date         : 2026-11-19
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from core.services.project_service import ProjectService


class DeleteRelationshipUseCase:
    """FN034/SU011 (TSK20): delete a relationship (with prior confirmation in
    the UI). Returns True when the relationship was removed."""

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self, relationship_id: int) -> bool:
        """Delete the relationship; return True on success."""
        project = self.project_service.current_project
        if project is None:
            return False
        narrative_map = project.narrative_maps[0]  # MVP: single map
        kept = [r for r in narrative_map.relationship if r.id != relationship_id]
        if len(kept) == len(narrative_map.relationship):
            return False
        narrative_map.relationship[:] = kept
        self.project_service.set_modified(True)
        return True
