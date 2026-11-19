# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_relationship_usecases.py
# Version      : 1
# Date         : 2026-11-19
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for the relationship_management use cases (TSK20): FN034
(create / edit / delete a typed relationship anchored to a block) and RG035
(unique (block, agent pair), two distinct agents, type from the config list
FN037, canonical sorted pair TSK25)."""

import pytest

from core.services.project_service import ProjectService
from usecases.project_management import CreateProjectUseCase
from usecases.agent_management import CreateAgentUseCase
from usecases.view_management import CreateBlockUseCase
from usecases.relationship_management import (
    CreateRelationshipUseCase, UpdateRelationshipUseCase, DeleteRelationshipUseCase,
)


def make_service():
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    return service


def make_agents(service, n=2):
    return [CreateAgentUseCase(service).execute(lb=f"Agent {i + 1}") for i in range(n)]


def test_fn034_create_relationship():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    a1, a2 = make_agents(service)
    start = nm.block[0]
    # pair given in reverse order on purpose: stored canonically sorted (TSK25)
    rel = CreateRelationshipUseCase(service).execute(a2.id, a1.id, "rival", start.id,
                                                      note="n", content="c")
    assert rel is not None
    assert (rel.agent_1_id, rel.agent_2_id) == (a1.id, a2.id)
    assert rel.block_id == start.id and rel.typ == "rival"
    assert rel.note == "n" and rel.content == "c"
    assert rel in nm.relationship
    assert service.is_modified is True


def test_rg035_duplicate_block_pair_refused():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    a1, a2 = make_agents(service)
    start = nm.block[0]
    s1 = CreateBlockUseCase(service).execute("Scene", lb="S1")
    rel = CreateRelationshipUseCase(service).execute(a1.id, a2.id, "friend", start.id)
    assert rel is not None
    # same (block, pair), another type -> refused (RG035 unique block-pair link)
    assert CreateRelationshipUseCase(service).execute(a2.id, a1.id, "enemy", start.id) is None
    # same pair on another block -> allowed
    rel2 = CreateRelationshipUseCase(service).execute(a1.id, a2.id, "enemy", s1.id)
    assert rel2 is not None
    assert len(nm.relationship) == 2


def test_rg035_self_pair_refused():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    (a1,) = make_agents(service, n=1)
    with pytest.raises(ValueError):  # no self-relationship (RG035)
        CreateRelationshipUseCase(service).execute(a1.id, a1.id, "friend", nm.block[0].id)


def test_fn037_invalid_type_refused():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    a1, a2 = make_agents(service)
    with pytest.raises(ValueError):
        CreateRelationshipUseCase(service).execute(a1.id, a2.id, "unknown", nm.block[0].id)


def test_create_unknown_agent_or_block_refused():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    a1, a2 = make_agents(service)
    with pytest.raises(ValueError):
        CreateRelationshipUseCase(service).execute(999, a2.id, "friend", nm.block[0].id)
    with pytest.raises(ValueError):
        CreateRelationshipUseCase(service).execute(a1.id, a2.id, "friend", 999)


def test_fn034_update_type_anchor_note_content():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    a1, a2 = make_agents(service)
    start = nm.block[0]
    s1 = CreateBlockUseCase(service).execute("Scene", lb="S1")
    rel = CreateRelationshipUseCase(service).execute(a1.id, a2.id, "friend", start.id)
    result = UpdateRelationshipUseCase(service).execute(
        rel, typ="ally", block_id=s1.id, note="", content="new content")
    assert result is rel
    assert rel.typ == "ally" and rel.block_id == s1.id
    assert rel.note is None and rel.content == "new content"  # "" clears the note
    assert rel.modification_date_time is not None
    assert service.is_modified is True
    with pytest.raises(ValueError):  # invalid type (FN037)
        UpdateRelationshipUseCase(service).execute(rel, typ="unknown")


def test_rg035_update_anchor_collision_refused():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    a1, a2 = make_agents(service)
    start = nm.block[0]
    s1 = CreateBlockUseCase(service).execute("Scene", lb="S1")
    rel1 = CreateRelationshipUseCase(service).execute(a1.id, a2.id, "friend", start.id)
    rel2 = CreateRelationshipUseCase(service).execute(a1.id, a2.id, "enemy", s1.id)
    # moving rel2 to start collides with rel1 (same block+pair) -> refused, unchanged
    assert UpdateRelationshipUseCase(service).execute(rel2, block_id=start.id) is None
    assert rel2.block_id == s1.id
    # moving rel1 to s1 also refused; moving to an unused block is fine
    assert UpdateRelationshipUseCase(service).execute(rel1, block_id=s1.id) is None
    s2 = CreateBlockUseCase(service).execute("Scene", lb="S2")
    assert UpdateRelationshipUseCase(service).execute(rel1, block_id=s2.id) is rel1
    assert rel1.block_id == s2.id


def test_fn034_delete_relationship():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    a1, a2 = make_agents(service)
    rel = CreateRelationshipUseCase(service).execute(a1.id, a2.id, "friend", nm.block[0].id)
    assert DeleteRelationshipUseCase(service).execute(rel.id) is True
    assert nm.relationship == []
    assert service.is_modified is True
    assert DeleteRelationshipUseCase(service).execute(rel.id) is False  # already gone
