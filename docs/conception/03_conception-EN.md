# Hyperscript ::: Design note

- **Date**: 2026-11-09.
- **Status**: adopted.
- **Context**:
  - planoscript closed on 06-11-2026, hyperscript repository initialized on 09-11-2026.
  - This note starts from the preconception note `docs/conception/hyperscript_preconception-FR.md` (planoscript repository, adopted on 06-11-2026) and integrates the decisions of the 09-11-2026 session.


---

## 1. Scope decisions

1. **planoscript is closed**; hyperscript is its successor, with this note as the starting point of the design.
2. The hyperscript MVP scope is aligned with planoscript's wherever the 09-11-2026 session does not decide otherwise (§7); the data model nevertheless anticipates the adopted evolutions (multiple maps, §3).
3. The existing documents in `docs/conception/` will be reviewed if necessary.


## 2. Adopted semantics (FR / EN)

| FR                                                            | EN                                                              | Replaces (planoscript)                                         |
| ------------------------------------------------------------- | --------------------------------------------------------------- | -------------------------------------------------------------- |
| **Bloc narratif** { Début ; Scène ; Pivot ; Condition ; Fin } | **Narrative block** { Start ; Scene ; Pivot ; Condition ; End } | State / Event (two separate components)                        |
| **Transition**                                                | **Transition**                                                  | arc State_to_event / Event_to_state                            |
| **Participation**                                             | **Participation**                                               | State_agent_rel association (agent ↔ state, non-directional)  |
| **Relation** (typée)                                          | **Relationship** (typed)                                        | — (out of the planoscript MVP; free text in practice)          |
| **Agent** { Personnage ; Artefact }                           | **Agent** { Character ; Artefact }                              | Agent { Subject ; Object }                                     |
| **Parcours**                                                  | **Journey**                                                     | Journey                                                        |

- « **Parcours** » (« **Journey** ») is the **adopted** term; « Version » is kept as a **future alternative**, should a redesign need be detected.
- « **Pivot** » replaces « Branch »; the term is bilingual (identical in FR and EN).
- A single **Narrative block** object for all types; the `typ` is chosen at creation and **immutable** afterwards (pattern already proven for `Initial`, planoscript RG061/RG062), with a different visual rendering per type.
- « **Relation** » (EN: « **Relationship** »; JSON key: `relationship`) exclusively designates agent-agent relationships; menus no longer use it as an umbrella term. The planoscript « Relation » state type disappears: the scene concerned becomes a **Scene** again.
- **Relationship** typing is a **list of values defined for the MVP in a configuration file**; its enrichment by the author is a **post-MVP** feature.


---

## 3. Adopted data model

- **Project** { id, lb, dates, agents[], narrative_maps[] } — agents at project level; the map list anticipates from the MVP the possibility of multiple maps (episodes/seasons axis), even if the MVP scope remains a single map per project (§7).
- **Narrative map** { id, lb, active_journey_id, blocks[], transitions[], participations[], relationships[], journeys[] }
- **Narrative block** { id, lb, typ ∈ {Start, Scene, Pivot, Condition, End}, note, content, dates }
- **Transition** { id, from_block_id, to_block_id, note, dates } — directed block → block; chaining constrained by the block-type matrix (§4, RG028), cycles included. **No `condition` key on the transition**: the structured condition is carried only by the Condition block.
- **Participation** { id, block_id, agent_id, note, dates } — presence of an agent in a block (symmetric, matrix view).
- **Relationship** { id, block_id (anchor), agent_a_id, agent_b_id, typ, note, content, dates } — directed and typed, **binary** (`agent_a_id`, `agent_b_id`): a relationship between more than two agents is a **post-MVP** evolution. **Anchored to a block**: "at this point in the story, the relationship A —typ→ B holds". A pair's history = its anchors ordered by block rank; the current state at a block = the last anchor of rank ≤ the block's rank (**derived, never stored**). No clock key (`clock_id`): the rank is that of the anchor block in the journey (`journey_node.sequence_order`).
- **Journey** { id, lb, default, note } + **journey node** { journey_id, block_id, sequence_order } — attachment is **on blocks**, not on transitions.
- **Agent** { id, lb, typ ∈ {Character, Artefact}, note, content, dates }.


## 4. Adopted rules (invariants, enforced by the application)

