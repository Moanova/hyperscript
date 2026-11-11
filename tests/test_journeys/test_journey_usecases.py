# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_journey_usecases.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for the journey_management use cases (TSK09).

Covers FN023–FN027, FN038 and RG024/RG034/RG038/RG039/RG043/RG062: creation
does not activate, activation, set-as-default (active unchanged, single
default), duplication (attachments copied, not activated), deletion (last
journey refused, reassignment to default, default/active fallback).
"""

from core.models.data_model import Block
from core.services.project_service import ProjectService
from core.services.journey_service import JourneyService
from usecases.project_management import CreateProjectUseCase
from usecases.view_management import CreateBlockUseCase
from usecases.journey_management import (
    CreateJourneyUseCase, UpdateJourneyUseCase, ActivateJourneyUseCase,
    SetDefaultJourneyUseCase, DuplicateJourneyUseCase, DeleteJourneyUseCase,
)


def make_service():
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    return service


def test_fn023_create_journey_does_not_activate():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    active_before = nm.active_journey_id
    j = CreateJourneyUseCase(service).execute()  # FN023
    assert j.lb == "Journey 2"
    assert j.default is False
    assert nm.active_journey_id == active_before  # the active journey is unchanged
    assert service.is_modified is True
    j2 = CreateJourneyUseCase(service).execute(lb="Alt", note="note")
    assert j2.lb == "Alt" and j2.note == "note"


def test_fn024_update_journey():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    j = CreateJourneyUseCase(service).execute()
    UpdateJourneyUseCase(service).execute(j, lb="Renamed", note="")
    assert j.lb == "Renamed"
    assert j.note is None  # empty note stored as None
    assert service.is_modified is True


def test_fn026_activate_journey():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    j = CreateJourneyUseCase(service).execute()
    ActivateJourneyUseCase(service).execute(j)  # FN026
    assert nm.active_journey_id == j.id
    assert nm.get_active_journey() is j


def test_fn038_set_default_replaces_and_keeps_active():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    j = CreateJourneyUseCase(service).execute()
    ActivateJourneyUseCase(service).execute(j)  # active = j, default = journey 1
    SetDefaultJourneyUseCase(service).execute(j)  # FN038/RG062
    assert j.default is True
    assert nm.journey[0].default is False
    assert sum(1 for x in nm.journey if x.default) == 1  # RG039: single default
    assert nm.active_journey_id == j.id  # RG062: active unchanged by the designation


def test_fn025_duplicate_copies_attachments_and_does_not_activate():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    active_before = nm.active_journey_id
    scene = CreateBlockUseCase(service).execute("Scene", lb="S1")  # attached to default journey
    copy = DuplicateJourneyUseCase(service).execute(nm.journey[0])  # FN025
    assert copy.id != nm.journey[0].id
    assert copy.lb == "Journey 1 (copy)"
    assert copy.default is False
    # RG043: attachments of the source journey's blocks are copied
    assert JourneyService.attachment_journey_ids(nm, scene.id) == [nm.journey[0].id, copy.id]
    # RG038: the active journey is unchanged by the duplication
    assert nm.active_journey_id == active_before
    assert service.is_modified is True


def test_fn027_delete_last_journey_refused():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    result = DeleteJourneyUseCase(service).execute(nm.journey[0])  # RG024
    assert result == {'success': False, 'reason': 'last_journey', 'entity_id': nm.journey[0].id}
    assert len(nm.journey) == 1


def test_fn027_delete_reassigns_attachments_and_fixes_default_active():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    j1 = nm.journey[0]  # default + active
    j2 = CreateJourneyUseCase(service).execute(lb="J2")
    # a block attached only to j2
    s2 = Block(id=nm.get_next_id('block'), lb="S2", typ="Scene")
    nm.block.append(s2)
    JourneyService.attach_block(nm, s2.id, j2.id)
    # a block attached to both
    s_both = CreateBlockUseCase(service).execute("Scene", lb="SB")  # attached to j1
    JourneyService.attach_block(nm, s_both.id, j2.id)
    nm.active_journey_id = j2.id
    SetDefaultJourneyUseCase(service).execute(j2)  # j2 default + active

    result = DeleteJourneyUseCase(service).execute(j2)  # FN027
    assert result['success'] is True
    assert len(nm.journey) == 1
    # RG034: s2 (only in j2) reassigned to the default journey (j1, now default); s_both keeps j1 only
    assert JourneyService.attachment_journey_ids(nm, s2.id) == [j1.id]
    assert JourneyService.attachment_journey_ids(nm, s_both.id) == [j1.id]
    # RG039: deleted was default -> oldest remaining (j1) is default; deleted was active -> default becomes active
    assert j1.default is True
    assert nm.active_journey_id == j1.id
    assert service.is_modified is True
