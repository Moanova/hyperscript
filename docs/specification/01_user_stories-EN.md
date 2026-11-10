# Hyperscript ::: User Stories

## Document Version
- **Version**: 1.0
- **Date**: 2026-11-09
- **Status**: initial.

---

## SU001: Manage a Narrative Project
- **Description**: As an author, I can create, open, save, rename and close a narrative project in order to group, retrieve and continue working on my narrative map.
- **Details**:
    - A project is a local document containing the project metadata, the agents and one or more narrative maps.
    - Only one project can be open in the application at any time.
    - A newly created project is an unsaved project: it exists in memory but is not associated with any file until the user saves it.
    - Each project has a stable identifier, a name, a creation date and a last modification date.
    - The file path is an application state; it is not portable business data of the project.
    - A new project is named "New project" and contains a narrative map named "Main narrative map".
- **Acceptance criteria**:
    - The user can create a project from the menu, a keyboard shortcut or the welcome message.
    - The user can open a valid project file from the file system; in case of an invalid, incompatible or unreadable file, the application shows a clear error and keeps the current project unchanged.
    - The user can save an unsaved project by choosing a name and a location; save the changes of a project already associated with a file without a new dialog; save a copy under another name or location (the copy becomes the current project).
    - The user can close a project; if the project is modified upon closing, opening, creating or exiting, the application offers "Save", "Don't save", "Cancel".
    - A saved project is added to the recent projects list, which respects the configured limit and removes files that no longer exist.
- **MVP scope**:
    - Each project contains a single narrative map.
    - No migration of existing planoscript projects.


## SU002: Manage a Narrative Map
- **Description**: As an author, I can name and edit the content of my project's narrative map in order to define my story.
- **Details**:
    - A narrative map belongs to one and only one project; it has a stable identifier, a name, a creation date and a last modification date.
    - A project always contains at least one narrative map.
    - A map is considered modified when the user adds, modifies or deletes a block, a transition, a participation or a relationship, or changes the position of a block in the workspace.
    - Changing the scroll bars position is not a map modification.
- **Acceptance criteria**:
    - The user can rename the map by directly editing its label or via an edit dialog.
    - Any modification updates the last modification date of the map and of the project.
- **MVP scope**:
    - A single narrative map per project: creating, duplicating, deleting, navigating between maps and importing/exporting a map are not available. Only renaming and editing the content are functional in the MVP (the file export, SU007, is out of the MVP — "Files › Export Map" greyed out; the in-app preview, "Export" view (SU010), is part of the minimal MVP).


## SU003: Manage a Narrative Block
- **Description**: As an author, I can create, name, move, edit or delete a narrative block in order to define the content of the sequences of my story.
- **Details**:
    - The narrative block is the story unit of the narrative map. Its type — Start, Scene, Pivot, Condition or End — is chosen at creation and immutable afterwards; each type has a specific visual rendering.
    - Each block has an identifier unique within the map, a label (not subject to uniqueness), a note and a narrative content.
    - Each block has two ports, incoming and outgoing, intended for creating transitions.
    - Each block can be moved in the workspace but not resized; it automatically snaps to the grid at creation and when moved; its position is kept between sessions.
    - When a narrative map is created, a single Start block is created automatically.
    - An End block cannot have an outgoing transition.
    - A Pivot block has at least two outgoing transitions; the Scene → Pivot promotion is automatic and one-way when a second outgoing transition is created (never the other way round).
    - A Condition block has exactly one incoming transition (from a Pivot) and one outgoing transition (to the guarded scene); it carries a structured condition: kind (choice / artefact / skill / flag), optional reference to an Artefact agent, label. Chaining Condition blocks equals an AND; two Condition blocks from the same Pivot equal an OR.
    - Attachment to journeys: blocks (not transitions) are attached to journeys. No orphan block: every block belongs to at least one journey; every newly created block is automatically attached to the default journey; a block cannot be removed from its last journey.
    - Deleting a block cascades to its transitions, participations, anchored relationships and journey attachments.
- **Acceptance criteria**:
    - The user can create a block from the main menu or the context menu, choosing its type; the block is automatically attached to the default journey and positioned on the grid at the designated location.
    - The user can duplicate a block (copy with a distinct name and a new identifier, attached to the default journey).
    - The user can edit the editable attributes of a block via an edit dialog.
    - The user can delete a block with confirmation; the deletion cascades as described above.
    - The user can move a block by drag-and-drop (mouse, stylus or touch) with automatic grid snapping.
    - Any creation, duplication, modification, move or deletion of a block marks the map, and therefore the project, as modified.
- **MVP scope**:
    - No toolbar: actions are handled through menus only.


