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
| RG032 | There can be only one participation per (block, agent) pair. | not-started | — | — | — |
| RG033 | Deleting an agent cascades to all its participations and all its relationships,… | not-started | — | — | — |
| RG034 | Deleting a journey reassigns to the default journey the attachments of the… | implemented | usecases/journey_management/delete_journey_usecase.py | tests/test_journeys/test_journey_usecases.py | reassignment to the default journey (no orphan block) |
| RG035 | A relationship is binary (exactly two agents), directed and typed, and anchored… | not-started | — | — | — |
| RG036 | In the "Agents" view, the columns (blocks) are ordered by default by creation… | not-started | — | — | To be re-designed with the "Agents" view. |

### 3. Journey logic and membership

| RG | Summary | Status | Code (file · symbol) | Unit test | Notes |
| --- | --- | --- | --- | --- | --- |
| RG037 | When a narrative map is created, a default journey is automatically created. | implemented | usecases/project_management/create_project_usecase.py | tests/test_project/test_project_service.py | parcours par défaut créé et activé |
| RG038 | Duplicating a journey does not change the active one when the journey filter is… | implemented | usecases/journey_management/duplicate_journey_usecase.py | tests/test_journeys/test_journey_usecases.py | copy not activated |
| RG039 | There is always a default journey, and only one; if the default journey is… | implemented | core/services/journey_service.py; delete/set_default use cases | tests/test_journeys/test_journey_usecases.py | single default; default/active fallback on deletion |
| RG040 | No orphan block: every block belongs to at least one journey; at creation, a… | implemented | core/services/journey_service.py (attach_new_block); create/duplicate block use cases | tests/test_blocks/test_block_usecases.py | active journey if filter on, default otherwise |
| RG041 | Journey membership is derived and never stored: a transition belongs to a… | implemented | core/services/journey_filter_service.py; core/services/journey_sequence_service.py | tests/test_journeys/test_journey_filter_service.py; test_journey_sequence_service.py | derived membership (never stored) |
| RG042 | The journeys a block is attached to are edited through the journey list shown… | not-started | — | — | — |
| RG043 | Duplicating a journey copies the attachments of its blocks. | implemented | usecases/journey_management/duplicate_journey_usecase.py | tests/test_journeys/test_journey_usecases.py | block attachments copied |
| RG044 | A journey's reading sequence is computed depth-first from the Start block,… | implemented | core/services/journey_sequence_service.py | tests/test_journeys/test_journey_sequence_service.py | DFS from Start, branches by increasing transition id, memoized cycles, deterministic fallback |

### 4. Visualization and interaction

