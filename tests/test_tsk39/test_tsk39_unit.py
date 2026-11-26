# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_tsk39_unit.py
# Version      : 1
# Date         : 2026-11-26
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Qt-free unit tests for TSK39 (session 12 test feedback).

1.9: the journey duplication was removed (menu entry + use case).
3.2/4.3: the structured condition was removed from the model (Block has no
`condition` attribute anymore, the update use case takes no `condition`).
"""

import pytest

from core.models.data_model import Block
from core.services.project_service import ProjectService
from usecases.project_management import CreateProjectUseCase
from usecases.view_management import UpdateBlockUseCase, CreateBlockUseCase


def test_1_9_duplicate_journey_usecase_removed():
    import importlib
    import usecases.journey_management as jm
    assert not hasattr(jm, "DuplicateJourneyUseCase")
    with pytest.raises(ImportError):
        importlib.import_module("usecases.journey_management.duplicate_journey_usecase")


def test_3_2_block_has_no_condition_attribute():
    with pytest.raises(TypeError):
        Block(id=1, lb="c", typ="Condition", condition={"kind": "Choice"})
    b = Block(id=2, lb="c", typ="Condition")
    assert not hasattr(b, "condition")


def test_3_2_update_block_usecase_takes_no_condition():
    service = ProjectService()
    CreateProjectUseCase(service).execute()
    block = CreateBlockUseCase(service).execute("Condition", lb="C1")
    uc = UpdateBlockUseCase(service)
    uc.execute(block, lb="C1 renamed", note="n", content="c")  # no condition param
    assert block.lb == "C1 renamed"
    with pytest.raises(TypeError):
        uc.execute(block, condition={"kind": "Choice"})
