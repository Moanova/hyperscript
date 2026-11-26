# Hyperscript ::: Implementation traceability matrix


- **Last modification date**: 11-11-2026
- **Description**: status and code location of the implementation of business rules (RG), features (FN), general menu entries and user stories (SU) in the codebase.


## Conventions

- **Statuses**: `not-started` (specified, no code yet) ; `stub` (stubbed menu entry, empty action) ; `greyed-MVP` (present but greyed out in the MVP) ; `partial` (partially implemented) ; `implemented` (implemented, test passing) ; `post-MVP` (out of the MVP scope).
- **Bidirectional links**: every implemented RG/FN carries its ID in a code comment (`# RG040: …`, `# FN023: …` — planoscript practice); unit tests named `test_rgXXX_*.py`; application tests `test_fnXXX_*.py` (pywinauto, skipped without a GUI session), specified by their `T-xxx` ID in `tests/SPECIFICATION.md`.
- This matrix is the human-readable index of those links; the IDs (RG/FN/SU/T) are stable anchors, verifiable by grep in `src/` and `tests/`.
- **Update rule**: at each kanban task move to Review then Done; a row only becomes `implemented` when the ID comment is present in the code and the associated test exists and passes.
- **Initial state** (specification phase, no code yet): all rows are `not-started`, except MVP-greyed entries (`greyed-MVP`) flagged in `05_menu` and `03_features`.

---

## A. Business rules (`02_business_rules-*.md`)


### 1. Project management and lifecycle