| RG | Summary | Status | Code (file · symbol) | Unit test | Notes |
| --- | --- | --- | --- | --- | --- |
| RG045 | Each block's position (x, y) is kept in the graphical metadata associated with… | not-started | — | — | — |
| RG046 | Blocks automatically snap to the grid at creation and when moved. | partial | core/services/layout_service.py (snap_to_grid); ui/nodes/base_node.py (itemChange) | — | offscreen test to validate on dev machine (no libGL in sandbox) |
| RG047 | Changing the zoom level, the scroll bar positions or the journey filter state… | not-started | — | — | — |
| RG048 | The journey filter displays either all journeys or a single one, in all views;… | partial | core/services/journey_filter_service.py; ui/views/journeys_workspace.py; ui/main_window.py | tests/test_journeys/test_journey_filter_service.py | service tested (opacity from config journey_filter_opacity); visual rendering (0.25 opacity + disabled) to validate offscreen |
| RG049 | In a workspace, only one element is selected at a time; creating or clicking an… | partial | ui/views/journeys_workspace.py (_select_item_only, _clear_all_selections) | — | offscreen test to validate |
| RG050 | A block cannot be created at coordinates overlapping an existing block; its… | partial | core/services/layout_service.py (find_non_overlapping_position); ui/views/journeys_workspace.py (next_free_position) | — | offscreen test to validate |
| RG051 | When a moved block goes beyond the visible part of the workspace, scrolling… | not-started | — | — | — |
| RG052 | A transition's trace must never cross a block that is neither its source nor… | not-started | — | — | — |
| RG053 | The clickable area of a graphical element (block, transition) is defined by its… | partial | ui/nodes/base_node.py; ui/nodes/connection.py (enlarged shape()/boundingRect) | — | offscreen test to validate |
| RG054 | The notes of blocks and transitions are shown in a tooltip as soon as they are… | partial | ui/nodes/base_node.py; ui/nodes/connection.py (hoverEnterEvent -> immediate QToolTip.showText) | — | offscreen test to validate |
| RG055 | When a context menu opens, the element under the cursor is selected first; the… | partial | ui/views/journeys_workspace.py; ui/main_window.py (_show_workspace_context_menu built from the application menu's own QActions) | — | offscreen test to validate |
| RG056 | The cross-view navigation focus (including the "Relationships" view) is a… | not-started | — | — | — |

### 5. Technical architecture and data model

| RG | Summary | Status | Code (file · symbol) | Unit test | Notes |
| --- | --- | --- | --- | --- | --- |
| RG057 | Agents belong to the project, not to the narrative map. | not-started | — | — | — |
| RG058 | The interface never modifies the business model directly: every change goes… | implemented | architecture: UI -> signals -> use cases/services (no model writes in ui/) | — | grep-verified (no model mutation in src/ui/) |
| RG059 | No value is hard-coded in the interface: dimensions, colors, default texts and… | not-started | — | — | — |
| RG060 | Graphical representation metadata (block positions, column order) are stored in… | partial | core/services/layout_service.py; ui/main_window.py (_do_save / _init_workspace) | — | persistence wired at save/load; layout roundtrip to validate |
| RG061 | The project is saved in a single structured file (JSON) containing metadata and… | implemented | project_service.py · save_project/load_project (JSON unique) | tests/test_project/test_project_service.py | fichier layouts séparé géré par LayoutService (RG060) |
| RG062 | The author can at any time designate one of the map's journeys as the default… | implemented | usecases/journey_management/set_default_journey_usecase.py; ui/dialogs/journey_selection_dialog.py | tests/test_journeys/test_journey_usecases.py | designation replaces the default, active unchanged |

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
| FN014 | Create a narrative block | implemented | Project › Narrative Blocks › New | usecases/view_management/create_block_usecase.py; ui/main_window.py (_create_new_block) | — | — | tests/test_blocks/test_block_usecases.py |
| FN015 | Edit a block's attributes | implemented | Project › Narrative Blocks › Edit... | usecases/view_management/update_block_usecase.py; ui/dialogs/block_dialog.py | — | — | tests/test_blocks/test_block_usecases.py |
| FN016 | Duplicate a block | implemented | — | usecases/view_management/duplicate_block_usecase.py; ui/main_window.py | — | — | tests/test_blocks/test_block_usecases.py |
| FN017 | Move a block | partial | — | ui/nodes/base_node.py (itemChange, snap RG046); ui/main_window.py (_on_workspace_modified) | — | — | offscreen test to validate |
| FN018 | Delete a block | implemented | Project › Narrative Blocks › Delete... | usecases/view_management/delete_block_usecase.py; ui/main_window.py | — | — | tests/test_blocks/test_block_usecases.py |
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
| FN025 | Duplicate a journey | implemented | — | usecases/journey_management/duplicate_journey_usecase.py | — | — | tests/test_journeys/test_journey_usecases.py |
| FN026 | Activate a journey | implemented | — | usecases/journey_management/activate_journey_usecase.py; ui/main_window.py (_activate_journey, Display > Journey) | — | — | tests/test_journeys/test_journey_usecases.py |
| FN027 | Delete a journey | implemented | — | usecases/journey_management/delete_journey_usecase.py | — | — | tests/test_journeys/test_journey_usecases.py |
| FN038 | Set the default journey | not-started | Project › Journeys › Set as Default... | — | — | — | — |

### Visualization

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN028 | Navigate in the workspace | partial | — | ui/views/journeys_workspace.py (20/80 grid, 4000x4000 extensible scene, 50 px auto-scroll) | — | — | offscreen test to validate |
| FN029 | Filter the display by journey | partial | — | core/services/journey_filter_service.py; ui/views/journeys_workspace.py; ui/main_window.py (dynamic Display > Journey) | — | — | tests/test_journeys/test_journey_filter_service.py (service); visual rendering offscreen to validate |

### Agents and participations

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN030 | Associate agents with a block | not-started | Associate agents... | — | — | — | — |
| FN031 | Manage the project's agents | not-started | Project › Agents | — | — | — | — |
| FN032 | Cross-view navigation | not-started | — | — | — | — | — |
| FN033 | Export preview (workspace "Export") | not-started | — | — | — | — | — |

### Relationships between agents

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN034 | Manage a relationship between agents | not-started | Project › Relationships | — | — | — | — |

### Conditions

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN035 | Manage a Condition block's condition | implemented | — | usecases/view_management/update_block_usecase.py (condition); ui/dialogs/block_dialog.py | — | — | tests/test_blocks/test_block_usecases.py |

### "Relationships" view

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN036 | "Relationships" view | not-started | — | — | — | — | — |

### Configuration

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN037 | Relationship type list | not-started | — | — | — | — | — |

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
| Display › Zoom | Zoom |  | not-started | — |
| Display › Zoom › In | In | Ctrl+= | greyed-MVP | — |
| Display › Zoom › Out | Out | Ctrl+- | greyed-MVP | — |
| Display › Zoom › Reset | Reset | Ctrl+0 | greyed-MVP | — |
| Project | Project |  | partial | — |
| Project › View | View |  | stub | menu_actions['view_*'] (stubs — views activated via the tab bar) |
| Project › View › Journeys | Journeys |  | stub | menu_actions['view_journeys'] |
| Project › View › Agents | Agents |  | stub | menu_actions['view_agents'] |
| Project › View › Relationships | Relationships |  | stub | menu_actions['view_relationships'] |
| Project › View › Export | Export |  | stub | menu_actions['view_export'] |
| Project › Agents | Agents |  | stub | menu_actions['agents_*'] (stubs — Agents view out of MVP) |
| Project › Agents › New... | New... |  | stub | menu_actions['agents_new'] |
| Project › Agents › Edit... | Edit... |  | stub | menu_actions['agents_edit'] |
| Project › Agents › Copy | Copy |  | stub | menu_actions['agents_copy'] |
| Project › Agents › Delete... | Delete... |  | stub | menu_actions['agents_delete'] |
| Project › Agents › Associate with Block... | Associate with Block... |  | stub | menu_actions['agents_associate'] |
| Project › Narrative Blocks | Narrative Blocks |  | implemented | menu_actions['blocks_*'] |
| Project › Narrative Blocks › New | New |  | implemented | menu_actions['blocks_new'] |
| Project › Narrative Blocks › New › Scene | Scene |  | implemented | menu_actions['blocks_new_scene'] |
| Project › Narrative Blocks › New › Pivot | Pivot |  | implemented | menu_actions['blocks_new_pivot'] |
| Project › Narrative Blocks › New › Condition | Condition |  | implemented | menu_actions['blocks_new_condition'] |
| Project › Narrative Blocks › New › Ending | Ending |  | implemented | menu_actions['blocks_new_ending'] |
| Project › Narrative Blocks › Edit... | Edit... |  | implemented | menu_actions['blocks_edit'] (BlockDialog, FN015) |
| Project › Narrative Blocks › Copy | Copy |  | implemented | menu_actions['blocks_copy'] (FN016) |
| Project › Narrative Blocks › Delete... | Delete... |  | implemented | menu_actions['blocks_delete'] (FN018) |
| Project › Transitions | Transitions |  | implemented | menu_actions['transitions_*'] |
| Project › Transitions › New | New |  | implemented | menu_actions['transitions_new'] (FN020, trace) |
| Project › Transitions › Edit... | Edit... |  | implemented | menu_actions['transitions_edit'] (TransitionDialog, FN021) |
| Project › Transitions › Delete... | Delete... |  | implemented | menu_actions['transitions_delete'] (FN022) |
| Project › Journeys | Journeys |  | implemented | menu_actions['journeys_*'] |
| Project › Journeys › New | New |  | implemented | menu_actions['journeys_new'] (FN023) |
| Project › Journeys › Edit... | Edit... |  | implemented | menu_actions['journeys_edit'] (JourneyDialog, FN024) |
| Project › Journeys › Copy | Copy |  | implemented | menu_actions['journeys_copy'] (FN025) |
| Project › Journeys › Set as Default... | Set as Default... |  | implemented | menu_actions['journeys_set_default'] (FN038) |
| Project › Journeys › Delete... | Delete... |  | implemented | menu_actions['journeys_delete'] (FN027) |
| Project › Relationships | Relationships |  | stub | menu_actions['relationships_*'] (stubs — Relationships view out of MVP) |
| Project › Relationships › New... | New... |  | stub | menu_actions['relationships_new'] |
| Project › Relationships › Edit... | Edit... |  | stub | menu_actions['relationships_edit'] |
| Project › Relationships › Delete... | Delete... |  | stub | menu_actions['relationships_delete'] |
| About | About |  | not-started | — |
| About › Change Log | Change Log |  | partial | menu_actions['change_log'] |
| About › About Hyperscript | About Hyperscript |  | partial | menu_actions['about'] |

## D. User stories (`01_user_stories-*.md`)

| SU | Title | Covered FNs | Aggregated status |
| --- | --- | --- | --- |
| SU001 | Manage a Narrative Project | FN001, FN002, FN005, FN006, FN007, FN008, FN009, FN010, FN011 | not-started |
| SU002 | Manage a Narrative Map | FN012, FN013 | not-started |
| SU003 | Manage a Narrative Block | FN014, FN015, FN016, FN017, FN018, FN019, FN035 | partial |
| SU004 | Manage a Transition Between Blocks | FN020, FN021, FN022, FN035 | implemented |
| SU005 | Manage a Journey | FN019, FN023, FN024, FN025, FN026, FN027, FN038 | implemented |
| SU006 | Visualize the Narrative Map (view "Journeys") | FN017, FN028, FN029 | partial |
| SU007 | Export the Narrative Map | FN013, FN033 | not-started |
| SU008 | Manage agent-block Participations | FN030, FN031 | not-started |
| SU009 | Manage the agents view — initialized, to be finalized after the design phase | FN031, FN032 | not-started |
| SU010 | Preview the export — initialized, to be finalized after the design phase | FN033 | not-started |
| SU011 | Manage a Relationship Between Agents | FN034, FN037 | not-started |
| SU012 | Manage the "Relationships" view — initialized, to be finalized after the design phase | FN032, FN036 | not-started |
