# Hyperscript ::: Implementation traceability matrix


- **Last modification date**: 10-11-2026
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
| RG023 | Deleting a block cascades to its transitions, participations, anchored… | not-started | — | — | — |
| RG024 | Deleting the last journey of a map is impossible. | not-started | — | — | — |
| RG025 | Each narrative map has one and only one Start block, created automatically when… | implemented | usecases/project_management/create_project_usecase.py | tests/test_project/test_project_service.py | bloc Start unique, auto-créé |
| RG026 | An End block cannot receive any outgoing transition (outgoing degree 0). While… | not-started | — | — | — |
| RG027 | A block can have several incoming and several outgoing transitions. | not-started | — | — | — |
| RG028 | Chaining through transitions is free (from any block to any block, cycles… | not-started | — | — | — |
| RG029 | A block's type is chosen at creation and immutable afterwards. | not-started | — | — | — |
| RG030 | A Pivot block has at least two outgoing transitions; the Scene → Pivot… | not-started | — | — | Rule subject to revision during the design phase if the need arises. |
| RG031 | A Condition block has exactly one incoming transition (from a Pivot) and one… | not-started | — | — | Rule subject to revision during the design phase if the need arises. |
| RG032 | There can be only one participation per (block, agent) pair. | not-started | — | — | — |
| RG033 | Deleting an agent cascades to all its participations and all its relationships,… | not-started | — | — | — |
| RG034 | Deleting a journey reassigns to the default journey the attachments of the… | not-started | — | — | — |
| RG035 | A relationship is binary (exactly two agents), directed and typed, and anchored… | not-started | — | — | — |
| RG036 | In the "Agents" view, the columns (blocks) are ordered by default by creation… | not-started | — | — | To be re-designed with the "Agents" view. |

### 3. Journey logic and membership

| RG | Summary | Status | Code (file · symbol) | Unit test | Notes |
| --- | --- | --- | --- | --- | --- |
| RG037 | When a narrative map is created, a default journey is automatically created. | implemented | usecases/project_management/create_project_usecase.py | tests/test_project/test_project_service.py | parcours par défaut créé et activé |
| RG038 | Duplicating a journey does not change the active one when the journey filter is… | not-started | — | — | — |
| RG039 | There is always a default journey, and only one; if the default journey is… | not-started | — | — | — |
| RG040 | No orphan block: every block belongs to at least one journey; at creation, a… | implemented | usecases/project_management/create_project_usecase.py (journey_node sur le bloc Start) | tests/test_project/test_project_service.py | rattachement actif si filtre activé, défaut sinon |
| RG041 | Journey membership is derived and never stored: a transition belongs to a… | not-started | — | — | — |
| RG042 | The journeys a block is attached to are edited through the journey list shown… | not-started | — | — | — |
| RG043 | Duplicating a journey copies the attachments of its blocks. | not-started | — | — | — |
| RG044 | A journey's reading sequence is computed depth-first from the Start block,… | not-started | — | — | — |

### 4. Visualization and interaction

| RG | Summary | Status | Code (file · symbol) | Unit test | Notes |
| --- | --- | --- | --- | --- | --- |
| RG045 | Each block's position (x, y) is kept in the graphical metadata associated with… | not-started | — | — | — |
| RG046 | Blocks automatically snap to the grid at creation and when moved. | not-started | — | — | — |
| RG047 | Changing the zoom level, the scroll bar positions or the journey filter state… | not-started | — | — | — |
| RG048 | The journey filter displays either all journeys or a single one, in all views;… | not-started | — | — | — |
| RG049 | In a workspace, only one element is selected at a time; creating or clicking an… | not-started | — | — | — |
| RG050 | A block cannot be created at coordinates overlapping an existing block; its… | not-started | — | — | — |
| RG051 | When a moved block goes beyond the visible part of the workspace, scrolling… | not-started | — | — | — |
| RG052 | A transition's trace must never cross a block that is neither its source nor… | not-started | — | — | — |
| RG053 | The clickable area of a graphical element (block, transition) is defined by its… | not-started | — | — | — |
| RG054 | The notes of blocks and transitions are shown in a tooltip as soon as they are… | not-started | — | — | — |
| RG055 | When a context menu opens, the element under the cursor is selected first; the… | not-started | — | — | — |
| RG056 | The cross-view navigation focus (including the "Relationships" view) is a… | not-started | — | — | — |

### 5. Technical architecture and data model

| RG | Summary | Status | Code (file · symbol) | Unit test | Notes |
| --- | --- | --- | --- | --- | --- |
| RG057 | Agents belong to the project, not to the narrative map. | not-started | — | — | — |
| RG058 | The interface never modifies the business model directly: every change goes… | not-started | — | — | — |
| RG059 | No value is hard-coded in the interface: dimensions, colors, default texts and… | not-started | — | — | — |
| RG060 | Graphical representation metadata (block positions, column order) are stored in… | not-started | — | — | — |
| RG061 | The project is saved in a single structured file (JSON) containing metadata and… | implemented | project_service.py · save_project/load_project (JSON unique) | tests/test_project/test_project_service.py | fichier layouts séparé géré par LayoutService (RG060) |
| RG062 | The author can at any time designate one of the map's journeys as the default… | not-started | — | — | — |

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
| FN014 | Create a narrative block | not-started | Project › Narrative Blocks › New | — | — | — | — |
| FN015 | Edit a block's attributes | not-started | Project › Narrative Blocks › Edit... | — | — | — | — |
| FN016 | Duplicate a block | not-started | — | — | — | — | — |
| FN017 | Move a block | not-started | — | — | — | — | — |
| FN018 | Delete a block | not-started | Project › Narrative Blocks › Delete... | — | — | — | — |
| FN019 | Manage a block's journey attachments | not-started | — | — | — | — | — |

### Transitions

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN020 | Create a transition | not-started | Project › Transitions › New | — | — | — | — |
| FN021 | Annotate and edit a transition | not-started | Project › Transitions › Edit... | — | — | — | — |
| FN022 | Delete a transition | not-started | Project › Transitions › Delete... | — | — | — | — |

### Journeys

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN023 | Create a journey | not-started | Project › Journeys › New | — | — | — | — |
| FN024 | Rename and describe a journey | not-started | — | — | — | — | — |
| FN025 | Duplicate a journey | not-started | — | — | — | — | — |
| FN026 | Activate a journey | not-started | — | — | — | — | — |
| FN027 | Delete a journey | not-started | — | — | — | — | — |
| FN038 | Set the default journey | not-started | Project › Journeys › Set as Default... | — | — | — | — |

### Visualization

| FN | Title | Status | UI entry point (menu) | Use case / service | Model | App test (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN028 | Navigate in the workspace | not-started | — | — | — | — | — |
| FN029 | Filter the display by journey | not-started | — | — | — | — | — |

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
| FN035 | Manage a Condition block's condition and the Scene → Pivot promotion | not-started | — | — | — | — | — |

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
| Display | Display |  | not-started | — |
| Display › Journey | Journey |  | not-started | — |
| Display › Zoom | Zoom |  | not-started | — |
| Display › Zoom › In | In | Ctrl+= | greyed-MVP | — |
| Display › Zoom › Out | Out | Ctrl+- | greyed-MVP | — |
| Display › Zoom › Reset | Reset | Ctrl+0 | greyed-MVP | — |
| Project | Project |  | not-started | — |
| Project › View | View |  | not-started | — |
| Project › View › Journeys | Journeys |  | not-started | — |
| Project › View › Agents | Agents |  | not-started | — |
| Project › View › Relationships | Relationships |  | not-started | — |
| Project › View › Export | Export |  | not-started | — |
| Project › Agents | Agents |  | not-started | — |
| Project › Agents › New... | New... |  | not-started | — |
| Project › Agents › Edit... | Edit... |  | not-started | — |
| Project › Agents › Copy | Copy |  | not-started | — |
| Project › Agents › Delete... | Delete... |  | not-started | — |
| Project › Agents › Associate with Block... | Associate with Block... |  | not-started | — |
| Project › Narrative Blocks | Narrative Blocks |  | not-started | — |
| Project › Narrative Blocks › New | New |  | not-started | — |
| Project › Narrative Blocks › New › Scene | Scene |  | not-started | — |
| Project › Narrative Blocks › New › Pivot | Pivot |  | not-started | — |
| Project › Narrative Blocks › New › Condition | Condition |  | not-started | — |
| Project › Narrative Blocks › New › Ending | Ending |  | not-started | — |
| Project › Narrative Blocks › Edit... | Edit... |  | not-started | — |
| Project › Narrative Blocks › Copy | Copy |  | not-started | — |
| Project › Narrative Blocks › Delete... | Delete... |  | not-started | — |
| Project › Transitions | Transitions |  | not-started | — |
| Project › Transitions › New | New |  | not-started | — |
| Project › Transitions › Edit... | Edit... |  | not-started | — |
| Project › Transitions › Delete... | Delete... |  | not-started | — |
| Project › Journeys | Journeys |  | not-started | — |
| Project › Journeys › New | New |  | not-started | — |
| Project › Journeys › Edit... | Edit... |  | not-started | — |
| Project › Journeys › Copy | Copy |  | not-started | — |
| Project › Journeys › Set as Default... | Set as Default... |  | not-started | — |
| Project › Journeys › Delete... | Delete... |  | not-started | — |
| Project › Relationships | Relationships |  | not-started | — |
| Project › Relationships › New... | New... |  | not-started | — |
| Project › Relationships › Edit... | Edit... |  | not-started | — |
| Project › Relationships › Delete... | Delete... |  | not-started | — |
| About | About |  | not-started | — |
| About › Change Log | Change Log |  | partial | menu_actions['change_log'] |
| About › About Hyperscript | About Hyperscript |  | partial | menu_actions['about'] |

## D. User stories (`01_user_stories-*.md`)

| SU | Title | Covered FNs | Aggregated status |
| --- | --- | --- | --- |
| SU001 | Manage a Narrative Project | FN001, FN002, FN005, FN006, FN007, FN008, FN009, FN010, FN011 | not-started |
| SU002 | Manage a Narrative Map | FN012, FN013 | not-started |
| SU003 | Manage a Narrative Block | FN014, FN015, FN016, FN017, FN018, FN019, FN035 | not-started |
| SU004 | Manage a Transition Between Blocks | FN020, FN021, FN022, FN035 | not-started |
| SU005 | Manage a Journey | FN019, FN023, FN024, FN025, FN026, FN027, FN038 | not-started |
| SU006 | Visualize the Narrative Map (view "Journeys") | FN017, FN028, FN029 | not-started |
| SU007 | Export the Narrative Map | FN013, FN033 | not-started |
| SU008 | Manage agent-block Participations | FN030, FN031 | not-started |
| SU009 | Manage the agents view — initialized, to be finalized after the design phase | FN031, FN032 | not-started |
| SU010 | Preview the export — initialized, to be finalized after the design phase | FN033 | not-started |
| SU011 | Manage a Relationship Between Agents | FN034, FN037 | not-started |
| SU012 | Manage the "Relationships" view — initialized, to be finalized after the design phase | FN032, FN036 | not-started |
