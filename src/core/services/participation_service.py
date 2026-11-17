# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : participation_service.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Participation helpers (RG032/RG033, TSK17).

A participation links an agent (project level) to a block of a narrative map
(SU008). RG032: at most one participation per (block, agent) pair.
RG033: deleting an agent cascades to all its participations and relationships.
RG041: journey membership is derived from the block - participations and
relationships carry no journey attachment of their own.
"""

from typing import Dict, List, Optional

from core.models.data_model import Agent, Block, NarrativeMap, Participation, Project, Relationship


class ParticipationService:
    """Pure business logic on participations/relationships; no Qt dependency (RG058)."""

    @staticmethod
    def get_agent(project: Project, agent_id: int) -> Optional[Agent]:
        for a in project.agent:
            if a.id == agent_id:
                return a
        return None

    @staticmethod
    def get_block(narrative_map: NarrativeMap, block_id: int) -> Optional[Block]:
        for b in narrative_map.block:
            if b.id == block_id:
                return b
        return None

    @staticmethod
    def find_participation(narrative_map: NarrativeMap, block_id: int,
                           agent_id: int) -> Optional[Participation]:
        """RG032: the participation between a block and an agent, or None."""
        for p in narrative_map.participation:
            if p.block_id == block_id and p.agent_id == agent_id:
                return p
        return None

    @staticmethod
    def get_block_participations(narrative_map: NarrativeMap, block_id: int) -> List[Participation]:
        return [p for p in narrative_map.participation if p.block_id == block_id]

    @staticmethod
    def get_agent_participations(project: Project, agent_id: int) -> List[Participation]:
        """All the participations of an agent, across all the map(s) of the project."""
        result = []
        for narrative_map in project.narrative_maps:
            result.extend(p for p in narrative_map.participation if p.agent_id == agent_id)
        return result

    @staticmethod
    def get_agent_relationships(project: Project, agent_id: int) -> List[Relationship]:
        """All the relationships involving an agent (either side), across all maps."""
        result = []
        for narrative_map in project.narrative_maps:
            result.extend(r for r in narrative_map.relationship
                          if r.agent_a_id == agent_id or r.agent_b_id == agent_id)
        return result

    @staticmethod
    def cascade_delete_agent(project: Project, agent_id: int) -> Dict[str, int]:
        """RG033: remove every participation and relationship referencing the
        agent, across all the map(s) of the project. Returns the removal
        counts (for the UI information message)."""
        counts = {'participation': 0, 'relationship': 0}
        for narrative_map in project.narrative_maps:
            kept_p = []
            for p in narrative_map.participation:
                if p.agent_id == agent_id:
                    counts['participation'] += 1
                else:
                    kept_p.append(p)
            narrative_map.participation[:] = kept_p
            kept_r = []
            for r in narrative_map.relationship:
                if r.agent_a_id == agent_id or r.agent_b_id == agent_id:
                    counts['relationship'] += 1
                else:
                    kept_r.append(r)
            narrative_map.relationship[:] = kept_r
        return counts
