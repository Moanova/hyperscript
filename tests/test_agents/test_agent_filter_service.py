# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_agent_filter_service.py
# Version      : 1
# Date         : 2026-11-17
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for AgentFilterService (TSK19a): RG063 agent filter visibility
and its combination with the journey filter (RG064 intersection, computed by
the caller as a set intersection)."""

from core.services.agent_filter_service import AgentFilterService
from core.services.journey_filter_service import JourneyFilterService
from core.services.project_service import ProjectService
from usecases.project_management import CreateProjectUseCase
from usecases.view_management import CreateBlockUseCase, CreateTransitionUseCase
from usecases.agent_management import CreateAgentUseCase
from usecases.participation_management import AssociateParticipationUseCase


def make_service():
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    return service


def make_map_with_agents(service):
    """Project with Start block, 2 scenes, 2 agents (A1 participates in both
    scenes, A2 only in S2), 3 participations, 2 transitions (Start->S1, S1->S2)."""
    nm = service.current_project.narrative_maps[0]
    start = nm.block[0]  # RG025
    s1 = CreateBlockUseCase(service).execute("Scene", lb="S1")
    s2 = CreateBlockUseCase(service).execute("Scene", lb="S2")
    a1 = CreateAgentUseCase(service).execute(lb="A1")
    a2 = CreateAgentUseCase(service).execute(lb="A2")
    AssociateParticipationUseCase(service).execute(a1.id, s1.id)
    AssociateParticipationUseCase(service).execute(a1.id, s2.id)
    AssociateParticipationUseCase(service).execute(a2.id, s2.id)
    t1 = CreateTransitionUseCase(service).execute(start.id, s1.id)
    t2 = CreateTransitionUseCase(service).execute(s1.id, s2.id)
    return nm, start, s1, s2, a1, a2, t1, t2


def test_rg063_filter_off_returns_all_blocks():
    service = make_service()
    nm, start, s1, s2, a1, a2, t1, t2 = make_map_with_agents(service)
    assert AgentFilterService.visible_block_ids(nm, None) == {start.id, s1.id, s2.id}


def test_rg063_visible_blocks_are_the_agent_participations():
    service = make_service()
    nm, start, s1, s2, a1, a2, t1, t2 = make_map_with_agents(service)
    assert AgentFilterService.visible_block_ids(nm, a1.id) == {s1.id, s2.id}
    assert AgentFilterService.visible_block_ids(nm, a2.id) == {s2.id}


def test_rg063_transition_visible_only_if_both_endpoints_visible():
    service = make_service()
    nm, start, s1, s2, a1, a2, t1, t2 = make_map_with_agents(service)
    # A1 participates in S1 and S2: S1->S2 visible, Start->S1 not (Start has no participation)
    assert AgentFilterService.visible_transition_ids(nm, a1.id) == {t2.id}
    # A2 only in S2: no transition has both endpoints in {S2}
    assert AgentFilterService.visible_transition_ids(nm, a2.id) == set()
    assert AgentFilterService.visible_transition_ids(nm, None) == {t1.id, t2.id}


def test_rg063_participation_and_relationship_visibility_follow_anchor_block():
    service = make_service()
    nm, start, s1, s2, a1, a2, t1, t2 = make_map_with_agents(service)
    p_ids = {p.id for p in nm.participation}
    assert AgentFilterService.visible_participation_ids(nm, a1.id) == {
        p.id for p in nm.participation if p.block_id in {s1.id, s2.id}}
    assert AgentFilterService.visible_participation_ids(nm, None) == p_ids
    assert AgentFilterService.visible_relationship_ids(nm, a1.id) == set()


def test_rg064_intersection_with_journey_filter():
    service = make_service()
    nm, start, s1, s2, a1, a2, t1, t2 = make_map_with_agents(service)
    # journey filter (all blocks here: single default journey) intersected with agent filter
    journey_blocks = JourneyFilterService.visible_block_ids(nm, nm.get_active_journey().id)
    agent_blocks = AgentFilterService.visible_block_ids(nm, a1.id)
    assert journey_blocks & agent_blocks == {s1.id, s2.id}  # RG064: intersection
    journey_transitions = JourneyFilterService.visible_transition_ids(nm, nm.get_active_journey().id)
    agent_transitions = AgentFilterService.visible_transition_ids(nm, a1.id)
    assert journey_transitions & agent_transitions == {t2.id}
