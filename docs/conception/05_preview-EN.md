# Design — the "Preview" view (in-app reading preview) — TSK37, SU010 / FN033

- **Date**: 2026-11-23 (session 11)
- **Status**: design adopted (TSC decisions, session 11) — implementation to come (dedicated task after TSK37)
- **Context**: SU010/FN033 planned an "Export" view (in-app preview, minimal MVP); the planoscript PoC shipped an equivalent preview (plano TSK31/TSK33: "Export" tab, `ExportWorkspace(QTextBrowser)` + `ExportService.build_reading_text`; file export FN013 implemented on neither side). The view is **renamed "Preview"**.
- **Out of scope**: SU007 / FN013 (HTML file export, "Files > Export Map..." greyed out, post-MVP) — unchanged; the coexistence "Preview" (in-app view) / "Export Map" (file, post-MVP) is assumed in the specifications.

## 1. Adopted decisions (TSC, session 11)

1. **Rename Export → Preview**: the view and everything referencing it — tab-bar tab, "View > Preview" menu entry (stub renamed from `view_export`), code objects and future script names (`preview_workspace.py`, `preview_service.py`, etc.). See checklist §6.
2. **Read-only, internal links**: read-only preview; internal hypertext links are anchors with passive scroll only (no effect on the application state). **Regenerated on each switch to the view AND after each model change when the view is already active** (both triggers kept, validated by TSC); never in the background.
3. **Rendering is dynamic according to the active filters** (Journey and/or Agent); the **filter side panel is part of the view** (same version as the "Journeys" view: `FiltersSidePanel(show_block_list=False)` inside a `SidePanelSplitter` at page level, TSK33).
4. Viewing the preview and applying filters **mark neither the map nor the project as modified** (RG058 + adopted point).
5. **Rendered sections** (in order):
   a) Project: project label (`lb`)
   b) Agent list: hypertext links to the project agents (anchors to g)
   c) Map: narrative map label (`lb`)
   d) Journey list: hypertext links to the map's journeys (anchors to e)
   e) Journey: sequence of narrative blocks from Start to End for the current journey, in reading-sequence order (RG044) — each block with `lb`, `typ`, `content`, note as a tooltip on hover; transitions rendered inline; conditions rendered on their branch; **after each block, the relationships anchored on it** (labels of agents 1 and 2, `typ`, `content`, note as a tooltip) — the "state of relationships" is thus rendered under each anchor block, with **no separate final section** (validated by TSC)
   f) Orphans: blocks with **no incoming and no outgoing transition** (adopted definition), for the current journey
   g) Agents: all project agents (`lb`, `typ`, `content`, note as a tooltip)

## 2. Behavior with filters (validated by TSC, session 11)

- Restitution scope: the Agent filter (RG063); the rest unchanged (RG047: filters disabled when a project is opened, not persisted between sessions, mark neither the map nor the project as modified).
- Preview behavior according to the side-panel (or menu) filters: yes — filter state owned and shared by MainWindow, mirrored across all views; changing a filter regenerates the preview (2nd trigger).
- According to the active journey filter: active filter → active journey only (section d: a single link); "All journeys" → all journeys rendered (one section e per journey, anchors d→e); section f restricted to the active journey's orphans.
- Agent filter active: visible blocks = the blocks the agent participates in; transitions whose both blocks are visible; relationships whose anchor block is visible (RG063), intersection with the journey if both filters are active (RG064).
- **Rendering under filters**: elements outside the filters are **omitted from the rendering** (a reading document has no dimmed/interactive state like the graphic views).
- **Navigation via internal anchors**: yes — passive scroll only.
- RG048: the journey filter applies to the map views, including the "Preview" preview; never to the "Agents" view.

## 3. Incomplete journeys (validated by TSC, session 11)

- `JourneySequenceService.recompute_journey` (RG044) computes the sequence as a DFS from the Start block, then appends attached-but-unreachable blocks at the end of the sequence (sorted by id): no block of the journey is ever lost.
- Rendering: main flow = DFS sequence from Start; then the remaining blocks of the journey (e.g. a chain ultimately attached to an End block with no link to the Start chain) are rendered **grouped by chain** (root = block with no incoming transition in the journey), each sub-section carrying a visible "branch not connected to the Start block" marker.
- Fully isolated blocks (no transition at all) go to section f) orphans.
- Journey consistency checking (dead ends, unfinished branches, etc.) remains **post-MVP**: the preview displays, it does not block.

## 4. Planned architecture (to be refined at implementation)

- Dedicated, **Qt-free, read-only** preview service (`core/services/preview_service.py` to come): `build_preview_html(project, narrative_map, journey=None, agent_id=None)` → escaped HTML 4 subset, built from `JourneySequenceService` (RG044 order), attachments (`journey_node`), transitions and `RelationshipService` (relationships per anchor block); never calls `set_modified`.
- UI: `PreviewWorkspace(QTextBrowser)` read-only in `src/ui/views/preview_workspace.py` (as in the PoC: `setOpenLinks(False)`, internal anchors = passive scroll, notes as tooltips via `#note-<kind>-<id>` anchors + index + `anchorAt` + `QToolTip.showText`, explicit dark theme), page = `SidePanelSplitter(browser, FiltersSidePanel(show_block_list=False))` at page level (as Journeys).
- MainWindow integration: "Preview" tab + page in the `QStackedWidget`; regeneration on tab switch (`_on_tab_changed`) and on the modification signal when the view is active; side panel wired to the same signals as the other views (`journey_filter_requested`/`agent_filter_requested`).
- Empty states: no project open (placeholder), journey with no block, journey with no Start attached (RG044 fallback), map with no journey.

## 5. Test plan (at implementation)

- Unit tests of the service: RG044 order, RG063/RG064 filters, orphans, branches not connected to Start, HTML escaping, non-modification.
- Offscreen rendering test (QTextBrowser) + rename tests (menu, tab).

## 6. Code rename checklist (at implementation)

- `menu_actions['view_export']` → `view_preview` (`main_window.py`); menu entry "View > Preview"; tab "Preview" (`tab_bar.py`, docstring); future scripts `preview_workspace.py` / `preview_service.py`.
- "Files > Export Map..." (`export_map`, FN013) **unchanged** (greyed out, post-MVP) — coexistence assumed.
- Specs updated (TSK37): SU010, FN033, `04_interface` §3/§7, `05_menu` FR/EN, RG048 + file-export rule (`02_business_rules` FR/EN), matrix `implementation-FR/EN.md`.
