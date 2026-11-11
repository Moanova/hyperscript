# Hyperscript ::: Features

## Document Version
- **Version**: 1.0
- **Date**: 2026-11-09
- **Status**: initial.

---

## MVP scope reminder
- A project contains a single narrative map (the data model supports several maps).
- Only renaming the default map, editing its content and its reading export are functional.
- Toolbars are not implemented: the corresponding actions are exclusively accessible from the menu.
- The view scope is not decided beyond the minimum: "Journeys" view and "Export" view.
- The application does not analyze journey consistency (post-MVP feature).
- The application exclusively targets Windows PCs.
- Zoom and editing functions (undo/redo) are to be defined during the design phase.
- The exact scope of the reading export will be specified later.
- No migration of existing planoscript projects.


---

# Application

## FN001: Launch the application
- **Description**: Launch the application.
- **References**: SU001 (home screen); home screen specified in `04_interface` (§9).
- **Expected behavior**:
    - At launch, the application displays a home screen allowing in particular to create a new project.
    - Only one instance of the application can run at a time: if an instance is already running, a new launch exits silently (single-instance guard).

## FN002: Quit the application
- **Description**: Quit the application.
- **References**: SU001 ; menu "Files › Quit" (Ctrl+Q).
- **Expected behavior**:
    - If the current project is modified, the application offers "Save", "Don't save", "Cancel" before quitting.
    - Cancelling keeps the project open and the application running.

## FN003: Display the change log
- **Description**: Display the change log of each application version.
- **References**: menu "About › Change Log".
- **Expected behavior**:
    - A dialog presents the list of versions and the associated changes.

## FN004: Display the "about" information
- **Description**: Display the application's "about" information message.
- **References**: menu "About › About Hyperscript".
- **Expected behavior**:
    - A dialog presents the general information about the application.


---

# Project

## FN005: Create a new project
- **Description**: Create a new narrative project.
- **References**: SU001 ; menu "Files › New Project..." (Ctrl+N) ; home screen.
- **Expected behavior**:
    - The project can be created from the menu, the keyboard shortcut or the home screen.
    - The new project is an unsaved project: it resides in memory and is not associated with any file until the user saves it.
    - It is named "New project" and contains a narrative map named "Main narrative map".
    - Only one project can be open at a time; creating a new project replaces the current one (with a save confirmation if modified).
    - The project has a stable identifier, a name, a creation date and a last modification date; the file path is an application state, not business data.

## FN006: Open a project
- **Description**: Open a project from the file system.
- **References**: SU001 ; menu "Files › Open..." (Ctrl+O).
- **Expected behavior**:
    - The user chooses a valid project file on the file system.
    - In case of an invalid, incompatible or unreadable file, the application shows a clear error message and keeps the current project unchanged.
    - If the current project is modified, a save confirmation is offered before opening.

## FN007: Open a recent project
- **Description**: Open a project from the recent projects list.
- **References**: SU001 ; menu "Files › Recent Projects".
- **Expected behavior**:
    - The menu presents a dynamic list of previously saved or opened projects.
    - The list respects the configured limit of recent projects.
    - Files that no longer exist are removed from the list.
    - The same handling of invalid files and save confirmations as FN006 applies.
- **MVP scope**:
    - "Files › Recent Projects" entry greyed out in the MVP (feature out of the MVP).

## FN008: Save the project
- **Description**: Save the project.
- **References**: SU001 ; menu "Files › Save" (Ctrl+S).
- **Expected behavior**:
    - If the project is already associated with a file, saving occurs without a new dialog.
    - If the project has never been saved, the application asks for a name and a location (behavior equivalent to FN009).
    - The action is disabled as long as the project is not modified.
    - Saving adds the project to the recent projects list.

## FN009: Save the project as...
- **Description**: Save the project under another name or in another location.
- **References**: SU001 ; menu "Files › Save as..." (Ctrl+Shift+S).
- **Expected behavior**:
    - The user chooses a name and a location.
    - The saved copy becomes the current project.
    - The action adds the project to the recent projects list.

## FN010: Close the project
- **Description**: Close the current project.
- **References**: SU001 ; menu "Files › Close" (Ctrl+W).
- **Expected behavior**:
    - If the project is modified, the application offers "Save", "Don't save", "Cancel".
    - After closing, no project is open (back to the home screen).

