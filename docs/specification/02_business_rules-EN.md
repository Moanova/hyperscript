# Business Rules - Hyperscript

## Document Version
- **Version**: 1.0
- **Date**: 2026-11-09
- **Status**: initial.


---

## 1. Project management and lifecycle

## RG001
- **Description** : A project is a local document (JSON format) containing its metadata, its agents and its narrative maps. The model supports several maps per project; the MVP contains a single one.
- **Classification** : 1. Project management and lifecycle

## RG002
- **Description** : Only one project can be open in the application at any time.
- **Classification** : 1. Project management and lifecycle

## RG003
- **Description** : A newly created project is an unsaved project: it exists in memory but is not associated with any file until the user saves it.
- **Classification** : 1. Project management and lifecycle

## RG004
- **Description** : Each project has a stable identifier, a name, a creation date, a last modification date and a format version.
- **Classification** : 1. Project management and lifecycle

## RG005
- **Description** : Projects saved or opened successfully are added to the recent projects list, ordered from most to least recently opened, with a single occurrence per file and a configured limit; entries whose file is missing, inaccessible or invalid are removed. [Post-MVP: the corresponding menu entry is greyed out in the MVP.]
- **Classification** : 1. Project management and lifecycle

## RG006
- **Description** : The "Save" command is enabled only when the open project is modified; "Save as..." is enabled as soon as a project is open; when no project is open, both are disabled.
- **Classification** : 1. Project management and lifecycle

## RG007
- **Description** : When no project is open, the entries of the Files (Close, Save, Save as...), Edit, Display and Project menus are greyed out. In the MVP, "Export Map", "Import Map", "Recent Projects...", the whole Edit menu and the Zoom submenu remain greyed out even with a project open.
- **Classification** : 1. Project management and lifecycle

## RG008
- **Description** : When a project is opened or created, the entries of the Files (Close, Save, Save as...), Display and Project menus are enabled (except the entries greyed out in the MVP, RG007).
- **Classification** : 1. Project management and lifecycle

## RG009
- **Description** : Opening a project replaces the current project only after the selected file has been read and validated successfully; otherwise an error is displayed and the current project remains unchanged. No planoscript project is migrated: such a file is treated as incompatible.
- **Classification** : 1. Project management and lifecycle

## RG010
- **Description** : The application opens a project only if its format version is supported; it migrates no file from another application and never overwrites an original file without an explicit action by the user.
- **Classification** : 1. Project management and lifecycle

## RG011
- **Description** : Saving replaces the existing file only after the new version has been fully and successfully written; on failure, the previously saved file remains usable and the project keeps its modified state; after a successful save, the project's last modification date is updated.
- **Classification** : 1. Project management and lifecycle

## RG012
- **Description** : "Save as..." creates or replaces a file at the chosen location (with confirmation if the file already exists); after a successful save, that file becomes the file associated with the open project, and the previous file is neither renamed nor deleted.
- **Classification** : 1. Project management and lifecycle

## RG013
- **Description** : A new project is named "New project" and contains a narrative map named "Main narrative map", created with a Start block (created automatically) and a default journey (created and activated).
- **Classification** : 1. Project management and lifecycle

## RG014
- **Description** : A project always contains at least one narrative map (in the MVP: exactly one).
- **Classification** : 1. Project management and lifecycle

## RG015
- **Description** : Only one instance of the application can run at a time; if an instance is already running, a new launch exits silently.
- **Classification** : 1. Project management and lifecycle

## RG016
- **Description** : No existing planoscript project is migrated: planoscript files are considered incompatible (RG009).
- **Classification** : 1. Project management and lifecycle

## RG017
- **Description** : File export is out of the MVP scope (only the in-app preview, "Export" view, is available in the MVP). When available, the reading export generates a standalone folder named after the map (index file + linked pages), in the journey's sequence order independently of the graphical positions, and marks neither the map nor the project as modified; the technical export remains to be defined during the design phase.
- **Classification** : 1. Project management and lifecycle

## 2. Narrative map structure

## RG018
- **Description** : Each narrative map has a stable identifier.
- **Classification** : 2. Narrative map structure

