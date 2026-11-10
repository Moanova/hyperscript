# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : create_project_usecase.py
# Version      : 1
# Date         : 2026-11-10
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
from core.models.data_model import Project, Block, Journey, Journey_node
from core.services.project_service import ProjectService

class CreateProjectUseCase:

    def __init__(self, project_service: ProjectService):
        self.project_service = project_service

    def execute(self) -> Project:
        project = self.project_service.create_project()
        self._initialize_narrative_map(project.narrative_maps[0])
        return project

    def _initialize_narrative_map(self, narrative_map) -> None:
        """
        Apply the creation invariants to a newly created narrative map.

        RG037/RG039: a default journey is automatically created and activated.
        RG025: each narrative map has one and only one Start block, created
        automatically, never deletable nor duplicable.
        RG040: no orphan block - the Start block is attached to the default
        journey at creation.
        """
        # RG037: create the default journey and activate it
        default_journey = Journey(
            id=narrative_map.get_next_id('journey'),
            lb="Journey 1",
            default=True
        )
        narrative_map.journey.append(default_journey)
        narrative_map.active_journey_id = default_journey.id

        # RG025: create the unique Start block
        start_block = Block(
            id=narrative_map.get_next_id('block'),
            lb="Start",
            typ="Start"
        )
        narrative_map.block.append(start_block)

        # RG040: attach the Start block to the default journey
        narrative_map.journey_node.append(Journey_node(
            id=narrative_map.get_next_id('journey_node'),
            journey_id=default_journey.id,
            block_id=start_block.id,
            sequence_order=0  # placeholder; real rank computed by the sequence service
        ))
