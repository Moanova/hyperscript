# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_participation_usecases.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for the participation use cases of participation_management
(TSK17): FN030 (associate / dissociate an agent with a block) and RG032
(unique participation per (block, agent) pair). Adapted from planoscript's
tests/test_agents/test_agent_state_association.py.
"""

import pytest

from core.services.participation_service import ParticipationService
from core.services.project_service import ProjectService
from usecases.project_management import CreateProjectUseCase
from usecases.agent_management import CreateAgentUseCase
from usecases.participation_management import (
    AssociateParticipationUseCase, DissociateParticipationUseCase,
)


def make_service():
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    return service


def test_fn030_associate_creates_participation():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    start = nm.block[0]  # the Start block created with the project (RG025)
    agent = CreateAgentUseCase(service).execute(lb="Hero")
    p = AssociateParticipationUseCase(service).execute(agent.id, start.id)
    assert p.block_id == start.id
    assert p.agent_id == agent.id
    assert p in nm.participation
    assert service.is_modified is True


def test_rg032_associate_is_idempotent():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    agent = CreateAgentUseCase(service).execute()
    block = nm.block[0]
    p1 = AssociateParticipationUseCase(service).execute(agent.id, block.id)
    p2 = AssociateParticipationUseCase(service).execute(agent.id, block.id)
    assert p1 is p2  # RG032: the existing participation is returned unchanged
    assert len(nm.participation) == 1


def test_fn030_dissociate_removes_participation():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    agent = CreateAgentUseCase(service).execute()
    block = nm.block[0]
    AssociateParticipationUseCase(service).execute(agent.id, block.id)
    removed = DissociateParticipationUseCase(service).execute(agent.id, block.id)
    assert removed is not None
    assert nm.participation == []
    assert DissociateParticipationUseCase(service).execute(agent.id, block.id) is None
    assert service.is_modified is True


def test_fn030_invalid_entities_refused():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    agent = CreateAgentUseCase(service).execute()
    with pytest.raises(ValueError):
        AssociateParticipationUseCase(service).execute(999, nm.block[0].id)  # unknown agent
    with pytest.raises(ValueError):
        AssociateParticipationUseCase(service).execute(agent.id, 999)  # unknown block
    with pytest.raises(ValueError):
        DissociateParticipationUseCase(service).execute(999, nm.block[0].id)
    with pytest.raises(ValueError):
        DissociateParticipationUseCase(service).execute(agent.id, 999)


def test_participation_service_helpers():
    service = make_service()
    project = service.current_project
    nm = project.narrative_maps[0]
    a1 = CreateAgentUseCase(service).execute(lb="A1")
    a2 = CreateAgentUseCase(service).execute(lb="A2")
    block = nm.block[0]
    AssociateParticipationUseCase(service).execute(a1.id, block.id)
    AssociateParticipationUseCase(service).execute(a2.id, block.id)
    assert ParticipationService.find_participation(nm, block.id, a1.id).agent_id == a1.id
    assert ParticipationService.find_participation(nm, block.id, 999) is None
    assert len(ParticipationService.get_block_participations(nm, block.id)) == 2
    assert len(ParticipationService.get_agent_participations(project, a1.id)) == 1
    assert ParticipationService.get_agent(project, a2.id).lb == "A2"
    assert ParticipationService.get_agent(project, 999) is None