## FN011: Rename the project
- **Description**: Edit the label (name) of the current project.
- **References**: SU001. **Outside the menu**: no dedicated menu option.
- **Expected behavior**:
    - The project label is a business attribute editable via a project edit window (specification of this window to come).
    - Any label change updates the last modification date and marks the project as modified.
    - The label is not subject to uniqueness.


---

# Narrative map

## FN012: Rename the narrative map
- **Description**: Rename the project's narrative map.
- **References**: SU002 (MVP scope: only renaming the default map is available).
- **Expected behavior**:
    - Renaming is done by directly editing the label or via an edit dialog.
    - Any renaming marks the map, and therefore the project, as modified, and updates the last modification dates.

## FN013: Export the narrative map as a reading document
- **Description**: Export the current narrative map as a standalone reading document (HTML), viewable in a standard browser.
- **References**: SU002 (map export), SU007 ; menu "Files › Export Map...".
- **Expected behavior**:
    - The export is launched from the "Files" menu (no toolbar in the MVP).
    - The export generates a folder named after the map, containing an index file and all the pages needed for hypertext navigation.
    - The document is standalone: no server, no Internet connection, no external dependency; it displays correctly in Chrome, Firefox and Edge.
    - The home page offers the choice of the reading mode; only the "by journey" mode is available in the MVP.
    - In "by journey" mode: an intermediate page lists the map's journeys; choosing a journey displays the complete linear sequence of its blocks.
    - Each block is rendered by its label (paragraph title) and its content (body text); if the content is empty, only the label is displayed. Transitions are rendered inline; conditions are rendered on their branch; agent relationships are listed under their anchor block; a final section summarizes the state of the relationships (last known type per agent pair in the journey).
    - The reading order is the journey's reading sequence (computed from the Start block), independently of the graphical positions.
    - Each reading page offers a link back to the index.
    - The export marks neither the map nor the project as modified.
- **Note**: the "Files › Export Map..." entry is **greyed out in the MVP** (file export out of the MVP; only the in-app preview, FN033, is available in the MVP). The exact scope of the reading export (pages, modes) will be specified later; the technical export intended for reimport is to be defined during the design phase.


---

# Narrative blocks

## FN014: Create a narrative block
- **Description**: Create a narrative block in the narrative map. The type — Start, Scene, Pivot, Condition or End — is chosen at creation and immutable afterwards.
- **References**: SU003 ; menu "Project › Narrative Blocks › New" (type choice).
- **Expected behavior**:
    - In the MVP, creation is done exclusively from the menu (no toolbar).
    - The block is created with an identifier unique within the map, the default label of its type, and the visual rendering corresponding to its type.
    - It is positioned at the location designated by the user, snapped to the alignment grid (always visible and active).
    - It has two active attachment ports: incoming (left) and outgoing (right).
    - It is not resizable.
    - No orphan block: the newly created block is attached to the active journey if the journey filter is enabled, to the default journey otherwise.
    - The Start block is unique: it is created automatically when the narrative map is created and cannot be created manually or duplicated.
    - Any creation marks the map, and therefore the project, as modified.

## FN015: Edit a block's attributes
- **Description**: Edit the editable attributes of a block via an edit dialog.
- **References**: SU003 ; menu "Project › Narrative Blocks › Edit...".
- **Expected behavior**:
    - The edit dialog presents the editable attributes: label, note (annotation) and narrative content. The type is not editable.
    - For a Condition block, the dialog also presents the structured condition: kind (choice / artefact / skill / flag), optional reference to an Artefact agent, label.
    - The label is not subject to uniqueness within the map.
    - Any attribute change marks the map, and therefore the project, as modified.

## FN016: Duplicate a block
- **Description**: Duplicate an existing block.
- **References**: SU003.
- **Expected behavior**:
    - The copy carries a distinct name ("{label} (copy)") and a new identifier.
    - The copy is attached to the active journey.
    - The Start block cannot be duplicated.
    - Any duplication marks the map, and therefore the project, as modified.

## FN017: Move a block
- **Description**: Position or reposition a block in the workspace (visualization).
- **References**: SU003, SU006.
- **Expected behavior**:
    - Moving is done by drag-and-drop with the mouse (PC), stylus or touch mode (tablet).
    - While moving, the block automatically snaps to the grid.
    - The position (x, y) is kept between sessions via the graphical metadata file associated with the project.
    - The block is not resizable.
    - Any move marks the map, and therefore the project, as modified.

