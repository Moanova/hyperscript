# Design — "Relationships" matrix (agent × agent), closer to the planoscript model

- **Date**: 2026-11-19 (session 09, TSK29)
- **Context**: the "Relationships" view (TSK27) used a read-only `QTableWidget` with natively movable headers and a single shared row/column order. TSC wants to get closer to the Agent × State matrix of planoscript (figé `faa8fdd`: `src/ui/views/agents_workspace.py` + `src/ui/nodes/matrix_card.py`), with adopted adaptations.

## planoscript references (figé faa8fdd)

- Custom scene: `AgentsWorkspace(QWidget)` + `_MatrixGraphicsView(QGraphicsView)`; 120×80 cells (`agents_view_cell_width/height`); headers = cards (`MatrixCardItem` 80×40): states on the first row (columns), agents on the first column (rows); checkboxes (`MatrixCheckItem`) centered at each intersection; background grid, visible area only, non-interactive lines.
- Reordering: header card drag **constrained to its axis**; on release, rounded target, `pop`/`insert`, `_persist_visual_order()`, full `_relayout()`.
- Order: `resolve_matrix_order(entities, saved_order, pinned_first_id)` (Qt-free); persistence `agents_view_row_order`/`column_order` in the `WorkspaceLayout` (per narrative map in planoscript).

## Decisions adopted (TSC, session 09)

1. **Independent rows and columns** (as in planoscript): two separate persisted orders — `relationships_view_row_order` and `relationships_view_column_order` in `ProjectLayout` (project level, RG067 — agents are project-level RG057, unlike planoscript). **RG070 revised** accordingly.
2. **Square cells**: `relationships_view_cell_size_px` = **100** (cell 100×100). Agent cards 80×40 centered → 10 px on each side, i.e. **20 px between adjacent cards horizontally** (checked), 60 px vertically.
3. **Agent cards with the narrative-block rendering**: 80×40 (`node_default_width/height`), corner radius `node_corner_radius_px`, **sand** border `block_scene_color` (consistency with the "Agents" view, RG066), truncated label + tooltip (RG054), `shape()` hit-testing (RG053). Technical object distinct from `BlockNode` (no ports): `MatrixAgentCard` (custom QGraphicsRectItem).
4. **Clickable cell** (no checkbox): left click on cell (A, B) → **creation** dialog (pair A-B + current block pre-filled) when no relationship exists, or **edit** dialog of the existing relationship (derived state at the selected block); right click → context menu (`Project › Relationships` + "View in Journeys view"). planoscript used a checkbox (binary yes/no association) — not suited here since a relationship is typed + anchored (type/anchor choice needed).
5. **Initial order kept**: alphabetical (label, ties by id) — RG070 unchanged on this point (planoscript used ascending id).
6. **Persistence at project level**: yes (ProjectLayout, `layouts/project.json`).
7. **Offscreen tests rewritten**: yes.

## Geometric mockup (TSK29)

- Scene: square cells C=100; cells area offset by C in x and y (`_CELLS_LEFT = _CELLS_TOP = C`); column cards on top (y = (C−40)/2 = 30, x = C + col·C + 10); row cards on the left (x = 10, y = C + row·C + 30); cell (row, col) = rect (C + col·C, C + row·C, C, C).
- Grid: lines spaced by C, visible area only, z = -2, `grid_minor_color`/`grid_major_color`, non-interactive.
- Cell: background `relationship_type_colors[typ]` (fallback `block_scene_color`), centered type text, tooltip = note; empty = discreet background; diagonal disabled; outside filter = dimmed (`journey_filter_opacity`) + not clickable.
- Drag: header card constrained to its axis while dragging; on release target = `round((pos − C − offset)/C)`, clamped, `pop`/`insert`, both orders persisted (signals), full relayout.
- Initial/resolved order: `resolve_axis_order(agents, saved_order)` Qt-free (in `relationship_service.py`): saved order (valid ids) then missing ones by (label, id).

## Deliberate differences vs planoscript

- Persistence at **project** level (not per narrative map) — RG057/RG067.
- Cell = clickable indicator (type + color), not a checkbox — RG035 (typed + anchored).
- Initial order alphabetical (not ascending id).
- Side panel (filters + block list, 3rd dimension) kept — specific to hyperscript.

## Revision TSK30 (session 10, TSC test feedback)

- **Top-left anchoring + scrolling**: view alignment `AlignLeft|AlignTop`, scene of at least 4000x4000 anchored on (0, 0) growing rightwards/downwards only; scrollbars always visible; the grid covers the **whole visible area** (`_GridLineItem` non-interactive lines — empty `shape()` but real `boundingRect()` — redrawn on scroll and resize). The window stays shrinkable (no minimum raised by the view).
- **Cell = checkbox** (back to the plano model, replaces session-09 decision 4): centered box outline (`relationships_view_checkbox_size`/`relationships_view_checkbox_color`) + **solid gold circle** (`relationships_view_check_color`) when the pair has a relationship; **a dot at the center of each cell** (same rendering as the "Agents" view anchor dots); the **type + note show in the tooltip on hover**. Left click: empty cell → **direct "Undefined" creation** (pair + current block, no dialog), filled cell → edit dialog; right click → context menu (unchanged, RG055).
- **Fixes**: header-card tooltip without the invalid `QWidget` 3rd argument (`QToolTip.showText(pos, text)`, the item is not a widget) + `hideText` on `hoverLeaveEvent`; card/cell hit-testing in item-local coordinates (`mapFromScene` before `shape().contains`) — row/column drags and cell clicks work again.
- **Side panel**: horizontal separator after the agent filter; the journey combo emits the chosen id (`None` = "All journeys") and the `MainWindow` **activates that journey** (FN026) + enables the filter (FN029), like "Display > Journey"; panel resynced after every journey CRUD.
- **Outside the matrix**: default active view "Agents" on project creation/open (revises TSK28); "Agents" view: creation on the first free cell from (0, 0) in row-major scan, workspace extensible rightwards/downwards only (scene clamped at 0 on the left/top).

## Revision TSK31 (session 10, 2nd feedback batch)

- **2.1**: `contextMenuEvent` uses `event.pos()`/`globalPos()` (`QContextMenuEvent` has no `position()` in all Qt6 versions) — no more exception on right click.
- **2.2**: the dimmed diagonal is matched by **agent identity** (`ai == aj`), not by index — with independent orders (RG070), the "same agent" cell follows the dragged card.
- **2.3**: transparent cells (no own fill/border) → the matrix lines are the background grid lines, identical everywhere.
- **2.4**: a dot at the center of **every cell of the whole visible workspace**, painted in the view's `drawBackground` (Agents-view anchor-dot rendering).
- **2.5**: the view applies `theme.WORKSPACE_STYLESHEET` + `WA_StyledBackground` → scrollbars identical to the "Journeys" view (always visible, dark, thin).
- **3.1**: separator = filled bar 2 px (`relationships_view_separator_height_px`) in `grid_major_color`.
- **3.2**: splitter slot pinned to the panel width on resize (`setSizes`) → no gray strip on the right of the panel; dark-themed panel (`theme.SIDE_PANEL_STYLESHEET`); block list vertical scrollbar always visible, Journeys-styled, list zone only.
- Outside the view: "Agents" view — first card margin = inter-card gap (40 px), invisible grid offset accordingly (`snap_to_grid` offset).
