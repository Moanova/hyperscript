# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_agent_usecases.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for the agent use cases of agent_management (TSK17).

Covers FN031 (create / update / duplicate / delete agent) and RG033 (cascade
of participations and relationships on agent deletion). Adapted from
planoscript's tests/test_agents (test_agent_usecases, test_agent_duplication,
test_delete_agent_usecase).
"""

import pytest

from core.models.data_model import Relationship
from core.services.project_service import ProjectService
from usecases.project_management import CreateProjectUseCase
from usecases.view_management import CreateBlockUseCase
from usecases.agent_management import (
    CreateAgentUseCase, UpdateAgentUseCase, DuplicateAgentUseCase, DeleteAgentUseCase,
)
from usecases.participation_management import AssociateParticipationUseCase


def make_service():
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    return service


def test_fn031_create_agent_defaults():
    service = make_service()
    agent = CreateAgentUseCase(service).execute()
    assert agent.id == 1
    assert agent.lb == "Agent 1"
    assert agent.typ == "Character"
    assert agent in service.current_project.agent
    assert service.is_modified is True


def test_fn031_create_agent_custom_values_and_artefact_type():
    service = make_service()
    agent = CreateAgentUseCase(service).execute(lb="  Sword  ", typ="Artefact", note="n", content="c")
    assert agent.lb == "Sword"
    assert agent.typ == "Artefact"
    assert agent.note == "n"
    assert agent.content == "c"


def test_fn031_create_agent_invalid_type_refused():
    service = make_service()
    with pytest.raises(ValueError):
        CreateAgentUseCase(service).execute(typ="Dragon")


def test_fn031_update_agent():
    service = make_service()
    agent = CreateAgentUseCase(service).execute(lb="Hero")
    updated = UpdateAgentUseCase(service).execute(agent, lb="Villain", typ="Artefact", note="", content="x")
    assert updated.lb == "Villain"
    assert updated.typ == "Artefact"
    assert updated.note is None  # "" clears the field
    assert updated.content == "x"
    assert updated.modification_date_time is not None
    assert service.is_modified is True


def test_fn031_update_agent_invalid_values_refused():
    service = make_service()
    agent = CreateAgentUseCase(service).execute(lb="Hero")
    with pytest.raises(ValueError):
        UpdateAgentUseCase(service).execute(agent, lb="   ")  # empty label
    with pytest.raises(ValueError):
        UpdateAgentUseCase(service).execute(agent, typ="Dragon")


def test_fn031_duplicate_agent():
    service = make_service()
    agent = CreateAgentUseCase(service).execute(lb="Hero", typ="Artefact", note="n")
    block = CreateBlockUseCase(service).execute("Scene", lb="S1")
    AssociateParticipationUseCase(service).execute(agent.id, block.id)  # not copied
    nm = service.current_project.narrative_maps[0]

    copy = DuplicateAgentUseCase(service).execute(agent)
    assert copy.id != agent.id
    assert copy.lb == "Hero (copy)"
    assert copy.typ == "Artefact"
    assert copy.note == "n"
    assert all(p.agent_id != copy.id for p in nm.participation)  # participations not copied

    custom = DuplicateAgentUseCase(service).execute(agent, lb="Sidekick")
    assert custom.lb == "Sidekick"
    assert service.is_modified is True


def test_fn031_duplicate_agent_not_in_project_refused():
    service = make_service()
    other_service = make_service()
    foreign = CreateAgentUseCase(other_service).execute(lb="Foreign")
    with pytest.raises(ValueError):
        DuplicateAgentUseCase(service).execute(foreign)


def test_rg033_delete_agent_cascades_participations_and_relationships():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    agent = CreateAgentUseCase(service).execute(lb="Hero")
    other = CreateAgentUseCase(service).execute(lb="Other")
    block = CreateBlockUseCase(service).execute("Scene", lb="S1")
    AssociateParticipationUseCase(service).execute(agent.id, block.id)
    nm.relationship.append(Relationship(
        id=nm.get_next_id('relationship'), block_id=block.id,
        agent_a_id=agent.id, agent_b_id=other.id, typ="friend"))

    result = DeleteAgentUseCase(service).execute(agent.id)
    assert result is not None
    assert result['removed'] == {'participation': 1, 'relationship': 1}  # RG033
    assert agent not in service.current_project.agent
    assert nm.participation == []
    assert nm.relationship == []
    assert service.is_modified is True


def test_fn031_delete_unknown_agent_returns_none():
    service = make_service()
    assert DeleteAgentUseCase(service).execute(999) is None
