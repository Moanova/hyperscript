# Hyperscript ::: User Interface Specification

## Document Version
- **Version**: 1.0
- **Date**: 2026-11-09
- **Status**: initial. The application is unilingual for now (English).


---

## General interface architecture

### Layout
- **Type**: main vertical layout (QVBoxLayout):
  - **Top**: menu bar (QMenuBar).
  - **Center**: tab bar, then the workspace (stacked pages: welcome message / project views).
  - **Bottom**: information bar, full width, 30 px.
- **Sidebars**: not planned in the MVP — to be defined during the design phase. *To be validated.*
- **Zoom bar**: none in the MVP (zoom post-MVP; "Display › Zoom" entries greyed out).

### Theme and style
- **Dark theme kept** (plano's charter 98): all colors, dimensions and fonts are read from `config.json` via a centralized theme module — **no hard-coded value in the UI code**.
- Palette (config.json defaults):
  - backgrounds: `bg_primary` `#1E1E1E`, `bg_surface` `#2D2D2D`; borders `border_color` `#383838`;
  - texts: `text_primary` `#FFFFFF`, `text_secondary` `#CCCCCC`; menu hover `menu_hover_bg` `#383838`;
  - connections: `connection_color` `#CCCCCC`, hover `connection_hover_color` `#E5C07B` (fixed sand); badges: `badge_bg_color` `#E5C07B`, `badge_border_color` `#F0F0F0`, `badge_text_color` `#1E1E1E`; error `error_color` `#D19A66`.
  - accents (welcome-page link, scroll bar hover, active tab underline): `block_scene_color` `#E5C07B` (sand);
- Font: Segoe UI; sizes in config (`menu_font_size_px` 12, `node_font_size_px` 13, `node_label_font_size_px` 9, `node_title_font_size_px` 14).
- Node (block): 80×40 px (`node_default_width`/`node_default_height`), corner radius 6 px.
- Grid: minor 20 px / major 80 px (`grid_minor_size`/`grid_major_size`), colors `#333333`/`#4A4A4A`, always visible, redrawn on the visible area only.
- "Agents" view: dots instead of a grid, purely decorative — spacing `agents_view_dot_spacing_px`, radius `agents_view_dot_radius_px`, color `agents_view_dot_color`; **invisible cell grid** for card positioning on drag release (`agents_view_cell_width`×`agents_view_cell_height`, anchored on the scene origin); agent cards `agents_view_card_width`×`agents_view_card_height` (larger than the 80×40 blocks, no ports) — adopted session 04 (TSK19b), invisible cell grid session 05 (TSK21).
- **Colors per narrative block type** (node border color): Start `#D19A66` (gold), Scene `#E5C07B` (sand), Pivot `#E06666` (red), Condition `#E06666` (red), End `#E5C07B` (sand) — adopted session 04 from the TSC visual test feedback (TSK16); Pivot and Condition deliberately share the same red, the type displayed inside the node tells them apart.
- "Relationships" view (adopted session 06, revised session 09 TSK29): right side panel width `relationships_view_panel_width_px`; **square matrix cells** `relationships_view_cell_size_px` (100); color per relationship type `relationship_type_colors` (indexed on the `relationship_types` list); "all" labels of the two panel filter zones = `journey_list_all_label` / `agent_list_all_label`.


---

## Interface components

### 1. Application window menu bar
- **Type**: native QMenuBar, at the top of the window, dark theme.
- **Content and shortcuts**: specified in `docs/specification/05_menu-EN.yaml` (French version: `05_menu-FR.yaml`). Non-implemented entries remain stubs (greyed out).
- **Behavior**: menus are disabled when no project is open (except "About"); "Save" is disabled if the project is unmodified.

### 2. Window title bar
- Native OS title bar.
- Dynamic format: `Hyperscript : {project_label} ({file_path})` if the project is saved, `Hyperscript : {project_label}` otherwise; welcome message ("start your new project") when no project is open. *Application language to be confirmed (unilingual for now).*

### 3. Tab bar (center)
- Height 40 px, dark theme. Named tabs, without numbering:
  - **Agents** — dedicated agents workspace, anchor dots + cards (see section 5, re-designed session 04);
  - **Journeys** — main view, graph of blocks and transitions, **default active** (display order swapped session 09, TSK28: Agents before Journeys; the default active tab remains "Journeys");
  - **Relationships** — agent-relationship matrix view (see section 6);
  - **Export** — in-app reading preview (see section 7).
- The bar is visible only when a project is open. Views are activated via the tab bar; the "Project › View" menu entries are stubs.
- **MVP scope**: at minimum the "Journeys" and "Export" tabs; "Agents" and "Relationships" according to the view scope to be decided. *To be validated.*
- Tab style: dark theme hover, selected tab bold with a visible 2 px bottom border in `block_scene_color` (sand `#E5C07B`).

### 4. Workspace — "Journeys" view
- **Type**: QGraphicsView. Graph of narrative blocks and their transitions.
- **Grid**: always visible (20/80 px); blocks snap to the grid at creation and on release of a move (free position while dragging, TSK24).
- **Default position at map creation**: the Start block is placed at the left edge of the scene plus one major grid step (80 px), centered vertically within a major grid step (adopted session 04, TSK16); without a saved layout, the other blocks are placed in a column below the Start block. **User-created block** (menu or context menu): at the first free spot to the right of the Start block (one node width + one major step, then lateral scan RG050), anchored on the Start block's current position and snapped to the grid (RG046) - adopted session 04 (TSK16, option B).
- **Scrolling**: horizontal and vertical scroll bars always visible; handle hover/active in `block_scene_color` (sand); auto-scroll when the mouse is within 50 px of an edge; initial scene 4000×4000 px, dynamically extended when blocks exceed it.
- **Selection and editing**: single selection (no multi-selection); selection outline as dashes in the block's type color (`node_selection_dash_pattern`, e.g. `[4.0, 4.0]` — shorter dashes, adopted session 04, TSK16); blocks moved by drag-and-drop; graphical elements hit-tested through an enlarged area (`shape()`); immediate tooltips on hover (block label + note, transition note).
- **Narrative block**: 80×40 px rectangle; border colored by type (color code above); active incoming (left) and outgoing (right) ports (8 px), **except the Start block (no incoming port) and End blocks (no outgoing port), whose port is hidden** (adopted 2026-11-11, TSK14; the business constraint is already covered by RG025/RG028); **type displayed** in the node, **label and note in a tooltip on hover**; badge with the participation count (agents present in the block): bottom-right corner of the node (2/3 of the badge inside the outline, 1/3 outside), 16 px diameter (`journeys_view_badge_diameter_px`), fixed `badge_bg_color` fill, `badge_border_color` outline, `badge_text_color` text; hidden at 0 participation, "9+" beyond 9; "Agents: …" line added to the tooltip.
- **Transition**: directed arrow, 2 px (`connection_color`), follows the connected blocks, not movable as such; hover as a solid line in `connection_hover_color` (fixed sand, adopted session 04, TSK16); note shown in a tooltip on hover; created with a temporary trace from the source block's outgoing port to the target block's incoming port; creation must start on the source's outgoing port and end on the target's incoming port (a click near the edge of a block lacking the required port counts as off-port, TSK14).
- **Journey filter**: applies to the **views bearing on the narrative map** (not to the "Agents" view); disabled by default when a project is opened; not persisted between sessions. With the filter active, only the blocks of the active journey, the transitions whose two blocks belong to it, and the participations/relationships whose anchor block belongs to it remain at full opacity; other elements are dimmed (opacity 0.25) and non-interactive.
- **Agent filter** (FN039/RG063): "Display > Agent" (checkable list, "All agents" on top, checked = filter disabled by default when a project is opened) filters the map views on the blocks the agent participates in (transitions whose two blocks are visible, participations/relationships whose anchor block is visible); with the journey filter active, **intersection** (RG064); not persisted; does not apply to the "Agents" view (RG048).
- **Context menus**: **dynamically aligned** with the application menu (same actions and handlers) according to the active view and the selected graphical objects; right-click selects the item under the cursor before opening the menu, so actions apply to the clicked item; on the empty grid, the creation entries carry the labels "New Block" (type submenu) and "New Transition" (adopted session 04, TSK16).

### 5. "Agents" view — re-designed session 04 (SU009, TSK19b)
- Workspace dedicated to agents (project level), distinct from the block graph: `bg_primary` background **identical to the "Journeys" view**, but dressed with **anchor dots instead of a grid** (spacing/radius/color in config, drawn on the visible area only) (RG065).
- Each project agent is represented by a **card** (`agents_view_card_width`×`agents_view_card_height`, larger than the 80×40 blocks, **no ports**) displaying label and type; card outline in `block_scene_color` (sand, TSC feedback session 04); note in a tooltip on hover (RG054); **no participation-count badge** on the card — participations and relationships are handled in other views (RG066).
- Cards are freely movable **in 2D** during a move (no corridor, no snap while dragging); **on release**, the card snaps to the nearest cell of the invisible cell grid (`agents_view_cell_width`×`agents_view_cell_height`, anchored on the scene origin; nearest free cell if the target cell is occupied); the release cell must lie within the bounding box of the other cards expanded by one cell (otherwise nearest free cell in that region; single card = free) (RG065, TSK23). On agent **creation**, the card is placed on the first free cell right of the bounding box of the existing cards (default cell (0, 140) if none) (RG065, TSK22). Single selection (RG049); hit-testing through an enlarged `shape()` (RG053); immediate tooltips (RG054).
- Context menu aligned with the application menu (RG055): Edit.../Copy/Delete.../Associate with Block... for an agent card.
- The filters (journey, agent) do not apply to this view (RG048/RG063).
- Card positions are persisted **at project level** in the graphics metadata (project layout file, distinct from the per-map layouts — structure matching the business model: agents belong to the project, RG067), restored on reopening; no business value.

### 6. "Relationships" view — mockup adopted session 06 (SU012 / FN036)
- **Type**: dedicated workspace made of an **agent × agent matrix** (central area, graphics scene) and a **side panel on the right** (width `relationships_view_panel_width_px`, RG059).
- **Matrix**: one row and one column per project agent — **all agents are displayed, even those with no (yet) relationship**; symmetric matrix (non-directed relationships, RG035). **Rows and columns each have their own, independent order** (RG070 revised session 09): initial order alphabetical on the label (ties by identifier); a row/column is moved by dragging its **header card** (move constrained to the row/column axis); orders persisted at project level (`relationships_view_row_order` / `relationships_view_column_order`, as RG067) and restored on reopening. **Scene** (revision session 09, TSK29 — closer to planoscript's Agent × State matrix, `docs/conception/04_relationships_matrix-EN.md`): **square cells** of `relationships_view_cell_size_px` (100); background grid on the visible area only (`grid_minor_color`/`grid_major_color`, below the items, non-interactive); header cards with the **narrative-block rendering** (80×40 `node_default_width/height`, `node_corner_radius_px` corners, `block_scene_color` border, truncated label + RG054 tooltip, `shape()` hit-testing RG053), centered in their cell; type colors `relationship_type_colors` (RG059).
- **Cell (A, B)**: shows the **type of the A-B pair's state at the selected block** — the relationship anchored to the last block of rank lower than or equal to the selected block's rank (derived data, never stored, SU011); only one relationship per (block, pair), hence a single type per cell (RG035); empty cell when the pair has no anchor at a lower or equal rank. The matrix is **dynamic**: recomputed on every selected-block change. The cell is a **clickable object** (revision session 09, TSK29): left click → **creation** dialog (pair A-B and current block pre-filled) when no relationship exists, or **edit** dialog of the existing relationship; right click → context menu; a cell outside the filter is dimmed and not clickable (RG048/RG063).
- **Side panel (right)**: three zones from top to bottom — (1) journey filter, (2) agent filter, (3) **block list** ordered from top to bottom by minimum rank across all journeys (ties by block identifier), restricted to the blocks visible under the active filters (intersection RG064). The two filter zones mirror the "Display" menu: same actions, always synchronized state (two ways to trigger the same action, RG047/RG048/RG063).
- **Current block selection**: by default the **Start** block (which belongs to all journeys — business rule adopted session 06, to be implemented in a dedicated task before TSK20); when switching to "Relationships" from a block selected in "Journeys", that block is selected if it belongs to the active filter, otherwise the Start (an element outside the filter is not selectable, RG048). This state is visual, session-only, not persisted (RG047/RG056).
- **Filters applied to the view**: journey filter (RG048) — relationships whose anchor block is outside the filter are dimmed (configured opacity) and non-interactive; agent filter (RG063) — all agents remain displayed, uninvolved agents are dimmed (same opacity) and creating a relationship involving them is forbidden.
- **Selection and menus**: single selection (RG049); clicking a cell opens the context menu aligned with the application menu (`Project › Relationships`: New.../Edit.../Delete..., RG055); "View in Journeys view" switches to "Journeys" with the focus on the anchor block (FN032, temporary visual state RG056); relationship note in a tooltip on hover (RG054).
- **MVP scope**: the "Relationships" view (matrix + side panel) is part of the MVP.

### 7. "Export" view (in-app preview)
- "Export" workspace: read-only reading preview of the current narrative map (inert links, no interaction on the content).
- Regenerated on each switch to the "Export" tab, and after each model change when the tab is already active; never in the background.
- Dynamic according to the journey filter (active filter → active journey only; "All journeys" → all journeys).
- Rendered content: blocks from the Start block in reading sequence order, transitions rendered inline, conditions rendered on their branch, agent relationships listed under their anchor block, final "state of relationships" section; label as title, content as body text (label only if empty), note in a tooltip on hover.
- Part of the **minimal MVP**; may be renamed later. *Details to be finalized after the design phase* (SU010).
- Viewing the preview marks neither the map nor the project as modified.

### 8. Information bar (bottom)
- Full width, height 30 px, dark theme (surface background, top border).
- Displays a contextual message depending on the selected object (block, transition, participation, relationship, agent); empty when nothing is selected. Information bar messages do not mark the project as modified.

### 9. Welcome message
- Displayed in the center as long as no project is open (the tab bar is hidden).
- Centered text, 40 px padding, dark theme: title + paragraph with a "create a new project" link in `block_scene_color` (sand) triggering project creation.


---

## Zoom
- Out of the MVP: the "Display › Zoom" entries (in/out/reset, Ctrl+= / Ctrl+- / Ctrl+0) remain greyed out; no zoom bar. Zoom will be added after the MVP (to be defined during the design phase).


---

## Open points to be validated during the design phase
1. Shapes/icons of the 5 narrative block types and of transitions — color code adopted session 04 from the visual test feedback (TSK16, see "Theme and style").
2. Badges: participation count in the "Journeys" view — adopted session 03 (see section 4); incoming/outgoing transition counts in the "Agents" view (to be re-designed).
3. Mockup of the "Relationships" view — **adopted session 06** (see section 6).
4. Content of the "Agents" view (re-design).
5. Sidebars (whether to integrate them or not).
6. Zoom (post-MVP).
7. MVP scope of the views beyond the minimum "Journeys" + "Export".