## FN018: Delete a block
- **Description**: Delete a block from the narrative map.
- **References**: SU003 ; menu "Project › Narrative Blocks › Delete...".
- **Expected behavior**:
    - If data is associated with the block, a confirmation is requested.
    - Deletion cascades to its transitions, participations, anchored relationships and journey attachments.
    - Any deletion marks the map, and therefore the project, as modified.

## FN019: Manage a block's journey attachments
- **Description**: Edit the list of journeys a block is attached to.
- **References**: SU003, SU005.
- **Expected behavior**:
    - Attachments are managed via a multi-choice list of journeys, presented in the block's edit dialog, among the existing journeys of the map.
    - The list cannot be emptied: no orphan block (a block cannot be removed from its last journey).
    - The option is disabled if the map has a single journey.
    - Any attachment change marks the map, and therefore the project, as modified.


---

# Transitions

## FN020: Create a transition
- **Description**: Create a directed transition between two blocks of the narrative map.
- **References**: SU004 ; menu "Project › Transitions › New".
- **Expected behavior**:
    - In the MVP, creation is initiated from the menu (no toolbar).
    - The user selects a source block; if no block is active, it becomes active. A connection (temporary trace) then follows the cursor until the click on the target block's port.
    - The transition is directed: the source block's outgoing port is linked to the target block's incoming port.
    - Chaining is constrained by the block-type matrix: Start → Scene or Pivot; Scene → Scene, Pivot or End; Pivot → Condition; Condition → Scene or End; End → none. Cycles remain allowed (e.g. Scene → Pivot → Condition → the same Scene).
    - The application refuses creation if a transition already exists for the ordered pair of blocks (source, target), or if the chaining of the two block types is not allowed by the matrix.
    - The transition is represented by a line; it follows the moves of the blocks it links and is not movable as such.
    - Journey membership is derived: a transition belongs to a journey if and only if both its blocks belong to it (no direct attachment).
    - Any creation marks the map, and therefore the project, as modified.

## FN021: Annotate and edit a transition
- **Description**: Annotate a transition with free text and edit its editable attributes.
- **References**: SU004 ; menu "Project › Transitions › Edit...".
- **Expected behavior**:
    - Annotation is done via the transition's edit dialog ("Note" field).
    - The transition's note is shown in a tooltip on hover over the representative line.
    - A transition carries no condition: the structured condition is carried by the Condition block (FN035).
    - Any modification marks the map, and therefore the project, as modified.

## FN022: Delete a transition
- **Description**: Delete a transition between two blocks.
- **References**: SU004 ; menu "Project › Transitions › Delete...".
- **Expected behavior**:
    - A confirmation is requested before deletion.
    - Deleting a transition removes no journey attachment (membership is derived from the blocks, RG041); it is independent of block deletion (except for the FN018 cascade).
    - Any deletion marks the map, and therefore the project, as modified.


---

# Journeys

## FN023: Create a journey
- **Description**: Create a journey in the map.
- **References**: SU005 ; menu "Project › Journeys › New" ; journey list in "Display › Journey".
- **Expected behavior**:
    - The new journey receives a unique identifier, a default label and an empty note.
    - The new journey is not activated: the active journey remains unchanged (if the journey filter is disabled, all journeys are active).
    - Any creation marks the map, and therefore the project, as modified.

## FN024: Rename and describe a journey
- **Description**: Edit the label and note of a journey.
- **References**: SU005.
- **Expected behavior**:
    - Editing is done via an edit dialog.
    - Any modification marks the map, and therefore the project, as modified.

## FN025: Duplicate a journey
- **Description**: Duplicate an existing journey.
- **References**: SU005.
- **Expected behavior**:
    - The copy carries a distinct name and a new identifier.
    - The block attachments of the source journey are also attached to the copy.
    - Any duplication marks the map, and therefore the project, as modified.

## FN026: Activate a journey
- **Description**: Activate a journey as the active journey.
- **References**: SU005 ; journey list in "Display › Journey".
- **Expected behavior**:
    - Activation is done from the journey list.
    - Activation makes the journey the active one: the display filter applies to it (FN029) and new blocks are attached to it (FN014).
    - Activation marks the map, and therefore the project, as modified.

## FN027: Delete a journey
- **Description**: Delete a journey from the narrative map.
- **References**: SU005.
- **Expected behavior**:
    - Deleting the last journey of the map is impossible: the application shows an explanatory message.
    - Otherwise, a confirmation is requested.
    - **The block attachments of the deleted journey are reassigned to the default journey**.
    - If the deleted journey was the default one, the oldest remaining journey becomes the default; if it was the active one, the default journey becomes the active one.
    - Any deletion marks the map, and therefore the project, as modified.