- **Block-type chaining matrix** (RG028): Start → {Scene, Pivot}; Scene → {Scene, Pivot, End}; Pivot → {Condition}; Condition → {Scene, End}; End → no outgoing transition. While building: 0 to n incoming/outgoing transitions per block; in a finalized, consistent map: 1 to n (consistency check out of the MVP, §7).
- **Start**: unique, automatically created, immutable; never receives an incoming transition; can carry the branching (several outgoing transitions to Scene or Pivot blocks).
- **End**: out-degree 0; adding an outgoing transition is forbidden (to extend: duplicate the block into a Scene); its incoming transitions come exclusively from Scene or Condition blocks.
- **Pivot**: incoming transitions from **Start** or **Scene** blocks only, outgoing transitions to **Condition** blocks only (matrix RG028); several **Condition** blocks from the same Pivot = OR.
- **Condition**: incoming transitions from **Pivot** blocks only, outgoing transitions to **Scene** or **End** blocks only (matrix RG028). Carries the structured condition — **unique support** of it (no `condition` on Transition): kind (choice / artefact / skill / flag), ref to an Artefact agent, label. Two Conditions from the same Pivot = OR; chaining Condition blocks (= AND) is not allowed (Condition → Condition forbidden).
- **Cycles**: allowed, expressed by block chaining — e.g. **S1 (Scene) → P1 (Pivot) → C1 (Condition) → S1**. The DFS sequence memoizes cycles.
- **Journey membership derived** (uniform rule): a Transition belongs to a journey iff **both its endpoints** belong to it; a Participation or a Relationship belongs to it iff its **anchor block** belongs to it. (Solves by construction the cross-association pollution observed on testCase01.)
- **Block attachment to journeys**: no orphan block — every block belongs to at least one journey; a newly created block is attached to the active journey if the journey filter is enabled, to the default journey otherwise; a block cannot be removed from its last journey.
- **Default journey**: unique at all times, automatically created when the map is created; the author can at any time designate another journey as the default journey (the designation replaces the previous one and does not change the active journey).
- **Sequence**: DFS from Start over the journey's transitions, branches explored by increasing transition id, cycle memoization, deterministic fallback for unreachable blocks (analogue of planoscript RG069).
- **Uniqueness**: one transition per ordered pair of blocks; (block, pair, typ) unique for relationships; one participation per (block, agent).
- **Cascades**: deleting an agent → its participations and relationships; deleting a block → its transitions, participations, anchored relationships, journey nodes; deleting a transition → journey nodes referencing it. **Do not reproduce the planoscript bug** `connection.py:811`: any model change goes through the use cases/services layers (TSK34 debt taken into account from the start, §7).


## 5. Views (workspaces)

1. **"Journeys" view** (formerly Events): block graph, rendering by type; journey filter (not persisted); participation badges.
2. **Agents view**: agents × blocks matrix of Participations.
3. **"Relationships" workspace** (anticipated by planoscript `99_mvp_scope-FR.md` §5): graph of agents, arcs labeled by type, annotated with anchor blocks; cross-navigation to the block in the blocks view (analogue of RG067). **Mockup to be defined during the design phase.**
4. **Export view**: reading preview by journey.


## 6. Export