## SU004: Manage a Transition Between Blocks
- **Description**: As an author, I can create, annotate, edit or delete a transition between two blocks in order to define the sequences of my story.
- **Details**:
    - A transition is directed from a source block to a target block; chaining is free, including cycles (e.g. Scene → Pivot → Condition → the same Scene).
    - There can be only one transition per ordered pair of blocks.
    - A transition carries a text note, shown in a tooltip on hover. It carries no condition: the structured condition is carried by the Condition block.
    - Derived journey membership: a transition belongs to a journey if and only if both its blocks belong to it.
    - Deleting a transition deletes its journey attachments; it is independent of block deletion, except for the cascade defined in SU003.
- **Acceptance criteria**:
    - The user can start creating a transition from the "Project" menu or the context menu: select the source block, a temporary trace follows the cursor until the click on the target block's port.
    - The application prevents creating a duplicate transition between two blocks already linked.
    - The user can annotate a transition with free text via an edit dialog.
    - The user can delete a transition with prior confirmation.
    - Any creation, modification or deletion of a transition marks the map, and therefore the project, as modified.
- **MVP scope**:
    - No toolbar: menu actions only.


## SU005: Manage a Journey
- **Description**: As an author, I can create, name, describe, duplicate, activate or delete a journey in order to define the alternative threads of my story.
- **Details**:
    - A journey belongs to a narrative map; it has an identifier unique within the map, plus an editable label and note.
    - Each map always contains at least one journey; when the map is created, an initial journey is created, activated and given a default name.
    - Blocks are attached to journeys; a block can belong to several journeys. The journey membership of a transition is derived from its two blocks; that of a participation or a relationship is derived from its anchor block.
    - When a new journey is created, it automatically becomes the active journey.
    - Every newly created block is attached to the default journey.
    - Deleting the last journey of a map is impossible; the application shows an explanatory message.
    - The reading sequence of a journey is computed depth-first from the Start block (it is used for the preview and the export).
- **Acceptance criteria**:
    - The user can create a journey from the "Project" menu; it automatically becomes the current journey.
    - The user can rename a journey and edit its note via an edit dialog.
    - The user can duplicate a journey (distinct name, new identifier; the block attachments of the source journey are copied).
    - The user can activate a journey by selecting it in the journey list or from the "Project" menu.
    - The user can delete a journey with prior confirmation, except if it is the last one; if the deleted journey was the default one, the oldest remaining journey becomes the default.
    - The user can change the journeys a block is attached to, without being able to remove it from its last journey.
    - Any operation on a journey marks the map, and therefore the project, as modified.
- **MVP scope**:
    - No journey consistency check (dead ends, unfinished branches, single-branch Pivot, unreachable End): post-MVP feature.
    - No toolbar: menu actions only.


## SU006: Visualize the Narrative Map (view "Journeys")
- **Description**: As an author, I can visualize and navigate in the workspace of the narrative map — the "Journeys" view, graph of blocks and their transitions — in order to consult, structure and validate my story.
- **Details**:
    - The workspace is virtually unlimited; navigation is done with horizontal and vertical scroll bars; the alignment grid is always visible and active.
    - A journey filter allows displaying either all journeys or a selected journey; visibility follows derived membership (blocks of the journey, transitions whose two blocks belong to the journey, participations and relationships whose anchor block belongs to the journey).
    - The scroll bars position is not business data and is not kept between sessions.
    - Zoom is to be defined during the design phase.
- **Acceptance criteria**:
    - The application adapts to the window size without loss of functionality (minimum size 1280×720).
    - The user can navigate in the workspace with the scroll bars; the application remains stable over a 10,000×10,000 pixels workspace and responsive (no perceptible latency) for a map containing up to 100 blocks.
    - If the journey filter is active, the user can switch from one journey to another via the journey list or the "Project" menu; the display updates instantly.
    - The displayed blocks and transitions are rendered according to their saved coordinates and graphical representation.
    - Moving the scroll bars does not mark the map as modified.
- **MVP scope**:
    - No toolbars.
    - View scope not decided beyond the minimum: "Journeys" view and "Export" view (SU010).
    - The application exclusively targets Windows PCs.
    - Zoom is to be defined during the design phase.


## SU007: Export the Narrative Map
- **Description**: As an author, I can export my narrative map as a standalone HTML document, readable in a standard browser, in order to validate my story and share it with my team.
- **Details**:
    - The reading export is a standalone document: no server, no Internet connection, no external dependency.
    - It generates a folder named after the narrative map, containing an index file and all the pages needed for hypertext navigation.
    - The reading order is the reading sequence of the journey (computed from the Start block), independent of the graphical positions.
    - Per block, the export renders: label as a paragraph title and content as body text (label only if the content is empty); transitions are rendered inline; conditions are rendered on their branch; agent relationships are listed under their anchor block; a final section summarizes the state of the relationships (last known type per agent pair in the journey).
    - Each reading page offers a link back to the index.
    - The export operation marks neither the map nor the project as modified.