## RG019
- **Description** : Each block, transition, participation, relationship, journey and block-to-journey attachment has an integer identifier unique within its narrative map.
- **Classification** : 2. Narrative map structure

## RG020
- **Description** : The labels of blocks, transitions, participations, relationships, journeys and agents are not subject to uniqueness.
- **Classification** : 2. Narrative map structure

## RG021
- **Description** : A narrative map always contains at least one journey.
- **Classification** : 2. Narrative map structure

## RG022
- **Description** : Deleting a narrative map is irreversible and deletes all its content (blocks, transitions, participations, relationships, journeys, attachments). [Post-MVP: a single map per project.]
- **Classification** : 2. Narrative map structure

## RG023
- **Description** : Deleting a block cascades to its transitions, participations, anchored relationships and journey attachments; an information message is displayed if the block was referenced by other elements.
- **Classification** : 2. Narrative map structure

## RG024
- **Description** : Deleting the last journey of a map is impossible.
- **Classification** : 2. Narrative map structure

## RG025
- **Description** : Each narrative map has one and only one Start block, created automatically when the map is created, never deletable nor duplicable; the "Start" type is offered nowhere else (creation or edition of another block).
- **Classification** : 2. Narrative map structure

## RG026
- **Description** : An End block cannot receive any outgoing transition (outgoing degree 0). While editing, a journey may temporarily have no End block (consistency check is out of the MVP).
- **Classification** : 2. Narrative map structure

## RG027
- **Description** : A block can have several incoming and several outgoing transitions.
- **Classification** : 2. Narrative map structure

## RG028
- **Description** : Chaining through transitions is free (from any block to any block, cycles allowed — e.g. Scene → Pivot → Condition → the same Scene); there can be only one transition per ordered pair of blocks.
- **Classification** : 2. Narrative map structure

## RG029
- **Description** : A block's type is chosen at creation and immutable afterwards.
- **Classification** : 2. Narrative map structure

## RG030
- **Description** : A Pivot block has at least two outgoing transitions; the Scene → Pivot promotion is automatic and one-way when a second outgoing transition is created (never the other way round). *Rule subject to revision during the design phase if the need arises.*
- **Classification** : 2. Narrative map structure

## RG031
- **Description** : A Condition block has exactly one incoming transition (from a Pivot) and one outgoing transition (to the guarded scene); it carries a structured condition (kind: choice / artefact / skill / flag; optional reference to an Artefact agent; label); chaining Condition blocks equals an AND, two Condition blocks from the same Pivot equal an OR. *Rule subject to revision during the design phase if the need arises.*
- **Classification** : 2. Narrative map structure

## RG032
- **Description** : There can be only one participation per (block, agent) pair.
- **Classification** : 2. Narrative map structure

## RG033
- **Description** : Deleting an agent cascades to all its participations and all its relationships, with an information message if the agent was referenced.
- **Classification** : 2. Narrative map structure

## RG034
- **Description** : Deleting a journey reassigns to the default journey the attachments of the blocks that belonged only to it (no orphan block).
- **Classification** : 2. Narrative map structure

## RG035
- **Description** : A relationship is binary (exactly two agents), directed and typed, and anchored to exactly one block; its type is read from the configuration file value list; there can be only one relationship per (block, agent pair, type).
- **Classification** : 2. Narrative map structure

## RG036
- **Description** : In the "Agents" view, the columns (blocks) are ordered by default by creation order, with persistent manual reordering between sessions; the Start block always occupies the first column. *To be re-designed with the "Agents" view.*
- **Classification** : 2. Narrative map structure

## 3. Journey logic and membership

## RG037
- **Description** : When a narrative map is created, a default journey is automatically created.
- **Classification** : 3. Journey logic and membership

## RG038
- **Description** : Duplicating a journey does not change the active one when the journey filter is activated.
- **Classification** : 3. Journey logic and membership

## RG039
- **Description** : There is always a default journey, and only one; if the default journey is deleted, the oldest remaining journey becomes the default; if the active journey is deleted, the default journey becomes the active one.
- **Classification** : 3. Journey logic and membership

## RG040
- **Description** : No orphan block: every block belongs to at least one journey; at creation, a block is attached to the default journey; a block cannot be removed from its last journey.
- **Classification** : 3. Journey logic and membership

