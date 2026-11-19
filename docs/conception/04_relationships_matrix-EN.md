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