## FN038: Set the default journey
- **Description**: Designate one of the map's journeys as the default journey.
- **References**: SU005 ; menu "Project › Journeys › Set as Default...".
- **Expected behavior**:
    - The designation is done via a dialog selecting the journey to set as default.
    - There is always only one default journey: the designation replaces the current default journey.
    - The default journey is the one to which new blocks are attached when the journey filter is disabled (otherwise, it is the active journey, FN014), and the one used for reassignment of attachments when a journey is deleted.
    - The designation does not change the active journey.
    - Any designation marks the map, and therefore the project, as modified.


---

# Visualization

## FN028: Navigate in the workspace
- **Description**: Navigate in the graphical workspace of the narrative map.
- **References**: SU006.
- **Expected behavior**:
    - Navigation is done with the horizontal and vertical scroll bars.
    - The workspace (visualization) is virtually unlimited (within operating system limits).
    - The block alignment grid is always visible and active.
    - Scroll bar positions and zoom level are not business data: they are not kept between sessions and do not mark the map as modified.
    - The interface remains fully functional for a window of at least 1280×720.
    - Zoom is to be defined during the design phase.

## FN029: Filter the display by journey
- **Description**: Display either all blocks and transitions of the map, or only those of the active journey — in all views.
- **References**: SU006.
- **Expected behavior**:
    - The filter switches between "show all" and "active journey".
    - Entry point: checkable "All journeys" item at the top of "Display › Journey" (checked = filter disabled); checking a journey activates that journey and the filter.
    - **The filter is disabled by default when a project is opened** and its state is not persisted between sessions.
    - **The filter applies to all views** ("Journeys" view, "Agents" view, "Relationships" view, "Export" preview): only the blocks of the active journey, the transitions whose two blocks belong to it, and the participations and relationships whose anchor block belongs to it remain fully visible; other elements are dimmed (reduced opacity) and non-interactive while the filter is active.
    - Switching from one journey to another instantly updates the display of all views.
    - Filtering does not mark the map as modified.


---

# Agents and participations

## FN030: Associate agents with a block
- **Description**: Associate or dissociate one or more agents with a block of the narrative map, from the "Journeys" view or from the "Agents" view.
- **References**: SU008 ; block context menu "Associate agents..." ("Journeys" view) ; agents × blocks matrix ("Agents" view).
- **Expected behavior**:
    - From the "Journeys" view, a block's context menu opens a dialog listing all the project's agents with their current participation status for this block (checked/unchecked). Checking associates, unchecking dissociates.
    - The dialog allows creating a new agent and associating it in a single operation (rules of FN031).
    - From the "Agents" view, editing is done by checking/unchecking the matrix cell.
    - The application prevents a duplicate participation (agent, block).
    - The participating agents of a block are represented by badges on the block in the "Journeys" view.
    - Journey membership is derived: a participation belongs to a journey if and only if its block belongs to it.
    - Any association or dissociation marks the map, and therefore the project, as modified.

## FN031: Manage the project's agents
- **Description**: Create, rename, edit or delete an agent of the project.
- **References**: SU008, SU009 ; submenu "Project › Agents" (New.../Edit.../Delete...) ; "Journeys" and "Agents" views.
- **Expected behavior**:
    - An agent belongs to the project; it is characterized by an identifier unique within the project, a label, a type (Character or Artefact), a note and a narrative content.
    - Deleting an agent cascades to all its participations and all its relationships, with a prior confirmation indicating the number of deleted elements.
    - Any creation, modification or deletion of an agent marks the project as modified.

## FN032: Cross-view navigation
- **Description**: Switch from one view to another while targeting an entity, in order to examine its relationships in the other representation.
- **References**: SU009, SU012.
- **Expected behavior**:
    - From the "Journeys" view, "View in Agents view" switches to the "Agents" view and highlights the targeted block's column.
    - From the "Agents" view, "View in Journeys view" switches to the "Journeys" view and sets the focus on the block (or on all the blocks of an agent).
    - From the "Relationships" view, "View in Journeys view" switches to the "Journeys" view and sets the focus on a relationship's anchor block.
    - The focus is a temporary visual state: a click in the empty area or the Escape key releases it.
    - Navigation marks neither the map nor the project as modified.

