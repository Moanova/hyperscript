# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_block_usecases.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for the block use cases of view_management (TSK08).

Covers FN014/FN015/FN016/FN018 and RG025/RG029/RG040/RG042/RG044: creation
with type chosen (Start not creatable), attachment to the active journey when
the filter is active / to the default journey otherwise, immutable type,
duplication ('(copy)', Start not duplicable), deletion cascade with Start
protected, journey attachment list that cannot be emptied.
"""

import pytest

from core.models.data_model import Journey
from core.services.project_service import ProjectService
from core.services.journey_service import JourneyService
from core.services.transition_service import TransitionService
from usecases.project_management import CreateProjectUseCase
from usecases.view_management import (
    CreateBlockUseCase, UpdateBlockUseCase, DuplicateBlockUseCase, DeleteBlockUseCase,
)


def make_service():
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    return service


def test_fn014_create_block_attached_to_default_journey_when_filter_off():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    block = CreateBlockUseCase(service).execute("Scene", lb="Opening")  # RG040: filter off -> default journey
    assert block.typ == "Scene"
    assert block.lb == "Opening"
    assert service.is_modified is True
    assert JourneyService.attachment_journey_ids(nm, block.id) == [nm.journey[0].id]


def test_rg040_attachment_to_active_journey_when_filter_on():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    j2 = Journey(id=nm.get_next_id('journey'), lb="Journey 2", default=False)
    nm.journey.append(j2)
    nm.active_journey_id = j2.id  # filter active on journey 2
    block = CreateBlockUseCase(service).execute("Scene", filter_active=True)  # RG040
    assert JourneyService.attachment_journey_ids(nm, block.id) == [j2.id]


def test_rg025_start_not_creatable_and_invalid_type_refused():
    service = make_service()
    with pytest.raises(ValueError):
        CreateBlockUseCase(service).execute("Start")  # RG025
    with pytest.raises(ValueError):
        CreateBlockUseCase(service).execute("Bogus")  # RG029/BLOCK_TYPES


def test_fn015_update_attributes_and_condition_only_on_condition():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    scene = CreateBlockUseCase(service).execute("Scene", lb="S1")
    cond = CreateBlockUseCase(service).execute("Condition", lb="C1")
    uc = UpdateBlockUseCase(service)
    uc.execute(scene, lb="S1 renamed", note="a note", content="text")
    assert (scene.lb, scene.note, scene.content) == ("S1 renamed", "a note", "text")
    assert scene.typ == "Scene"  # RG029: the type is immutable, edition never changes it
    with pytest.raises(ValueError):
        uc.execute(scene, condition={"kind": "Flag", "label": "x"})  # condition only on Condition blocks
    uc.execute(cond, condition={"kind": "Artefact", "ref_agent_id": 3, "label": "has key"})  # FN035
    assert cond.condition["kind"] == "Artefact"
    with pytest.raises(ValueError):
        uc.execute(cond, condition={"kind": "Bogus"})


def test_rg042_journey_list_cannot_be_emptied():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    j2 = Journey(id=nm.get_next_id('journey'), lb="Journey 2", default=False)
    nm.journey.append(j2)
    block = CreateBlockUseCase(service).execute("Scene")
    uc = UpdateBlockUseCase(service)
    with pytest.raises(ValueError):
        uc.execute(block, journey_ids=[])  # RG042: cannot detach from the last journey
    uc.execute(block, journey_ids=[nm.journey[0].id, j2.id])
    assert set(JourneyService.attachment_journey_ids(nm, block.id)) == {nm.journey[0].id, j2.id}
    uc.execute(block, journey_ids=[j2.id])
    assert JourneyService.attachment_journey_ids(nm, block.id) == [j2.id]


def test_fn016_duplicate_block():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    start = next(b for b in nm.block if b.typ == "Start")
    scene = CreateBlockUseCase(service).execute("Scene", lb="S1")
    copy = DuplicateBlockUseCase(service).execute(scene)
    assert copy.id != scene.id
    assert copy.lb == "S1 (copy)"
    assert copy.typ == scene.typ
    assert JourneyService.attachment_journey_ids(nm, copy.id) == [nm.journey[0].id]  # RG040
    with pytest.raises(ValueError):
        DuplicateBlockUseCase(service).execute(start)  # RG025: Start not duplicable


def test_fn018_delete_block_cascade_and_start_protected():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    start = next(b for b in nm.block if b.typ == "Start")
    scene = CreateBlockUseCase(service).execute("Scene", lb="S1")
    TransitionService.create_transition(nm, start.id, scene.id)
    with pytest.raises(ValueError):
        DeleteBlockUseCase(service).execute(start.id)  # RG025
    removed = DeleteBlockUseCase(service).execute(scene.id)  # RG023
    assert removed is not None and len(removed['transition']) == 1
    assert all(b.id != scene.id for b in nm.block)
    assert service.is_modified is True
    assert DeleteBlockUseCase(service).execute(999) is None