| RG | Summary | Status | Code (file · symbol) | Unit test | Notes |
| --- | --- | --- | --- | --- | --- |
| RG001 | A project is a local document (JSON format) containing its metadata, its agents… | not-started | — | — | — |
| RG002 | Only one project can be open in the application at any time. | not-started | — | — | — |
| RG003 | A newly created project is an unsaved project: it exists in memory but is not… | implemented | src/core/services/project_service.py · ProjectService.create_project | tests/test_project/test_project_service.py | projet non enregistré (pas de fichier associé) |
| RG004 | Each project has a stable identifier, a name, a creation date, a last… | not-started | — | — | — |
| RG005 | Projects saved or opened successfully are added to the recent projects list,… | not-started | — | — | — |
| RG006 | The "Save" command is enabled only when the open project is modified; "Save… | not-started | — | — | — |
| RG007 | When no project is open, the entries of the Files (Close, Save, Save as...),… | not-started | — | — | — |
| RG008 | When a project is opened or created, the entries of the Files (Close, Save,… | not-started | — | — | — |
| RG009 | Opening a project replaces the current project only after the selected file has… | implemented | src/core/services/project_service.py · load_project | tests/test_project/test_project_service.py | fichier invalide/incompatible : projet courant inchangé |
| RG010 | The application opens a project only if its format version is supported; it… | implemented | src/core/services/project_service.py · load_project (format_version) | tests/test_project/test_project_service.py | — |
| RG011 | Saving replaces the existing file only after the new version has been fully and… | not-started | — | — | — |
| RG012 | "Save as..." creates or replaces a file at the chosen location (with… | not-started | — | — | — |
| RG013 | A new project is named "New project" and contains a narrative map named "Main… | implemented | project_service.py · create_project + usecases/project_management/create_project_usecase.py | tests/test_project/test_project_service.py | — |
| RG014 | A project always contains at least one narrative map (in the MVP: exactly one). | not-started | — | — | — |
| RG015 | Only one instance of the application can run at a time; if an instance is… | not-started | — | — | — |
| RG016 | No existing planoscript project is migrated: planoscript files are considered… | implemented | project_service.py · load_project (rejet si format_version absent) | tests/test_project/test_project_service.py | fichiers planoscript = incompatibles |
| RG017 | File export is out of the MVP scope (only the in-app preview, "Export" view, is… | not-started | — | — | — |

### 2. Narrative map structure

| RG | Summary | Status | Code (file · symbol) | Unit test | Notes |
| --- | --- | --- | --- | --- | --- |
| RG018 | Each narrative map has a stable identifier. | not-started | — | — | — |
| RG019 | Each block, transition, participation, relationship, journey and… | not-started | — | — | — |
| RG020 | The labels of blocks, transitions, participations, relationships, journeys and… | not-started | — | — | — |
| RG021 | A narrative map always contains at least one journey. | not-started | — | — | — |
| RG022 | Deleting a narrative map is irreversible and deletes all its content (blocks,… | not-started | — | — | — |
| RG023 | Deleting a block cascades to its transitions, participations, anchored… | implemented | core/services/transition_service.py (delete_block_cascade) | tests/test_transitions/test_transition_service.py | cascade tested |
| RG024 | Deleting the last journey of a map is impossible. | implemented | usecases/journey_management/delete_journey_usecase.py | tests/test_journeys/test_journey_usecases.py | last journey refused (UI message) |
| RG025 | Each narrative map has one and only one Start block, created automatically when… | implemented | usecases/project_management/create_project_usecase.py; usecases/view_management/ (delete/duplicate) | tests/test_project/test_project_service.py; tests/test_blocks/test_block_usecases.py | Start never deletable nor duplicable |
| RG026 | An End block cannot receive any outgoing transition (outgoing degree 0). While… | implemented | core/services/transition_service.py (matrix: End -> no target) | tests/test_transitions/test_transition_service.py | via the RG028 matrix |
| RG027 | A block can have several incoming and several outgoing transitions. | implemented | core/services/transition_service.py | tests/test_transitions/test_transition_service.py | 0..n within the RG028 matrix limits |
| RG028 | Chaining constrained by the block-type matrix (Start→Scene/Pivot; Scene→Scene/Pivot/End; Pivot→Condition; Condition→Scene/End; End→none), cycles… | implemented | core/services/transition_service.py (ALLOWED_TARGET_TYPES) | tests/test_transitions/test_transition_service.py | matrix adopted session 03; cycles allowed; ordered-pair uniqueness |
| RG029 | A block's type is chosen at creation and immutable afterwards. | implemented | core/models/data_model.py (Block.__post_init__); usecases/view_management/update_block_usecase.py | tests/test_blocks/test_block_usecases.py | type not editable on update |
| RG030 | A Pivot block: incoming from Start/Scene only, outgoing to Condition… | implemented | core/services/transition_service.py (matrix) | tests/test_transitions/test_transition_service.py | revised session 03: Scene->Pivot promotion removed |
| RG031 | A Condition block: incoming from Pivot only, outgoing to Scene/End… | implemented | core/services/transition_service.py (matrix); core/models/data_model.py (condition) | tests/test_transitions/; tests/test_blocks/ | revised session 03: AND not expressible, OR kept |
| RG032 | There can be only one participation per (block, agent) pair. | implemented | core/services/participation_service.py (find_participation); usecases/participation_management/associate_participation_usecase.py | tests/test_agents/test_participation_usecases.py | idempotent association |
| RG033 | Deleting an agent cascades to all its participations and all its relationships,… | implemented | core/services/participation_service.py (cascade_delete_agent); usecases/agent_management/delete_agent_usecase.py | tests/test_agents/test_agent_usecases.py | counts returned for the UI information message |
| RG034 | Deleting a journey reassigns to the default journey the attachments of the… | implemented | usecases/journey_management/delete_journey_usecase.py | tests/test_journeys/test_journey_usecases.py | reassignment to the default journey (no orphan block) |
| RG035 | A relationship is binary (exactly two distinct agents — unordered pair), non-directed and typed (TSK25), and anchored… | implemented | core/services/relationship_service.py (find_relationship, check_pair, validate_type) ; usecases/relationship_management/ (create/update/delete) ; ui/dialogs/relationship_dialog.py | tests/test_relations/ | RG035 hardened session 06: uniqueness (block, pair) + two distinct agents (no self-relationship) — TSK20 (Review 19-11-2026); Block/Relationship entities kept distinct for post-MVP |

### 3. Journey logic and membership

| RG | Summary | Status | Code (file · symbol) | Unit test | Notes |
| --- | --- | --- | --- | --- | --- |
| RG037 | When a narrative map is created, a default journey is automatically created. | implemented | usecases/project_management/create_project_usecase.py | tests/test_project/test_project_service.py | parcours par défaut créé et activé |
| RG038 | Duplicating a journey does not change the active one when the journey filter is… | **removed** (TSK39 session 12, 1.9) | — | — |
| RG039 | There is always a default journey, and only one; if the default journey is… | implemented | core/services/journey_service.py; delete/set_default use cases | tests/test_journeys/test_journey_usecases.py | single default; default/active fallback on deletion |
| RG040 | No orphan block: every block belongs to at least one journey; at creation, a… | implemented | core/services/journey_service.py (attach_new_block); create/duplicate block use cases | tests/test_blocks/test_block_usecases.py | active journey if filter on, default otherwise |
| RG041 | Journey membership is derived and never stored: a transition belongs to a… | implemented | core/services/journey_filter_service.py; core/services/journey_sequence_service.py | tests/test_journeys/test_journey_filter_service.py; test_journey_sequence_service.py | derived membership (never stored) |
| RG042 | The journeys a block is attached to are edited through the journey list shown… | not-started | — | — | — |
| RG043 | Duplicating a journey copies the attachments of its blocks. | **removed** (TSK39 session 12, 1.9) | — | — |
| RG044 | A journey's reading sequence is computed depth-first from the Start block,… | implemented | core/services/journey_sequence_service.py | tests/test_journeys/test_journey_sequence_service.py | DFS from Start, branches by increasing transition id, memoized cycles, deterministic fallback |

### 4. Visualization and interaction

| RG | Summary | Status | Code (file · symbol) | Unit test | Notes |
| --- | --- | --- | --- | --- | --- |
| RG045 | Each block's position (x, y) is kept in the graphical metadata associated with… | not-started | — | — | — |
| RG046 | Blocks snap to the grid at creation and on release of a move (free position while dragging — TSK24) | implemented | core/services/layout_service.py (snap_to_grid); ui/nodes/base_node.py (itemChange: free position + scene limits, no snap while dragging ; mouseReleaseEvent: grid snap + clamp → setPos) | tests/test_journeys/test_block_drag_offscreen.py | offscreen test to validate on dev machine (no libGL in sandbox) |
| RG047 | Changing the zoom level, the scroll bar positions or the journey filter state… | not-started | — | — | — |
| RG048 | The journey filter displays either all journeys or a single one, in the narrative-map views only (not the "Agents" view);… | partial | core/services/journey_filter_service.py; ui/views/journeys_workspace.py; ui/main_window.py | tests/test_journeys/test_journey_filter_service.py | service tested (opacity from config journey_filter_opacity); visual rendering (0.25 opacity + disabled) to validate offscreen |
| RG049 | In a workspace, only one element is selected at a time; creating or clicking an… | partial | ui/views/journeys_workspace.py (_select_item_only, _clear_all_selections) | — | offscreen test to validate |
| RG050 | A block cannot be created at coordinates overlapping an existing block; its… | partial | core/services/layout_service.py (find_non_overlapping_position); ui/views/journeys_workspace.py (next_free_position) | — | offscreen test to validate |
| RG051 | When a moved block goes beyond the visible part of the workspace, scrolling… | not-started | — | — | — |
| RG052 | A transition's trace must never cross a block that is neither its source nor… | not-started | — | — | — |
| RG053 | The clickable area of a graphical element (block, transition) is defined by its… | partial | ui/nodes/base_node.py; ui/nodes/connection.py (enlarged shape()/boundingRect) | — | offscreen test to validate |
| RG054 | The notes of blocks and transitions are shown in a tooltip as soon as they are… | partial | ui/nodes/base_node.py; ui/nodes/connection.py (hoverEnterEvent -> immediate QToolTip.showText) | — | offscreen test to validate |
| RG055 | When a context menu opens, the element under the cursor is selected first; the… | partial | ui/views/journeys_workspace.py; ui/main_window.py (_show_workspace_context_menu built from the application menu's own QActions) | — | offscreen test to validate |
| RG056 | The cross-view navigation focus (including the "Relationships" view) is a temporary visual state, not persisted | implemented | ui/views/journeys_workspace.py (focus_block, selection_changed signal) ; ui/views/relationships_workspace.py ; ui/main_window.py (_view_relationship_anchor_in_journeys, _on_tab_changed) | tests/test_relations/test_relationships_workspace_offscreen.py | TSK27 ; "View in Journeys view" in the cell context menu |

### 5. Technical architecture and data model

| RG | Summary | Status | Code (file · symbol) | Unit test | Notes |
| --- | --- | --- | --- | --- | --- |
| RG057 | Agents belong to the project, not to the narrative map. | not-started | — | — | — |
| RG058 | The interface never modifies the business model directly: every change goes… | implemented | architecture: UI -> signals -> use cases/services (no model writes in ui/) | — | grep-verified (no model mutation in src/ui/) |
| RG059 | No value is hard-coded in the interface: dimensions, colors, default texts and… | not-started | — | — | — |
| RG060 | Graphical representation metadata (block positions, column order) are stored in… | partial | core/services/layout_service.py; ui/main_window.py (_do_save / _init_workspace) | — | persistence wired at save/load; layout roundtrip to validate |
| RG061 | The project is saved in a single structured file (JSON) containing metadata and… | implemented | project_service.py · save_project/load_project (JSON unique) | tests/test_project/test_project_service.py | fichier layouts séparé géré par LayoutService (RG060) |
| RG062 | The author can at any time designate one of the map's journeys as the default… | implemented | usecases/journey_management/set_default_journey_usecase.py; ui/dialogs/journey_selection_dialog.py | tests/test_journeys/test_journey_usecases.py | designation replaces the default, active unchanged |
| RG063 | Agent filter in the map views; not applied to the Agents view; off by default, not persisted,… | implemented | core/services/agent_filter_service.py; ui/views/journeys_workspace.py (_item_in_filter, apply_filters, set_agent_filter); ui/main_window.py (Display > Agent, _rebuild_agent_menu, _set_agent_filter) | tests/test_agents/test_agent_filter_service.py | visual rendering (opacity + disabled) to validate offscreen |
| RG064 | Journey filter + agent filter active at once: intersection of the two filters | implemented | ui/views/journeys_workspace.py (_item_in_filter: AND of both filters) | tests/test_agents/test_agent_filter_service.py (RG064 intersection) | — |
| RG065 | "Agents" view: same dark background as "Journeys", purely decorative dots; cards freely movable in 2D during a drag (no corridor, no snap while dragging); on release, snap to the nearest cell of an invisible grid (config agents_view_cell_*, anchored on the scene origin, nearest free cell if occupied); snap also at creation and on load; on creation, first free cell right of the bounding box of the existing cards (TSK22); on release, cell constrained to the bounding box of the other cards + 1 cell (TSK23, single card = free) | implemented | ui/views/agents_workspace.py (drawBackground: visible dots, config agents_view_dot_* ; next_free_card_position: bounding-box anchor + cell snap + free cell, default-cell fallback ; create_agent_card) ; ui/nodes/agent_card.py (itemChange: _free_pos accumulation, scene limits, no snap while dragging ; mouseReleaseEvent: _cell_snap_target → scene bounds ∩ other-cards bounding box + 1 cell, then nearest free cell → setPos) ; core/services/layout_service.py (snap_to_grid, find_nearest_free_position) ; config agents_view_cell_width/height | tests/test_agents/test_agents_workspace_offscreen.py (free diagonal drag, snap on release, occupied cell, initial placement in a row, new card next to the moved group, empty workspace, far drag pulled back into the ring TSK23, single card free) ; tests/test_agents/test_project_layout.py (snap_to_grid cell, find_nearest_free_position) | visual rendering offscreen to validate |
| RG066 | Agent card in the "Agents" view: larger than a block, no ports, label + type, single selection, note tooltip; no participation-count badge | implemented | ui/nodes/agent_card.py AgentCardItem (agents_view_card_width/height, no ports no badge, shape() RG053, single selection RG049, immediate tooltip RG054) ; ui/views/agents_workspace.py (_select_item_only) | — | visual rendering offscreen to validate |
| RG067 | Agent card positions persisted at project level in the graphics metadata (project layout file), restored on reopening; no business value | implemented | core/models/view_model.py (AgentCardLayout, ProjectLayout) ; core/services/layout_service.py (save/load_project_layout → layouts/project.json) ; ui/views/agents_workspace.py (collect_project_layout, populate_agents) ; ui/main_window.py (_do_save, _init_workspace) | tests/test_agents/test_project_layout.py | — |

| RG068 | The Start block belongs to every journey of the map, attachment not editable by the author (automatic on journey creation, list disabled in the edit dialog, never affected by RG034) | implemented | core/services/journey_service.py (set_block_attachments: RG068 guard) ; usecases/journey_management/create_journey_usecase.py (Start auto-attached + recompute RG044) ; ui/dialogs/block_dialog.py (list disabled for the Start block) | tests/test_journeys/test_journey_usecases.py (test_rg068_*) | adopted session 06; TSK26 (Done 19-11-2026) |
| RG069 | "Relationships" view: all agents displayed; cell = type of the pair's derived state at the selected block (last anchor of rank <=, minimum rank across journeys); panel list by minimum rank (ties by id), restricted to visible blocks (RG064); Start by default, fallback if outside filter; agent filter = uninvolved agents dimmed + creation forbidden | implemented | core/services/relationship_service.py (pair_state_at_block, block_min_rank, ordered_anchor_block_ids) ; ui/views/relationships_workspace.py | tests/test_relations/test_relationships_view_logic.py + test_relationships_workspace_offscreen.py | adopted session 06; TSK27; completed session 10 (TSK32: one active cell per pair, upper-triangle matrix) |
| RG070 | Row/column order of the "Relationships" matrix: alphabetical initial (label, ties by id); **single shared row/column order** (revised session 10 TSK32: upper-triangle matrix, one active cell per pair), movable by header-card drag (row and column follow together); order persisted at project level (`relationships_view_agent_order`, migration of the legacy `row_order`/`column_order` then `relationships_axis_order`) | implemented | core/models/view_model.py (ProjectLayout.relationships_view_agent_order + migration) ; core/services/relationship_service.py (resolve_axis_order) ; ui/views/relationships_workspace.py (_on_card_released, _reorder, collect_project_layout) ; ui/nodes/matrix_agent_card.py ; ui/main_window.py (_do_save) ; config `relationships_view_*` | tests/test_relations/test_relationships_workspace_offscreen.py (card drag) + test_relationships_view_logic.py (resolve_axis_order, migration) | adopted session 06, revised session 09, **revised session 10 (TSK32)**; TSK27 + TSK29 + TSK32 |

## B. Features (`03_features-*.md`)


### Hyperscript ::: Features

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

### Application

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN001 | Launch the application | partial | — | src/main.py (garde single-instance) + ui/main_window.py (écran d'accueil) | — | — (test appli T-xxx à venir) | test GUI à valider sur poste de dev |
| FN002 | Quit the application | partial | Files › Quit | ui/main_window.py · _handle_quit/closeEvent + QuitApplicationUseCase | — | tests/test_project/test_file_usecases.py (logique) | — |
| FN003 | Display the change log | partial | About › Change Log | ui/dialogs/change_log_dialog.py + core/services/change_log_service.py | — | — | menu About › Change Log câblé |
| FN004 | Display the "about" information | partial | About › About Hyperscript | ui/dialogs/about_dialog.py + core/services/about_service.py | — | — | menu About › About Hyperscript câblé |

### Project

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN005 | Create a new project | implemented | Files › New Project... | usecases/project_management/create_project_usecase.py + main_window.py · _create_project | — | tests/test_project/test_project_service.py | — |
| FN006 | Open a project | partial | Files › Open... | main_window.py · _open_project + LoadProjectUseCase | — | tests/test_project/test_file_usecases.py | boîte de dialogue fichier câblée |
| FN007 | Open a recent project | greyed-MVP | Files › Recent Projects | — | — | — | — |
| FN008 | Save the project | partial | Files › Save | main_window.py · _save_project/_do_save + SaveProjectUseCase | — | tests/test_project/test_file_usecases.py | — |
| FN009 | Save the project as... | partial | Files › Save as... | main_window.py · _save_project_as | — | tests/test_project/test_file_usecases.py | — |
| FN010 | Close the project | partial | Files › Close | main_window.py · _close_project + ProjectService.close_project | — | tests/test_project/test_file_usecases.py | — |
| FN011 | Rename the project | not-started | — | — | — | — | — |

### Narrative map

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN012 | Rename the narrative map | not-started | — | — | — | — | — |
| FN013 | Export the narrative map as a reading document | greyed-MVP | Files › Export Map... | — | — | — | — |

### Narrative blocks

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN014 | Create a narrative block | implemented | Project › Blocks › New | usecases/view_management/create_block_usecase.py; ui/main_window.py (_create_new_block) | — | — | tests/test_blocks/test_block_usecases.py |
| FN015 | Edit a block's attributes | implemented | Project › Blocks › Edit... | usecases/view_management/update_block_usecase.py; ui/dialogs/block_dialog.py | — | — | tests/test_blocks/test_block_usecases.py |
| FN016 | Duplicate a block | implemented | — | usecases/view_management/duplicate_block_usecase.py; ui/main_window.py | — | — | tests/test_blocks/test_block_usecases.py |
| FN017 | Move a block | partial | — | ui/nodes/base_node.py (mouseReleaseEvent: snap on release RG046 ; itemChange: free position); ui/main_window.py (_on_workspace_modified) | — | — | offscreen test to validate |
| FN018 | Delete a block | implemented | Project › Blocks › Delete... | usecases/view_management/delete_block_usecase.py; ui/main_window.py | — | — | tests/test_blocks/test_block_usecases.py |
| FN019 | Manage a block's journey attachments | implemented | — | usecases/view_management/update_block_usecase.py (journey_ids); ui/dialogs/block_dialog.py | — | — | tests/test_blocks/test_block_usecases.py |

### Transitions

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN020 | Create a transition | implemented | Project › Transitions › New | usecases/view_management/create_transition_usecase.py; ui/views/journeys_workspace.py (trace); ui/main_window.py | — | — | tests/test_transitions/ |
| FN021 | Annotate and edit a transition | implemented | Project › Transitions › Edit... | usecases/view_management/update_transition_usecase.py; ui/dialogs/transition_dialog.py | — | — | tests/test_transitions/test_transition_usecases.py |
| FN022 | Delete a transition | implemented | Project › Transitions › Delete... | usecases/view_management/delete_transition_usecase.py; ui/main_window.py | — | — | tests/test_transitions/test_transition_usecases.py |

### Journeys

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN023 | Create a journey | implemented | Project › Journeys › New | usecases/journey_management/create_journey_usecase.py | — | — | tests/test_journeys/test_journey_usecases.py |
| FN024 | Rename and describe a journey | implemented | — | usecases/journey_management/update_journey_usecase.py; ui/dialogs/journey_dialog.py | — | — | tests/test_journeys/test_journey_usecases.py |
| FN025 | Duplicate a journey | **removed** (TSK39 session 12, 1.9) | — | — (use case deleted) | — | — | — |
| FN026 | Activate a journey | implemented | — | usecases/journey_management/activate_journey_usecase.py; ui/main_window.py (_activate_journey, Display > Journey) | — | — | tests/test_journeys/test_journey_usecases.py |
| FN027 | Delete a journey | implemented | — | usecases/journey_management/delete_journey_usecase.py | — | — | tests/test_journeys/test_journey_usecases.py |
| FN038 | Set the default journey | not-started | Project › Journeys › Set as Default... | — | — | — | — |
| FN039 | Filter the display by agent | implemented | Display › Agent | core/services/agent_filter_service.py; ui/views/journeys_workspace.py (set_agent_filter, apply_filters); ui/main_window.py (_rebuild_agent_menu, _set_agent_filter) | — | — | tests/test_agents/test_agent_filter_service.py ; visual rendering offscreen to validate |

### Visualization

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN028 | Navigate in the workspace | partial | — | ui/views/journeys_workspace.py (20/80 grid, 4000x4000 extensible scene, 50 px auto-scroll) | — | — | offscreen test to validate |
| FN029 | Filter the display by journey | partial | — | core/services/journey_filter_service.py; ui/views/journeys_workspace.py; ui/main_window.py (dynamic Display > Journey) | — | — | tests/test_journeys/test_journey_filter_service.py (service); visual rendering offscreen to validate |

### Agents and participations

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN030 | Associate agents with a block | implemented | Add Participation (block context menu, Journeys view); Add Participation (Project > Agents) - normalized label TSK39 session 12 1.3; "Agents" list of the block edit dialog (TSK39 3.1) | usecases/participation_management/ (associate/dissociate); core/services/participation_service.py; ui/dialogs/agent_association_dialog.py; ui/main_window.py (_open_association_dialog, _show_workspace_context_menu) | — | — | tests/test_agents/test_participation_usecases.py; tests/test_tsk39/ |
| FN031 | Manage the project's agents | implemented | Project › Agents (New.../Edit.../Copy/Delete.../Add Participation) | usecases/agent_management/ (create/update/duplicate/delete); ui/dialogs/agent_dialog.py, agent_selection_dialog.py; ui/main_window.py | — | — | tests/test_agents/test_agent_usecases.py |
| FN032 | Cross-view navigation | not-started | — | — | — | — | — |
| FN033 | Reading preview ("Preview" view) | implemented | View › Preview ("Preview" tab) | core/services/preview_service.py ; ui/views/preview_workspace.py ; ui/main_window.py (tab + side panel + view_preview) ; ui/widgets/tab_bar.py ; config.json (link_color) | — | — | tests/test_preview/ (18 tests: service + offscreen) ; design docs/conception/05_preview-EN.md (TSK37), implemented TSK38 session 11 |

### Relationships between agents

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN034 | Manage a relationship between agents | implemented | Project › Relationships (New.../Edit.../Delete... wired, TSK20) | usecases/relationship_management/ ; ui/dialogs/relationship_dialog.py + relationship_selection_dialog.py | core/models/data_model.py (Relationship, canonical pair TSK25) | tests/test_relations/test_relationship_usecases.py | uniqueness (block, pair) RG035 ; dialog anchor list ordered by minimum rank across journeys (RG069) |

### Conditions

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN035 | Manage a Condition block's condition | **removed** (TSK39 session 12, 3.2: structured condition removed from the model) | — | — | — | — | — |

### "Relationships" view

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN036 | "Relationships" view: agent×agent matrix + right side panel (mockup adopted session 06, `04_interface` §6; **graphics scene like the Planoscript Agent×State matrix, reworked session 09, then session 10 TSK30**: 100×100 square cells anchored top-left (scrollbars always on, grid over the whole visible area, center dot per cell), header cards with narrative-block rendering 80×40, **session 10 TSK32 revision: upper-triangle matrix, Relationship card (border #E06666, label = type, tooltip = type+pair+anchor+note) in the active cell, right click only -> context menu (empty cell = pre-filled New..., filled cell = Edit/Delete + View in Journeys; menu also on the agent cards)**) | implemented | "Relationships" tab (tab bar) ; cell + agent-card context menus (TSK32) | ui/views/relationships_workspace.py (QGraphicsScene v4: upper triangle, single order, card in the cell + filter/block side panel) ; ui/nodes/matrix_agent_card.py + matrix_relationship_card.py ; ui/dialogs/relationship_dialog.py (pre-fill) ; ui/main_window.py (integration, filter resync, block forwarding FN032, `_show_relationships_context_menu` / `_show_relationships_agent_context_menu`) | core/services/relationship_service.py (pair_state_at_block RG069, resolve_axis_order RG070) | tests/test_relations/ | TSK27 + TSK29 + **TSK32** ; upper-triangle matrix: active cell = derived state RG069 materialized as a Relationship card, right click only (RG055) ; single shared order RG070 ; filters RG048/RG063/RG064 |

### Configuration

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN037 | Relationship type list | implemented | — | core/services/relationship_service.py (relationship_types, validate_type) | config.json `relationship_types` | tests/test_relations/test_relationship_service.py (test_fn037_*) | author enrichment post-MVP |

### Out of MVP scope / to be defined during the design phase

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

## C. General menu entries (`05_menu-*.yaml`)

| Path | Label | Shortcut | Status | `main_window.py` key |
| --- | --- | --- | --- | --- |
| Files | Files |  | not-started | — |
| Files › New Project... | New Project... | Ctrl+N | partial | menu_actions['new'] |
| Files › Open... | Open... | Ctrl+O | partial | menu_actions['open'] |
| Files › Close | Close | Ctrl+W | partial | menu_actions['close'] |
| Files › Save | Save | Ctrl+S | partial | menu_actions['save'] |
| Files › Save as... | Save as... | Ctrl+Shift+S | partial | menu_actions['save_as'] |
| Files › Export Map... | Export Map... |  | greyed-MVP | — |
| Files › Import Map... | Import Map... |  | greyed-MVP | — |
| Files › Recent Projects | Recent Projects |  | greyed-MVP | — |
| Files › Quit | Quit | Ctrl+Q | partial | menu_actions['quit'] |
| Edit | Edit |  | greyed-MVP | — |
| Edit › Undo | Undo | Ctrl+Z | greyed-MVP | — |
| Edit › Redo | Redo | Ctrl+Y | greyed-MVP | — |
| Edit › Cut | Cut | Ctrl+X | greyed-MVP | — |
| Edit › Copy | Copy | Ctrl+C | greyed-MVP | — |
| Edit › Paste | Paste | Ctrl+V | greyed-MVP | — |
| Display | Display |  | partial | — |
| Display › Journey | Journey |  | implemented | main_window._rebuild_journey_menu (dynamic, checkable, FN026/FN029) |
| Display › Agent | Agent |  | implemented | main_window._rebuild_agent_menu (dynamic, checkable, "All agents" + one per agent, FN039/RG063) |
| Display › Zoom | Zoom |  | not-started | — |
| Display › Zoom › In | In | Ctrl+= | greyed-MVP | — |
| Display › Zoom › Out | Out | Ctrl+- | greyed-MVP | — |
| Display › Zoom › Reset | Reset | Ctrl+0 | greyed-MVP | — |
| Project | Project |  | partial | — |
| Project › View | View |  | stub | menu_actions['view_*'] (stubs — views activated via the tab bar) |
| Project › View › Agents | Agents |  | stub | menu_actions['view_agents'] (order swapped session 09, TSK28: Agents before Journeys) |
| Project › View › Journeys | Journeys |  | stub | menu_actions['view_journeys'] (default active view unchanged, TSK28) |
| Project › View › Relationships | Relationships |  | stub | menu_actions['view_relationships'] |
| Project › View › Export | Export |  | stub | menu_actions['view_export'] |
| Project › Agents | Agents |  | implemented | menu_actions['agents_*'] (TSK18; AGENT_DEPENDENT for edit/copy/delete/associate) |
| Project › Agents › New... | New... |  | implemented | main_window._new_agent (dialog + use case + card added in the "Agents" view, TSK19b) |
| Project › Agents › Edit... | Edit... |  | implemented | main_window._edit_agent (optional agent = card of the context menu, TSK19b) |
| Project › Agents › Copy | Copy |  | implemented | main_window._copy_agent |
| Project › Agents › Delete... | Delete... |  | implemented | main_window._delete_agent (counted RG033 confirmation, card removed TSK19b) |
| Project › Agents › Add Participation | Add Participation |  | implemented | main_window._associate_agent_with_block → _open_association_dialog (FN030); greyed unless Journeys view active + block selected (TSK39 1.3) |
| Project › Blocks | Blocks |  | implemented | menu_actions['blocks_*'] |
| Project › Blocks › New | New |  | implemented | menu_actions['blocks_new'] |
| Project › Blocks › New › Scene | Scene |  | implemented | menu_actions['blocks_new_scene'] |
| Project › Blocks › New › Pivot | Pivot |  | implemented | menu_actions['blocks_new_pivot'] |
| Project › Blocks › New › Condition | Condition |  | implemented | menu_actions['blocks_new_condition'] |
| Project › Blocks › New › Ending | Ending |  | implemented | menu_actions['blocks_new_ending'] |
| Project › Blocks › Edit... | Edit... |  | implemented | menu_actions['blocks_edit'] (BlockDialog, FN015) |
| Project › Blocks › Copy | Copy |  | implemented | menu_actions['blocks_copy'] (FN016) |
| Project › Blocks › Delete... | Delete... |  | implemented | menu_actions['blocks_delete'] (FN018) |
| Project › Transitions | Transitions |  | implemented | menu_actions['transitions_*'] |
| Project › Transitions › New | New |  | implemented | menu_actions['transitions_new'] (FN020, trace) |
| Project › Transitions › Edit... | Edit... |  | implemented | menu_actions['transitions_edit'] (TransitionDialog, FN021) |
| Project › Transitions › Delete... | Delete... |  | implemented | menu_actions['transitions_delete'] (FN022) |
| Project › Journeys | Journeys |  | implemented | menu_actions['journeys_*'] |
| Project › Journeys › New | New |  | implemented | menu_actions['journeys_new'] (FN023) |
| Project › Journeys › Edit... | Edit... |  | implemented | menu_actions['journeys_edit'] (JourneyDialog, FN024) |
| Project › Journeys › Copy | Copy |  | **removed** (TSK39 session 12, 1.9) | — |
| Project › Journeys › Set as Default... | Set as Default... |  | implemented | menu_actions['journeys_set_default'] (FN038) |
| Project › Journeys › Delete... | Delete... |  | implemented | menu_actions['journeys_delete'] (FN027) |
| Project › Relationships | Relationships |  | implemented | menu_actions['relationships_*'] (TSK20 ; the "Relationships" view remains TSK27) |
| Project › Relationships › New... | New... |  | implemented | menu_actions['relationships_new'] (FN034, ≥ 2 agents) |
| Project › Relationships › Edit... | Edit... |  | implemented | menu_actions['relationships_edit'] (FN034, ≥ 1 relationship) |
| Project › Relationships › Delete... | Delete... |  | implemented | menu_actions['relationships_delete'] (FN034, confirmation) |
| About | About |  | not-started | — |
| About › Change Log | Change Log |  | partial | menu_actions['change_log'] |
| About › About Hyperscript | About Hyperscript |  | partial | menu_actions['about'] |

## D. User stories (`01_user_stories-*.md`)

| SU | Title | Covered FNs | Aggregated status |
| --- | --- | --- | --- |
| SU001 | Manage a Narrative Project | FN001, FN002, FN005, FN006, FN007, FN008, FN009, FN010, FN011 | not-started |
| SU002 | Manage a Narrative Map | FN012, FN013 | not-started |
| SU003 | Manage a Narrative Block | FN014, FN015, FN016, FN017, FN018, FN019 | partial |
| SU004 | Manage a Transition Between Blocks | FN020, FN021, FN022 | implemented |
| SU005 | Manage a Journey | FN019, FN023, FN024, FN026, FN027, FN038 | implemented |
| SU006 | Visualize the Narrative Map (view "Journeys") | FN017, FN028, FN029 | partial |
| SU007 | Export the Narrative Map | FN013, FN033 | not-started |
| SU008 | Manage agent-block Participations | FN030, FN031 | implemented |
| SU009 | Manage the agents view — re-designed session 04 (anchor dots + agent cards, TSK19b) | FN031, FN032 | implemented |
| SU010 | View the reading preview ("Preview" view) | FN033 | implemented |
| SU011 | Manage a Relationship Between Agents | FN034, FN037 | implemented |
| SU012 | Manage the "Relationships" view — mockup adopted session 06 (matrix + side panel, `04_interface` §6) | FN032, FN036 | implemented |