## FN033: Export preview (workspace "Export")
- **Description**: Display in the "Export" workspace a read-only reading preview of the current narrative map.
- **References**: SU010, SU007 ; "Export" tab of the tab bar ; journey filter FN029.
- **Expected behavior**:
    - The "Export" tab is present in the tab bar next to the "Journeys" and "Agents" views.
    - The preview is read-only: no interaction on the content; displayed links are inert.
    - The preview is regenerated on each switch to the "Export" tab, and after each model change when the tab is already active; never in the background.
    - The preview is dynamic according to the journey filter (FN029): active filter → active journey only; "All journeys" → all journeys.
    - Rendering: blocks from the Start block, in reading sequence order; transitions rendered inline; conditions rendered on their branch; agent relationships listed under their anchor block; final "state of relationships" section; label as title, content as body text (label only if empty), note in a tooltip on hover.
    - Journey index at the top; section detailing the agents; possible orphan components listed.
    - Viewing the preview marks neither the map nor the project as modified.
- **Note**: scenario SU010 is initialized and will be finalized after the design phase; the "Export" view is part of the minimal MVP scope and may be renamed later.


---

# Relationships between agents

## FN034: Manage a relationship between agents
- **Description**: Create, annotate, edit or delete a typed relationship between two agents, anchored to a block.
- **References**: SU011 ; menu "Project › Relationships".
- **Expected behavior**:
    - The relationship is binary: it links exactly two agents (an evolution to more than two agents is post-MVP).
    - It is directed and typed; the type is chosen from the value list of the configuration file (FN037).
    - It is anchored to a block: "at this point of the story, the relationship A —type→ B holds".
    - There can be only one relationship per (block, agent pair, type).
    - The history of an agent pair is the set of its anchored relationships, ordered by the position of their block in the journey; the current state of the pair at a block is derived (never stored).
    - Journey membership is derived from the anchor block.
    - The note is shown in a tooltip on hover.
    - Deleting an agent or a block cascades to its relationships.
    - Any creation, modification or deletion marks the map, and therefore the project, as modified.


---

# Conditions

## FN035: Manage a Condition block's condition
- **Description**: Edit the structured condition of a Condition block.
- **References**: SU003, SU004.
- **Expected behavior**:
    - The structured condition of a Condition block is edited via the block's edit dialog (FN015): kind (choice / artefact / skill / flag), optional reference to an Artefact agent, label.
    - A Pivot block can only receive incoming transitions from Start or Scene blocks and only emit outgoing transitions to Condition blocks; several Condition blocks from the same Pivot equal an OR.
    - A Condition block can only receive incoming transitions from Pivot blocks and only emit outgoing transitions to Scene or End blocks. Two Condition blocks from the same Pivot equal an OR; chaining Condition blocks (Condition → Condition) is not allowed.
    - An End block cannot receive an outgoing transition.
    - Any modification marks the map, and therefore the project, as modified.


---

# "Relationships" view

## FN036: "Relationships" view
- **Description**: Visualize the graph of agents and their relationships (arcs labeled by type, annotated with anchor blocks) in the "Relationships" workspace, with cross-navigation to the anchor block in the "Journeys" view (FN032).
- **References**: SU012 ; journey filter FN029.
- **Expected behavior**:
    - To be specified with the view's mockup, to be defined during the design phase.
    - The MVP view scope is not decided beyond the minimum ("Journeys" view and "Export" view).


---

# Configuration

## FN037: Relationship type list
- **Description**: Read the type of relationships between agents from a value list defined in a configuration file.
- **References**: SU011.
- **Expected behavior**:
    - In the MVP, the relationship types offered at creation (FN034) are read from the configuration file.
    - Enriching this list by the author is a post-MVP feature.


---

# Out of MVP scope / to be defined during the design phase

- Multi-map operations: creating, duplicating, deleting and navigating between several narrative maps of the same project (MVP: a single map per project; the model supports several maps).
- Importing a narrative map from a standalone file; no migration of existing planoscript projects.
- Technical map export intended for reimport; "by events" reading export — to be defined during the design phase.
- Workspace zoom; editing functions (undo/redo, history, cut/copy/paste) — to be defined during the design phase.
- Toolbars and sidebars — menu actions only in the MVP; sidebars to be defined during the design phase.
- Journey consistency check (dead ends, unfinished branches, single-branch Pivot, unreachable End) — post-MVP feature.
- Author enrichment of the relationship type list (FN037) — post-MVP.
- Relationships involving more than two agents — post-MVP.
- Finalization of the scenarios and features of the "Agents" and "Relationships" views and of the "Export" preview — after the design phase.
