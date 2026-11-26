# TSK40 — Correction TSC séance 12 : règle 2.4 inversée + renommages du panneau latéral

- **Statut** : Review (26-11-2026) ; dépend de #TSK39 (Review 26-11-2026).
- **Origine** : correction TSC en séance 12 — la règle 2.4 de TSK39 était inversée, plus une petite évolution des libellés du panneau latéral.

## Demande TSC (26-11-2026, séance 12)

1. **Règle 2.4 inversée** (panneau latéral, liste des blocs de la vue « Relationships ») :
   - filtre de parcours sur « All journeys » → le ou les parcours du bloc entre parenthèses après le nom : `lb (parcours…)` ;
   - filtre sur un parcours précis → le type du bloc entre parenthèses : `lb (typ)`.
   (TSK39 avait implémenté l'inverse : `lb (typ)` sur « All journeys », `lb (parcours…)` quand un parcours est filtré.)
2. **Renommages des sections du panneau latéral** (`FiltersSidePanel`, vues « Relationships » et « Journeys »/« Preview ») :
   - « Journey » → « Journey Filter » ;
   - « Agent » → « Agent Filter » ;
   - « Blocks » → « Block Sequence ».

## Causes racines (vérifiées dans le code)

| Point | Cause racine | Modification |
|---|---|---|
| 2.4 inversé | `FiltersSidePanel.rebuild_block_list` (`src/ui/widgets/filters_side_panel.py:222-229`) : branche `journey_filter_active` → parcours entre parenthèses, sinon `lb (typ)` | Inverser les deux branches : `journey_filter_active` False (« All journeys ») → `lb (journeys…)` via `JourneyService.attachment_journey_ids` ; True (parcours filtré) → `lb (typ)` |
| Libellés | `QLabel("Journey")` / `QLabel("Agent")` / `QLabel("Blocks")` en dur dans `_build_ui` (`filters_side_panel.py:91,95,106`) | `QLabel("Journey Filter")` / `QLabel("Agent Filter")` / `QLabel("Block Sequence")` |

## Plan d'implémentation

1. `src/ui/widgets/filters_side_panel.py` : 3 libellés + inversion des branches de `rebuild_block_list` (commentaires TSK40).
2. Tests : remanier le test 2.4 de `tests/test_tsk39/test_tsk39_offscreen.py` (nouvelle règle) ; nouveau `tests/test_tsk40/` (test offscreen : libellés des sections « Journey Filter »/« Agent Filter »/« Block Sequence » sur le panneau « Relationships », filtres seuls sur « Journeys »/« Preview » ; + règle 2.4 inversée).
3. Specs FR/EN : `04_interface` §4 (zones **Journey Filter**/**Agent Filter**) et §6 (libellés des 3 zones + règle 2.4 inversée, TSK40) ; note de révision dans la fiche TSK39 ; kanban + SESSIONS.md.
4. Vérifications : `py_compile`, pyflakes sans nouveau warning vs base, suite complète `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`.
5. Kanban : TSK40 → Review après implémentation+tests. Commit+push sur `dev` (demande explicite TSC).

## Journal

- 2026-11-26 : créée en To do puis passée en Doing (feu vert TSC : « implémenter directement et pousser »).
- 2026-11-26 : **implémentée et passée en Review** — `filters_side_panel.py` (3 libellés `QLabel` + branches inversées de `rebuild_block_list`, commentaires TSK40) ; test 2.4 de `tests/test_tsk39/test_tsk39_offscreen.py` remané à la nouvelle règle ; nouveaux tests `tests/test_tsk40/` (+2 offscreen : libellés des sections sur les 3 panneaux, règle 2.4 inversée) ; specs `04_interface` §4/§6 FR/EN (libellés + règle inversée) ; note de révision ajoutée dans la fiche TSK39. **Vérifications** : py_compile OK ; pyflakes sans nouveau warning vs base ; **192 tests passed + 3 failed pré-existants** (`test_block_drag_offscreen.py`, reproductibles sur arbre propre `00de5b4`). Commit+push sur `dev` effectués sur demande explicite TSC.
