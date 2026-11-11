# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_journey_sequence_service.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for JourneySequenceService (TSK08) - RG044.

DFS from the unique Start block, following only the journey's transitions,
branches explored by increasing transition id, cycles memoized, unreachable
attached blocks ranked deterministically after the reachable ones.
"""

from core.models.data_model import Block
from core.services.project_service import ProjectService
from core.services.transition_service import TransitionService
from core.services.journey_service import JourneyService
from core.services.journey_sequence_service import JourneySequenceService
from usecases.project_management import CreateProjectUseCase


def make_map():
    service = ProjectService()
    project = CreateProjectUseCase(service).execute()
    return service, project.narrative_maps[0]


def add_block(narrative_map, typ, lb=None):
    block = Block(id=narrative_map.get_next_id('block'), lb=lb or typ, typ=typ)
    narrative_map.block.append(block)
    JourneyService.attach_block(narrative_map, block.id, narrative_map.journey[0].id)
    return block


def rank(narrative_map, block_id, journey_id=None):
    journey_id = journey_id or narrative_map.journey[0].id
    return next(jn.sequence_order for jn in narrative_map.journey_node
                if jn.block_id == block_id and jn.journey_id == journey_id)


def test_rg044_dfs_order_and_branch_by_transition_id():
    _, nm = make_map()
    start = next(b for b in nm.block if b.typ == "Start")
    s1 = add_block(nm, "Scene", "S1")
    s2 = add_block(nm, "Scene", "S2")
    p = add_block(nm, "Pivot", "P1")
    c1 = add_block(nm, "Condition", "C1")
    c2 = add_block(nm, "Condition", "C2")
    # creation order of transitions = id order
    TransitionService.create_transition(nm, start.id, s1.id)   # t1
    TransitionService.create_transition(nm, start.id, p.id)     # t2
    TransitionService.create_transition(nm, s1.id, s2.id)       # t3
    TransitionService.create_transition(nm, p.id, c1.id)        # t4
    TransitionService.create_transition(nm, p.id, c2.id)        # t5
    TransitionService.create_transition(nm, c1.id, s1.id)       # t6 cycle C1 -> S1
    JourneySequenceService.recompute_all(nm)  # RG044
    assert rank(nm, start.id) == 0
    assert rank(nm, s1.id) == 1
    assert rank(nm, s2.id) == 2
    assert rank(nm, p.id) == 3
    assert rank(nm, c1.id) == 4
    assert rank(nm, c2.id) == 5  # cycle memoized: S1 not re-ranked


def test_rg044_unreachable_block_deterministic_fallback():
    _, nm = make_map()
    start = next(b for b in nm.block if b.typ == "Start")
    s1 = add_block(nm, "Scene", "S1")
    orphan_attached = add_block(nm, "Scene", "S3")  # attached but no incoming transition
    TransitionService.create_transition(nm, start.id, s1.id)
    JourneySequenceService.recompute_all(nm)
    assert rank(nm, start.id) == 0
    assert rank(nm, s1.id) == 1
    assert rank(nm, orphan_attached.id) == 2  # after the reachable ones, deterministic


def test_rg044_only_journey_transitions_followed():
    # RG041: a transition belongs to a journey iff both its blocks do
    _, nm = make_map()
    start = next(b for b in nm.block if b.typ == "Start")
    from core.models.data_model import Journey
    j1 = nm.journey[0]
    j2 = Journey(id=nm.get_next_id('journey'), lb="Journey 2", default=False)
    nm.journey.append(j2)
    s1 = add_block(nm, "Scene", "S1")  # journey 1 (default) only
    s2 = Block(id=nm.get_next_id('block'), lb="S2", typ="Scene")
    nm.block.append(s2)
    JourneyService.attach_block(nm, s2.id, j2.id)         # journey 2 only
    TransitionService.create_transition(nm, start.id, s1.id)  # in journey 1
    TransitionService.create_transition(nm, s1.id, s2.id)      # endpoints in different journeys
    JourneySequenceService.recompute_all(nm)
    assert JourneyService.attachment_journey_ids(nm, s1.id) == [j1.id]
    assert JourneyService.attachment_journey_ids(nm, s2.id) == [j2.id]
    # journey 1: Start -> S1 followed; S1 -> S2 NOT followed (S2 not attached to journey 1, RG041)
    assert rank(nm, start.id, journey_id=j1.id) == 0
    assert rank(nm, s1.id, journey_id=j1.id) == 1
    # journey 2: only S2 attached; Start not in j2 -> no DFS, deterministic fallback rank 0
    assert rank(nm, s2.id, journey_id=j2.id) == 0


def test_rg044_recompute_is_idempotent():
    _, nm = make_map()
    start = next(b for b in nm.block if b.typ == "Start")
    s1 = add_block(nm, "Scene")
    TransitionService.create_transition(nm, start.id, s1.id)
    JourneySequenceService.recompute_all(nm)
    first = rank(nm, s1.id)
    JourneySequenceService.recompute_all(nm)
    assert rank(nm, s1.id) == first
