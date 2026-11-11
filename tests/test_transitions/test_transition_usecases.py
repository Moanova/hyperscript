# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_transition_usecases.py
# Version      : 1
# Date         : 2026-11-11
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for the transition use cases of view_management (TSK08/TSK12).

Covers FN020/FN021/FN022: creation through the use case (RG028 validation,
modified flag, sequence recompute RG044), note edition (no condition on the
transition), deletion.
"""

from core.models.data_model import Block
from core.services.project_service import ProjectService
from core.services.journey_service import JourneyService
from usecases.project_management import CreateProjectUseCase
from usecases.view_management import (
    CreateTransitionUseCase, UpdateTransitionUseCase, DeleteTransitionUseCase,
)


def make_service():
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    return service


def add_block(narrative_map, typ, lb=None):
    block = Block(id=narrative_map.get_next_id('block'), lb=lb or typ, typ=typ)
    narrative_map.block.append(block)
    JourneyService.attach_block(narrative_map, block.id, narrative_map.journey[0].id)
    return block


def test_fn020_usecase_creates_and_marks_modified():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    start = next(b for b in nm.block if b.typ == "Start")
    scene = add_block(nm, "Scene")
    t = CreateTransitionUseCase(service).execute(start.id, scene.id, note="go")
    assert t is not None and t.note == "go"
    assert service.is_modified is True
    # RG044: the sequence was recomputed
    rank = next(jn.sequence_order for jn in nm.journey_node
                if jn.block_id == scene.id and jn.journey_id == nm.journey[0].id)
    assert rank == 1


def test_fn020_usecase_refuses_forbidden_pair():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    start = next(b for b in nm.block if b.typ == "Start")
    end = add_block(nm, "End")
    assert CreateTransitionUseCase(service).execute(start.id, end.id) is None  # RG028: Start -> End forbidden


def test_fn021_update_note_only():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    start = next(b for b in nm.block if b.typ == "Start")
    scene = add_block(nm, "Scene")
    t = CreateTransitionUseCase(service).execute(start.id, scene.id)
    UpdateTransitionUseCase(service).execute(t, note="new note")
    assert t.note == "new note"
    assert not hasattr(t, 'condition') or getattr(t, 'condition', None) is None  # no condition key on transitions


def test_fn022_delete_usecase():
    service = make_service()
    nm = service.current_project.narrative_maps[0]
    start = next(b for b in nm.block if b.typ == "Start")
    scene = add_block(nm, "Scene")
    t = CreateTransitionUseCase(service).execute(start.id, scene.id)
    assert DeleteTransitionUseCase(service).execute(t.id) is True
    assert len(nm.transition) == 0
    assert service.is_modified is True
    assert DeleteTransitionUseCase(service).execute(t.id) is False
