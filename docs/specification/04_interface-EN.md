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
  - connections: `connection_color` `#CCCCCC`; badges: `badge_bg_color` `#E5C07B`, `badge_border_color` `#F0F0F0`, `badge_text_color` `#1E1E1E`; error `error_color` `#D19A66`.
- Font: Segoe UI; sizes in config (`menu_font_size_px` 12, `node_font_size_px` 13, `node_label_font_size_px` 9, `node_title_font_size_px` 14).
- Node (block): 80×40 px (`node_default_width`/`node_default_height`), corner radius 6 px.
- Grid: minor 20 px / major 80 px (`grid_minor_size`/`grid_major_size`), colors `#333333`/`#4A4A4A`, always visible, redrawn on the visible area only.
- **Colors per narrative block type** (node border color): Start `#E5C07B` (gold), Scene `#A7C957` (olive green), Pivot `#D19A66` (copper), Condition `#E06666` (red), End `#F0F0F0` (off-white) — adopted session 03; values to be confirmed after the first visual tests, within the same hues (dark grey, off-white, gold, sand…).


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
  - **Journeys** — default active (main view, graph of blocks and transitions);
  - **Agents** — matrix view (see section 5);
  - **Relationships** — agent-relationship graph view (see section 6);
  - **Export** — in-app reading preview (see section 7).
- The bar is visible only when a project is open. Views are activated via the tab bar; the "Project › View" menu entries are stubs.
- **MVP scope**: at minimum the "Journeys" and "Export" tabs; "Agents" and "Relationships" according to the view scope to be decided. *To be validated.*
- Tab style: dark theme hover, selected tab bold with visible bottom border.

### 4. Workspace — "Journeys" view
- **Type**: QGraphicsView. Graph of narrative blocks and their transitions.
- **Grid**: always visible (20/80 px); blocks snap to the grid at creation and when moved.
- **Scrolling**: horizontal and vertical scroll bars always visible; auto-scroll when the mouse is within 50 px of an edge; initial scene 4000×4000 px, dynamically extended when blocks exceed it.
- **Selection and editing**: single selection (no multi-selection); blocks moved by drag-and-drop; graphical elements hit-tested through an enlarged area (`shape()`); immediate tooltips on hover (block and transition notes).
- **Narrative block**: 80×40 px rectangle; border colored by type (color code above); active incoming (left) and outgoing (right) ports (8 px), **except the Start block (no incoming port) and End blocks (no outgoing port), whose port is hidden** (adopted 2026-11-11, TSK14; the business constraint is already covered by RG025/RG028); **type displayed** in the node, **label and note in a tooltip on hover**; badge with the participation count (agents present in the block): bottom-right corner of the node (2/3 of the badge inside the outline, 1/3 outside), 16 px diameter (`journeys_view_badge_diameter_px`), fixed `badge_bg_color` fill, `badge_border_color` outline, `badge_text_color` text; hidden at 0 participation, "9+" beyond 9; "Agents: …" line added to the tooltip.
- **Transition**: directed arrow, 2 px (`connection_color`), follows the connected blocks, not movable as such; note shown in a tooltip on hover; created with a temporary trace from the source block's outgoing port to the target block's incoming port; creation must start on the source's outgoing port and end on the target's incoming port (a click near the edge of a block lacking the required port counts as off-port, TSK14).
- **Journey filter**: applies to **all views**; disabled by default when a project is opened; not persisted between sessions. With the filter active, only the blocks of the active journey, the transitions whose two blocks belong to it, and the participations/relationships whose anchor block belongs to it remain at full opacity; other elements are dimmed (opacity 0.25) and non-interactive.
- **Context menus**: **dynamically aligned** with the application menu according to the active view and the selected graphical objects; right-click selects the item under the cursor before opening the menu, so actions apply to the clicked item.

### 5. "Agents" view
- *Specification left empty for now — re-design work to come* (SU009 initialized, to be finalized after the design phase).

### 6. "Relationships" view
- *Specification left empty for now — the mockup will be defined during the design phase* (SU012 / FN036). Reminder of the need: graph of agents, arcs labeled by type, annotated with anchor blocks, cross-navigation to the anchor block in the "Journeys" view.

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
- Centered text, 40 px padding, dark theme: title + paragraph with a "create a new project" link triggering project creation.


---

## Zoom
- Out of the MVP: the "Display › Zoom" entries (in/out/reset, Ctrl+= / Ctrl+- / Ctrl+0) remain greyed out; no zoom bar. Zoom will be added after the MVP (to be defined during the design phase).


---

## Open points to be validated during the design phase
1. Visual style of the 5 narrative block types (shapes/icons) and of transitions — color code adopted session 03 (see "Theme and style"); color values to be confirmed after the first visual tests (same hues).
2. Badges: participation count in the "Journeys" view — adopted session 03 (see section 4); incoming/outgoing transition counts in the "Agents" view (to be re-designed).
3. Mockup of the "Relationships" view.
4. Content of the "Agents" view (re-design).
5. Sidebars (whether to integrate them or not).
6. Zoom (post-MVP).
7. MVP scope of the views beyond the minimum "Journeys" + "Export".