## RG041
- **Description** : Journey membership is derived and never stored: a transition belongs to a journey if and only if both its blocks do; a participation or a relationship belongs to it if and only if its anchor block does.
- **Classification** : 3. Journey logic and membership

## RG042
- **Description** : The journeys a block is attached to are edited through the journey list shown in the block's edit dialog; this list cannot be emptied; the option is disabled when there is only one journey.
- **Classification** : 3. Journey logic and membership

## RG043
- **Description** : Duplicating a journey copies the attachments of its blocks.
- **Classification** : 3. Journey logic and membership

## RG044
- **Description** : A journey's reading sequence is computed depth-first from the Start block, following only the journey's transitions, branches ordered by increasing transition identifier, cycles memoized, and unreachable blocks given a deterministic rank after the others; each block's rank is recomputed on every graph change and at project load, and is never manually editable.
- **Classification** : 3. Journey logic and membership

## 4. Visualization and interaction

## RG045
- **Description** : Each block's position (x, y) is kept in the graphical metadata associated with the project, between sessions.
- **Classification** : 4. Visualization and interaction

## RG046
- **Description** : Blocks automatically snap to the grid at creation and when moved.
- **Classification** : 4. Visualization and interaction

## RG047
- **Description** : Changing the zoom level, the scroll bar positions or the journey filter state is not a modification of the map or the project, and is not persisted between sessions.
- **Classification** : 4. Visualization and interaction

## RG048
- **Description** : The journey filter displays either all journeys or a single one, in all views; it is disabled by default when a project is opened; with the filter active, only the blocks of the journey, the transitions whose two blocks belong to it and the participations/relationships whose anchor block belongs to it remain fully visible — the other elements are dimmed (opacity level set in the configuration) and non-interactive.
- **Classification** : 4. Visualization and interaction

## RG049
- **Description** : In a workspace, only one element is selected at a time; creating or clicking an element selects it and deselects the previous one; a click in the empty area deselects.
- **Classification** : 4. Visualization and interaction

## RG050
- **Description** : A block cannot be created at coordinates overlapping an existing block; its position is automatically adjusted to avoid any overlap.
- **Classification** : 4. Visualization and interaction

## RG051
- **Description** : When a moved block goes beyond the visible part of the workspace, scrolling adjusts to keep the block visible.
- **Classification** : 4. Visualization and interaction

## RG052
- **Description** : A transition's trace must never cross a block that is neither its source nor its target; the transition routing adjusts automatically, without changing block coordinates or project data (graphical adjustment only).
- **Classification** : 4. Visualization and interaction

## RG053
- **Description** : The clickable area of a graphical element (block, transition) is defined by its geometric shape, enlarged beyond the thickness of its stroke.
- **Classification** : 4. Visualization and interaction

## RG054
- **Description** : The notes of blocks and transitions are shown in a tooltip as soon as they are hovered, without delay.
- **Classification** : 4. Visualization and interaction

## RG055
- **Description** : When a context menu opens, the element under the cursor is selected first; the context menu stays aligned with the application menu according to the active view and the current selection.
- **Classification** : 4. Visualization and interaction

## RG056
- **Description** : The cross-view navigation focus (including the "Relationships" view) is a temporary visual state: it marks neither the map nor the project as modified and is not persisted.
- **Classification** : 4. Visualization and interaction

## 5. Technical architecture and data model

## RG057
- **Description** : Agents belong to the project, not to the narrative map.
- **Classification** : 5. Technical architecture and data model

## RG058
- **Description** : The interface never modifies the business model directly: every change goes through the application layers (use cases and services).
- **Classification** : 5. Technical architecture and data model

## RG059
- **Description** : No value is hard-coded in the interface: dimensions, colors, default texts and limits come from the application configuration file.
- **Classification** : 5. Technical architecture and data model

## RG060
- **Description** : Graphical representation metadata (block positions, column order) are stored in a dedicated file associated with the project and restored on reopening.
- **Classification** : 5. Technical architecture and data model

## RG061
- **Description** : The project is saved in a single structured file (JSON) containing metadata and data, associated with the graphical metadata file.
- **Classification** : 5. Technical architecture and data model