- **Adopted**: reading text by journey — blocks in sequence order; transitions rendered inline; conditions rendered on their branch ("→ if artefact « USB key »: …"); relationships listed under their anchor block; final "relationship state" section (last type per pair).
- **To be defined during the design phase**: technical export format for the development team (persona Jen Yen's frustration #3), export "by events", technical export for reimport, workspace zoom, undo/redo.


## 7. Adopted MVP scope

- **A single narrative map per project** (aligned on planoscript); the data model nevertheless anticipates multiple maps from the MVP (§3).
- **No journey consistency check** in the MVP (dead ends, unfinished branches, single-branch Pivot, unreachable End) — developed as a **post-MVP** feature.
- **No migration** of existing planoscript projects (only two test projects exist to date) — out of scope.
- **Relationship typing**: value list in a configuration file for the MVP; enrichment by the author post-MVP.
- **Planoscript technical debt (TSK34) taken into account from the start**: hyperscript is developed according to best practices — UI → use cases → services → models architecture, no direct writes to the model from the UI, no dead code, and the latent export bug `_esc(rel.agent_id)` handled from the design phase.
- **Sidebars** (planoscript TSK14/TSK30): to be defined during the design phase.


## 8. Summary of the decisions of the 09-11-2026 session

1. « Parcours » / « Journey » adopted; « Version » kept as a future alternative.
2. « Branch » replaced by the bilingual term « Pivot ».
3. Relationship typing: value list in a configuration file for the MVP; enrichment by the author post-MVP.
4. MVP aligned on planoscript (a single narrative map per project); the model anticipates multiple maps from the MVP.
5. Cycles possible, expressed by block chaining (e.g. S1 → P1 → C1 → S1); **no `condition` key on the Transition** (the structured condition is carried by the Condition block).
6. Mockup of the « Relationships » view to be defined during the design phase.
7. No migration of existing planoscript projects (only two test projects).
8. No journey consistency check in the MVP (post-MVP feature).
9. Exports, zoom and editing functions (undo/redo) to be defined during the design phase.
10. Planoscript technical debt taken into account from the start (best practices); sidebars, export by events and technical export for reimport to be defined in the design phase.
11. Kanban TSK01 = writing the design documents; existing documents to be reviewed if necessary.
12. Same-session clarifications: relationships **binary** (`agent_a_id`, `agent_b_id`) until a possible post-MVP evolution; no `clock_id` key (relationship ordering is the anchor block's rank in the journey, derived from `journey_node.sequence_order`); `condition` key removed from the Transition entity.

13. Same-session clarifications (user scenarios): the main view (formerly Events) is called **« Parcours » / Journeys**; the reading export remains **standalone HTML**; **no orphan block** (automatic attachment to the active journey if the journey filter is enabled, to the default journey otherwise, restored); MVP scope of views not decided beyond the minimum **« Parcours » and « Export » views**; the « agents view », « export preview » and « Relations » view scenarios are initialized but to be finalized after the design phase; no business-rule references or technical keys in the scenarios (semantics only); scenario numbering free (planoscript numbering resumed, SU011+ added).

14. Same-session clarifications (features): deleting a journey → **reassignment of its blocks' attachments to the default journey** (no orphan block); **journey filter disabled by default** and **applied to all views**; workspaces are referenced **by name**, without numbering (« Parcours » / "Journeys", « Agents », « Relations » / "Relationships", « Export »); no business-rule references in the features as long as they are not revised; "Status" field removed from the features; new features **FN034–FN037** adopted (agent-agent relationships, structured condition / Scene→Pivot promotion, « Relations » view, list of relationship types in a configuration file); **FN038** adopted: the author can designate the default journey from the menu (`Project › Journeys › Set as Default...`, RG062); creating a journey does not activate it (SU005/FN023: the active journey remains unchanged); new blocks are attached to the active journey if the journey filter is enabled, to the default journey otherwise (FN014/RG040).

15. Same-session trade-offs (menu and misc): general menu adopted (see `docs/specification/05_menu-EN.yaml` /
`05_menu-FR.yaml`) — **Files** in planoscript order with separators (New Project..., Open..., Close, Save, Save as..., sep., Export Map..., Import Map..., sep., Recent Projects, sep., Quit); **Export Map...** and **Import Map...** greyed out in the MVP, **Recent Projects** greyed out in the MVP; Import Map = import a map previously exported into the current project (distinct from the non-migration of planoscript projects); **Edit** reduced to Undo/Redo/Cut/Copy/Paste, still greyed out in the MVP (History and Delete removed, to be re-added after the MVP if needed); **Display** › Journey (checkable list, "All journeys" on top, filter disabled by default, applied to all views, not persisted) and Zoom greyed out in the MVP; **Project** › View (Journeys, Agents, Relationships, Export — views named, without numbering; minimum MVP: Journeys + Export; stub entries, views activated via the tab bar); Agents (New.../Edit.../Copy/Delete.../ **Associate with Block...** — replacing « Link to Block », a term deemed ambiguous with transitions); Narrative Blocks (New › Scene/Pivot/Condition/Ending — **Start deliberately absent: auto-created, unique, not duplicable**, will be the subject of a business rule; Edit.../Copy/Delete...); Transitions (New/Edit.../Delete...); Journeys (New/Edit.../**Copy**/**Set as Default...**/Delete... — "Copy" retained as the duplication term on all submenus; "Set as Default..." = designate the default journey, FN038); Relationships (New.../Edit.../Delete...); **file export (Files › Export Map...) out of the MVP**: only the in-app preview ("Export" view) is in the MVP and is not concerned by this menu entry; in EN, the entity is named **« Relationship »** (FR: « Relation »), most relationships being between characters; the context menu must remain **dynamically aligned with the application menu** according to the active view and the selected objects; the remark "Display dynamic according to the active view" is ignored for the moment; keyboard shortcuts preserved; ellipsis rule adopted: "..." = entry opening a window that requires an additional action from the user (input, choice or confirmation dialog), a purely informational window has none (see the legend of `05_menu-EN.yaml` / `05_menu-FR.yaml`); the application being monolingual English for the moment, all specification documents reference the English names of the menu entries.
