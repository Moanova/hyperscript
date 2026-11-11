# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_journey_filter_service.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for JourneyFilterService (TSK08) - RG041/RG048.

Membership is derived: a transition belongs to a journey iff both its
endpoints do; a participation/relationship iff its anchor block does.
Filter off (journey_id=None) = everything visible. The dimmed opacity is read
from config.json (RG048/RG059).
"""

from core.models.data_model import Block, Journey, Participation, Relationship
from core.services.project_service import ProjectService
from core.services.transition_service import TransitionService
from core.services.journey_service import JourneyService
from core.services.journey_filter_service import JourneyFilterService
from usecases.project_management import CreateProjectUseCase


def make_map():
    service = ProjectService()
    project = CreateProjectUseCase(service).execute()
    return service, project.narrative_maps[0]


def add_block(narrative_map, typ, lb=None, journey_id=None):
    block = Block(id=narrative_map.get_next_id('block'), lb=lb or typ, typ=typ)
    narrative_map.block.append(block)
    JourneyService.attach_block(narrative_map, block.id,
                                journey_id or narrative_map.journey[0].id)
    return block


def test_rg048_filter_off_shows_everything():
    _, nm = make_map()
    start = next(b for b in nm.block if b.typ == "Start")
    s = add_block(nm, "Scene")
    t = TransitionService.create_transition(nm, start.id, s.id)
    assert JourneyFilterService.visible_block_ids(nm, None) == {start.id, s.id}
    assert JourneyFilterService.visible_transition_ids(nm, None) == {t.id}


def test_rg041_derived_membership():
    _, nm = make_map()
    j1 = nm.journey[0]
    j2 = Journey(id=nm.get_next_id('journey'), lb="Journey 2", default=False)
    nm.journey.append(j2)
    start = next(b for b in nm.block if b.typ == "Start")  # attached to j1 only
    s1 = add_block(nm, "Scene", "S1", journey_id=j1.id)
    s2 = add_block(nm, "Scene", "S2", journey_id=j2.id)  # j2 only
    t = TransitionService.create_transition(nm, start.id, s1.id)  # both in j1
    nm.participation.append(Participation(id=nm.get_next_id('participation'), block_id=s1.id, agent_id=1))
    nm.participation.append(Participation(id=nm.get_next_id('participation'), block_id=s2.id, agent_id=1))
    nm.relationship.append(Relationship(id=nm.get_next_id('relationship'), block_id=s2.id,
                                        agent_a_id=1, agent_b_id=2, typ="friend"))

    # journey 1: Start + S1 visible; transition Start->S1 visible (both endpoints in j1)
    assert JourneyFilterService.visible_block_ids(nm, j1.id) == {start.id, s1.id}
    assert JourneyFilterService.visible_transition_ids(nm, j1.id) == {t.id}
    assert len(JourneyFilterService.visible_participation_ids(nm, j1.id)) == 1
    assert JourneyFilterService.visible_relationship_ids(nm, j1.id) == set()
    # journey 2: only S2; the transition is not visible (Start not in j2)
    assert JourneyFilterService.visible_block_ids(nm, j2.id) == {s2.id}
    assert JourneyFilterService.visible_transition_ids(nm, j2.id) == set()
    assert len(JourneyFilterService.visible_participation_ids(nm, j2.id)) == 1
    assert len(JourneyFilterService.visible_relationship_ids(nm, j2.id)) == 1


def test_rg048_opacity_from_config():
    # RG048/RG059: dimmed opacity is read from config.json (journey_filter_opacity = 0.25)
    assert JourneyFilterService.filter_opacity() == 0.25