- **Acceptance criteria**:
    - The user can launch the export from the "File" menu.
    - The generated document displays correctly in standard browsers (Chrome, Firefox, Edge) without an Internet connection.
    - An intermediate page lists the journeys of the map; clicking a journey displays the complete linear reading of its sequence.
- **MVP scope**:
    - The file export is **out of the MVP scope** ("Files › Export Map" greyed out); in the MVP, only the in-app preview ("Export" view, SU010/FN033) is available.
    - The exact scope of the reading export (pages, reading modes) will be specified later for the post-MVP version.
    - The technical export for reimport and the "by events" reading mode are to be defined during the design phase.


## SU008: Manage agent-block Participations
- **Description**: As an author, I can associate an agent with one or more blocks, and conversely associate a block with one or more agents, in order to define who takes part in each step of my story.
- **Details**:
    - An agent is a project-level element, of type Character or Artefact. A block belongs to a narrative map. A participation links an agent to a block.
    - A participation is non-oriented; there can be only one per (agent, block) pair.
    - Derived journey membership: a participation belongs to a journey if and only if its block belongs to it.
    - Two persistent entry points: the context menu of a block in the "Journeys" view ("Associate agents...") and the matrix of the agents view (SU009, initialized) — checking associates, unchecking dissociates; both entry points modify the same data and are immediately reflected in each other.
    - The participating agents of a block are represented by badges displayed on the block in the "Journeys" view.
    - Deleting an agent or a block cascades to its participations.
- **Acceptance criteria**:
    - The user can associate an agent with a block from the block's context menu in the "Journeys" view, or from the agents view; the user can dissociate from either entry point.
    - The user can create a new agent from the association dialog and associate it immediately with the current block.
    - The application prevents a duplicate participation between an agent and a block.
    - Participations modified from one view are immediately visible in the other.
    - Any agent participating in at least one block is visible as a badge on that block in the "Journeys" view.
    - Any association, dissociation or agent creation marks the map, and therefore the project, as modified.
- **MVP scope**:
    - Participations are part of the MVP.
    - The note carried by a participation is not editable in the MVP.


## SU009: Manage the agents view — initialized, to be finalized after the design phase
- **Description**: As an author, I can visualize and edit the participations between the project's agents and the blocks of the narrative map in a second workspace, in order to manage the agents independently from the block graph.
- **Status**: initialized scenario — to be finalized after the design phase. The MVP view scope is not decided yet (minimum: "Journeys" view and "Export" view).
- **Elements to specify during design**: column order (the Start block first), manual reordering kept between sessions, cross-view navigation between the "Journeys" and agents views.


## SU010: Preview the export — initialized, to be finalized after the design phase
- **Description**: As an author, I can visualize in the application a reading preview of my narrative map, as it will be rendered by the export (the "Export" workspace), in order to validate my story before sharing it.
- **Status**: initialized scenario — to be finalized after the design phase. The "Export" view is part of the minimal MVP scope and may be renamed later.
- **Elements to specify during design**: read-only with inert links, dynamic according to the journey filter, reading order (reading sequence), rendering of relationships under their anchor block and of the "state of relationships" section, possible orphan components.


## SU011: Manage a Relationship Between Agents
- **Description**: As an author, I can create, annotate, edit or delete a typed relationship between two agents, anchored to a block, in order to follow the evolution of the relationships between characters or artefacts along my story.
- **Details**:
    - A relationship is binary: it links exactly two agents. An evolution towards relationships involving more than two agents is post-MVP.
    - It is directed and typed; the type is read from a value list defined in a configuration file (enriching this list by the author is post-MVP).
    - It is anchored to a block: "at this point of the story, the relationship A —type→ B holds".
    - There can be only one relationship per (block, agent pair, type).
    - The history of an agent pair is the set of its anchored relationships, ordered by the position of their block in the journey; the current state of the pair at a block is the last relationship anchored to a block located before or at the same rank in that journey (derived data, never stored).
    - Derived journey membership: a relationship belongs to a journey if and only if its anchor block belongs to it.
    - Deleting an agent or a block cascades to its relationships.
- **Acceptance criteria**:
    - The user can create a relationship from the "Project" menu or the context menu: choice of the two agents, the type (from the configured list) and the anchor block.
    - The user can edit a relationship (type, anchor block, note, content) via an edit dialog.
    - The user can delete a relationship with prior confirmation.
    - The application prevents duplicates (block, agent pair, type).
    - Any creation, modification or deletion of a relationship marks the map, and therefore the project, as modified.
- **MVP scope**:
    - Agent-agent relationships are part of the MVP (model + configured type list).
    - The dedicated view (SU012) is initialized separately.


## SU012: Manage the "Relationships" view — initialized, to be finalized after the design phase
- **Description**: As an author, I can visualize the graph of agents and their relationships (arcs labeled by type, annotated with anchor blocks) in a dedicated workspace, with cross-navigation to the anchor block in the "Journeys" view.
- **Status**: initialized scenario — the mockup of this view will be defined during the design phase.
