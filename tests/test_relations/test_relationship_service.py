# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_relationship_service.py
# Version      : 1
# Date         : 2026-11-19
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for RelationshipService (TSK20): RG035 (binary, two distinct
agents, non-directed, typed from the configuration list FN037, anchored to one
block, unique (block, pair)), TSK25 canonical sorted pair, and the RG069
anchor-block ordering (minimum rank across all journeys, ties by id)."""

import pytest

from core.models.data_model import Relationship
from core.services.project_service import ProjectService
from core.services.journey_service import JourneyService
from core.services.journey_sequence_service import JourneySequenceService
from core.services.relationship_service import RelationshipService
from usecases.project_management import CreateProjectUseCase
from usecases.view_management import CreateBlockUseCase, CreateTransitionUseCase
from usecases.journey_management import CreateJourneyUseCase


def make_service():
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    return service


def make_rel(narrative_map, block_id, agent_1_id, agent_2_id, typ="friend"):
    rel = Relationship(id=narrative_map.get_next_id('relationship'), block_id=block_id,
                       agent_1_id=agent_1_id, agent_2_id=agent_2_id, typ=typ)
    narrative_map.relationship.append(rel)
    return rel


def test_fn037_types_read_from_config():
    types = RelationshipService.relationship_types()
    assert "friend" in types and "enemy" in types  # config.json relationship_types
    assert RelationshipService.validate_type("friend") is True
    assert RelationshipService.validate_type("unknown") is False


def test_rg035_canonical_pair_and_distinct_agents():
    assert RelationshipService.canonical_pair(5, 2) == (2, 5)
    assert RelationshipService.canonical_pair(2, 5) == (2, 5)
    RelationshipService.check_pair(2, 5)  # distinct: no error
    with pytest.raises(ValueError):  # no self-relationship (RG035)
        RelationshipService.check_pair(3, 3)


def test_rg035_find_relationship_block_pair():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    start = nm.block[0]
    other = CreateBlockUseCase(service).execute("Scene", lb="S1")
    rel = make_rel(nm, start.id, 7, 3, "ally")
    assert (rel.agent_1_id, rel.agent_2_id) == (3, 7)  # canonical sorted storage (TSK25)
    # find works in both pair orders
    assert RelationshipService.find_relationship(nm, start.id, 3, 7) is rel
    assert RelationshipService.find_relationship(nm, start.id, 7, 3) is rel
    # same pair on another block -> None; another pair on the same block -> None
    assert RelationshipService.find_relationship(nm, other.id, 3, 7) is None
    assert RelationshipService.find_relationship(nm, start.id, 3, 8) is None
    # block/pair queries
    assert RelationshipService.get_block_relationships(nm, start.id) == [rel]
    assert RelationshipService.get_pair_relationships(nm, 7, 3) == [rel]
    assert RelationshipService.get_pair_relationships(nm, 3, 8) == []


def test_rg069_ordered_anchor_block_ids_min_rank_then_id():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    start = nm.block[0]  # Start, rank 0 in the default journey
    j1 = nm.journey[0]
    j2 = CreateJourneyUseCase(service).execute(lb="J2")  # RG068: Start auto-attached to J2
    s1 = CreateBlockUseCase(service).execute("Scene", lb="S1")  # attached to j1 by default
    s2 = CreateBlockUseCase(service).execute("Scene", lb="S2")
    JourneyService.set_block_attachments(nm, s1.id, [j2.id])   # s1 only in j2
    JourneyService.set_block_attachments(nm, s2.id, [j1.id, j2.id])
    CreateTransitionUseCase(service).execute(start.id, s1.id)  # t1 -> j2: start(0) -> s1(1)
    CreateTransitionUseCase(service).execute(start.id, s2.id)  # t2 -> j1: s2 rank 1 ; j2: s2 rank 2
    JourneySequenceService.recompute_all(nm)  # RG044
    # min ranks: start 0; s1 1 (j2); s2 min(1 in j1, 2 in j2) = 1 -> tie -> by id (s1 < s2)
    assert RelationshipService.ordered_anchor_block_ids(nm) == [start.id, s1.id, s2.id]
