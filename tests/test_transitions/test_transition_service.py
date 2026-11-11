# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_transition_service.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for TransitionService (TSK08).

Covers:
- RG028: block-type chaining matrix (allowed/forbidden pairs, Start->Pivot and
  Condition->End allowed, Condition->Condition forbidden), one transition max
  per ordered pair, cycles allowed
- RG023: deleting a block cascades to transitions, participations,
  relationships and journey nodes
- RG041: deleting a transition removes no journey attachment
"""

import pytest

from core.models.data_model import Block, Participation, Relationship
from core.services.project_service import ProjectService
from core.services.transition_service import TransitionService, ALLOWED_TARGET_TYPES
from core.services.journey_service import JourneyService
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


def test_rg028_matrix_matches_spec():
    # RG028 adopted matrix (session 03)
    assert ALLOWED_TARGET_TYPES == {
        "Start": {"Scene", "Pivot"},
        "Scene": {"Scene", "Pivot", "End"},
        "Pivot": {"Condition"},
        "Condition": {"Scene", "End"},
        "End": set(),
    }


def test_rg028_allowed_pairs():
    _, nm = make_map()
    start = next(b for b in nm.block if b.typ == "Start")
    scene = add_block(nm, "Scene")
    pivot = add_block(nm, "Pivot")
    cond = add_block(nm, "Condition")
    end = add_block(nm, "End")
    allowed = [
        (start.id, scene.id), (start.id, pivot.id),          # Start -> Scene, Pivot
        (scene.id, scene.id), (scene.id, pivot.id), (scene.id, end.id),  # Scene -> Scene, Pivot, End
        (pivot.id, cond.id),                                   # Pivot -> Condition
        (cond.id, scene.id), (cond.id, end.id),                # Condition -> Scene, End
    ]
    for src, dst in allowed:
        assert TransitionService.can_create_transition(nm, src, dst), (src, dst)
        assert TransitionService.create_transition(nm, src, dst) is not None


def test_rg028_forbidden_pairs():
    _, nm = make_map()
    start = next(b for b in nm.block if b.typ == "Start")
    scene = add_block(nm, "Scene")
    pivot = add_block(nm, "Pivot")
    cond = add_block(nm, "Condition")
    end = add_block(nm, "End")
    forbidden = [
        (start.id, start.id), (start.id, cond.id), (start.id, end.id),
        (scene.id, start.id),
        (pivot.id, scene.id), (pivot.id, pivot.id), (pivot.id, end.id), (pivot.id, start.id),
        (cond.id, pivot.id), (cond.id, cond.id), (cond.id, start.id),  # Condition -> Condition forbidden (no AND chaining)
        (end.id, scene.id), (end.id, end.id), (end.id, start.id),      # End: no outgoing transition
    ]
    for src, dst in forbidden:
        assert not TransitionService.can_create_transition(nm, src, dst), (src, dst)
        assert TransitionService.create_transition(nm, src, dst) is None


def test_rg028_unknown_blocks_refused():
    _, nm = make_map()
    assert not TransitionService.can_create_transition(nm, 999, 1)
    assert not TransitionService.can_create_transition(nm, 1, 999)


def test_rg028_unique_ordered_pair():
    _, nm = make_map()
    start = next(b for b in nm.block if b.typ == "Start")
    s1 = add_block(nm, "Scene", "S1")
    s2 = add_block(nm, "Scene", "S2")
    assert TransitionService.create_transition(nm, s1.id, s2.id) is not None
    assert TransitionService.create_transition(nm, s1.id, s2.id) is None  # duplicate ordered pair refused
    assert TransitionService.create_transition(nm, s2.id, s1.id) is not None  # reverse pair is a distinct ordered pair


def test_rg028_cycles_allowed():
    _, nm = make_map()
    s = add_block(nm, "Scene", "S1")
    p = add_block(nm, "Pivot", "P1")
    c = add_block(nm, "Condition", "C1")
    assert TransitionService.create_transition(nm, s.id, p.id) is not None
    assert TransitionService.create_transition(nm, p.id, c.id) is not None
    assert TransitionService.create_transition(nm, c.id, s.id) is not None  # cycle S1 -> P1 -> C1 -> S1


def test_delete_transition_removes_no_attachment():
    # RG041: membership is derived from blocks; no journey_node references a transition
    _, nm = make_map()
    start = next(b for b in nm.block if b.typ == "Start")
    s = add_block(nm, "Scene")
    t = TransitionService.create_transition(nm, start.id, s.id)
    before = len(nm.journey_node)
    assert TransitionService.delete_transition(nm, t.id) is True
    assert len(nm.transition) == 0
    assert len(nm.journey_node) == before
    assert TransitionService.delete_transition(nm, t.id) is False


def test_rg023_delete_block_cascade():
    _, nm = make_map()
    start = next(b for b in nm.block if b.typ == "Start")
    s = add_block(nm, "Scene", "S1")
    e = add_block(nm, "End", "E1")
    t1 = TransitionService.create_transition(nm, start.id, s.id)
    t2 = TransitionService.create_transition(nm, s.id, e.id)
    agent_id = 1
    nm.participation.append(Participation(id=nm.get_next_id('participation'), block_id=s.id, agent_id=agent_id))
    nm.relationship.append(Relationship(id=nm.get_next_id('relationship'), block_id=s.id,
                                        agent_a_id=agent_id, agent_b_id=2, typ="friend"))
    removed = TransitionService.delete_block_cascade(nm, s.id)  # RG023
    assert removed is not None
    assert removed['block'][0].id == s.id
    assert {t.id for t in removed['transition']} == {t1.id, t2.id}
    assert len(removed['participation']) == 1
    assert len(removed['relationship']) == 1
    assert len(removed['journey_node']) == 1
    assert all(b.id != s.id for b in nm.block)
    assert all(t.from_block_id != s.id and t.to_block_id != s.id for t in nm.transition)
    assert all(p.block_id != s.id for p in nm.participation)
    assert all(r.block_id != s.id for r in nm.relationship)
    assert all(jn.block_id != s.id for jn in nm.journey_node)
    assert TransitionService.delete_block_cascade(nm, 999) is None


def test_tsk14_port_visibility_derived_from_matrix():
    # TSK14: port visibility is derived from the RG028 matrix (single source
    # of truth) - RG025: Start never incoming; RG028: End never outgoing
    from core.services.transition_service import type_allows_incoming, type_allows_outgoing
    assert type_allows_outgoing("Start") is True
    assert type_allows_outgoing("Scene") is True
    assert type_allows_outgoing("Pivot") is True
    assert type_allows_outgoing("Condition") is True
    assert type_allows_outgoing("End") is False
    assert type_allows_incoming("Start") is False
    assert type_allows_incoming("Scene") is True
    assert type_allows_incoming("Pivot") is True
    assert type_allows_incoming("Condition") is True
    assert type_allows_incoming("End") is True
    # consistency with the matrix itself
    for typ, targets in ALLOWED_TARGET_TYPES.items():
        assert type_allows_outgoing(typ) == bool(targets)
        assert type_allows_incoming(typ) == any(typ in tgts for tgts in ALLOWED_TARGET_TYPES.values())
