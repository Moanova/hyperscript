# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_relationships_view_logic.py
# Version      : 1
# Date         : 2026-11-19
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Qt-free tests for the "Relationships" view logic (TSK27): RG069 derived
pair state at a block (pair_state_at_block / block_min_rank), the RG069 anchor
block ordering, the RG070 axis-order persistence in ProjectLayout, and the
RG048/RG063/RG064 filter visibility of relationships."""

from core.models.view_model import ProjectLayout
from core.services.project_service import ProjectService
from core.services.journey_service import JourneyService
from core.services.journey_sequence_service import JourneySequenceService
from core.services.journey_filter_service import JourneyFilterService
from core.services.agent_filter_service import AgentFilterService
from core.services.relationship_service import RelationshipService
from usecases.project_management import CreateProjectUseCase
from usecases.agent_management import CreateAgentUseCase
from usecases.view_management import CreateBlockUseCase, CreateTransitionUseCase
from usecases.journey_management import CreateJourneyUseCase
from usecases.relationship_management import CreateRelationshipUseCase


def make_service():
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    return service


def make_graph():
    """start(0) -> s1(1) -> s2(2) in the default journey j1; a second journey j2
    holds start and s2 (s2 rank 2 there via start->s2 direct? no: j2 = start->s2)."""
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    j1 = nm.journey[0]
    start = nm.block[0]
    s1 = CreateBlockUseCase(service).execute("Scene", lb="S1")
    s2 = CreateBlockUseCase(service).execute("Scene", lb="S2")
    CreateTransitionUseCase(service).execute(start.id, s1.id)
    CreateTransitionUseCase(service).execute(s1.id, s2.id)
    j2 = CreateJourneyUseCase(service).execute(lb="J2")  # RG068: Start auto-attached
    JourneyService.set_block_attachments(nm, s2.id, [j1.id, j2.id])
    CreateTransitionUseCase(service).execute(start.id, s2.id)  # in j2: s2 rank 1
    JourneySequenceService.recompute_all(nm)  # RG044
    return service, nm, start, s1, s2, j1, j2


def test_rg069_block_min_rank():
    service, nm, start, s1, s2, j1, j2 = make_graph()
    assert RelationshipService.block_min_rank(nm, start.id) == 0
    assert RelationshipService.block_min_rank(nm, s1.id) == 1   # j1 only
    assert RelationshipService.block_min_rank(nm, s2.id) == 1   # min(2 in j1, 1 in j2)


def test_rg069_pair_state_at_block():
    service, nm, start, s1, s2, j1, j2 = make_graph()
    a = CreateAgentUseCase(service).execute(lb="A")
    b = CreateAgentUseCase(service).execute(lb="B")
    r1 = CreateRelationshipUseCase(service).execute(a.id, b.id, "friend", s1.id)
    CreateRelationshipUseCase(service).execute(a.id, b.id, "enemy", s2.id)
    # state at start (rank 0): no anchor <= 0 -> None
    assert RelationshipService.pair_state_at_block(nm, a.id, b.id, start.id) is None
    # state at s1 (rank 1): friend
    assert RelationshipService.pair_state_at_block(nm, a.id, b.id, s1.id) is r1
    # state at s2 (rank min = 1 in j2... but anchor ranks: r1 at rank 1, r2 at rank min(2,1)=1)
    # both ranks equal 1 -> the last one by rank wins only if strictly greater; here tie -> r1 kept
    assert RelationshipService.pair_state_at_block(nm, a.id, b.id, s2.id) is r1
    # pair order does not matter (TSK25)
    assert RelationshipService.pair_state_at_block(nm, b.id, a.id, s1.id) is r1


def test_rg069_pair_state_uses_min_rank_across_journeys():
    service, nm, start, s1, s2, j1, j2 = make_graph()
    a = CreateAgentUseCase(service).execute(lb="A")
    b = CreateAgentUseCase(service).execute(lb="B")
    # anchored to s2 whose min rank across journeys is 1 (j2): visible from s2
    r = CreateRelationshipUseCase(service).execute(a.id, b.id, "ally", s2.id)
    assert RelationshipService.pair_state_at_block(nm, a.id, b.id, s2.id) is r
    assert RelationshipService.pair_state_at_block(nm, a.id, b.id, start.id) is None  # rank 0


def test_rg070_axis_order_persistence_roundtrip():
    layout = ProjectLayout()
    layout.relationships_axis_order = [3, 1, 2]
    data = layout.to_dict()
    restored = ProjectLayout.from_dict(data)
    assert restored.relationships_axis_order == [3, 1, 2]
    # absent key -> empty order (initial alphabetical order computed by the view)
    assert ProjectLayout.from_dict({}).relationships_axis_order == []


def test_rg048_rg063_relationship_filter_visibility():
    service, nm, start, s1, s2, j1, j2 = make_graph()
    a = CreateAgentUseCase(service).execute(lb="A")
    b = CreateAgentUseCase(service).execute(lb="B")
    c = CreateAgentUseCase(service).execute(lb="C")
    r_ab = CreateRelationshipUseCase(service).execute(a.id, b.id, "friend", s1.id)  # s1 in j1 only
    r_ac = CreateRelationshipUseCase(service).execute(a.id, c.id, "enemy", s2.id)   # s2 in j1+j2
    # no filter: both visible
    assert JourneyFilterService.visible_relationship_ids(nm) == {r_ab.id, r_ac.id}
    # journey filter on j2: s1 not in j2 -> r_ab hidden, r_ac visible
    assert JourneyFilterService.visible_relationship_ids(nm, j2.id) == {r_ac.id}
    # agent filter (RG063): only the blocks the agent participates in count
    from usecases.participation_management import AssociateParticipationUseCase
    AssociateParticipationUseCase(service).execute(c.id, s2.id)
    AssociateParticipationUseCase(service).execute(a.id, s1.id)
    AssociateParticipationUseCase(service).execute(a.id, s2.id)
    assert AgentFilterService.visible_relationship_ids(nm, c.id) == {r_ac.id}
    assert AgentFilterService.visible_relationship_ids(nm, a.id) == {r_ab.id, r_ac.id}
    # an agent with no participation sees no relationship
    assert AgentFilterService.visible_relationship_ids(nm, b.id) == set()
