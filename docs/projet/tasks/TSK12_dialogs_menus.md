# TSK12 — Dialogues + câblage des entrées restantes du menu Project

- **Créée** : 2026-11-11 — passée en Doing 2026-11-11 (TSK08–TSK11 en Review) — implémentée et passée en Review 2026-11-11
- **Dépendances** : → #TSK09 (use cases parcours), → #TSK11 (workspace + menus en place)

## Objectif

Dialogues d'édition de la vue « Journeys » (reprise adaptée des dialogues planoscript) + câblage des entrées `Project` restantes : `blocks_edit` (FN015), `transitions_edit` (FN021), `journeys_edit` (FN024), `journeys_set_default` (FN038). Les menus Agents/Relationships restent des stubs (vues hors MVP).

- **Références** : FN015, FN021, FN024, FN035, FN038 ; RG029 (type immuable), RG042 (liste parcours non vidable), RG062 ; 05_menu-EN.yaml.

## Plan d'implémentation

- `src/ui/dialogs/block_dialog.py` (fusion plano `component_dialog` + `relation_dialog`) : BlockDialog(block, journeys, attached_journey_ids, artefact_agents) — Label, Note, Content ; **type affiché en lecture seule** (RG029) ; liste « Journeys » à coches (RG042 : non vidable, désactivée si un seul parcours) ; pour un bloc Condition : condition structurée (kind Choice/Artefact/Skill/Flag, référence éventuelle vers un agent Artefact, libellé) — FN035. `get_values()` → lb/note/content/journey_ids/condition.
- `src/ui/dialogs/transition_dialog.py` : note seule (FN021 ; pas de condition sur la transition).
- `src/ui/dialogs/journey_dialog.py` (plano, adapté) : lb + note (FN024).
- `src/ui/dialogs/journey_selection_dialog.py` (plano, adapté, titre paramétrable) : choix d'un parcours pour « Set as Default... » (FN038/RG062).
- `src/ui/dialogs/__init__.py` : exports.
- `main_window.py` : `_edit_selected_block` (BlockDialog → UpdateBlockUseCase → `node.update_entity_data()` + filtre), `_edit_selected_transition` (TransitionDialog → UpdateTransitionUseCase), `_edit_journey` (JourneyDialog sur le parcours actif → UpdateJourneyUseCase + rebuild menu Journey), `_set_default_journey` (JourneySelectionDialog → SetDefaultJourneyUseCase + rebuild). Câblage des 4 entrées stubs.

## Vérifications

- `python -m py_compile` sur tous les dialogues + `main_window.py` : OK.
- Imports locaux résolus (vérification AST) : OK.
- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` : **44 passed** (ajout de `tests/test_transitions/test_transition_usecases.py` FN020/FN021/FN022 + assertion RG029).
- Dialogues Qt non exécutables dans le sandbox (libGL.so.1 absent) : revue statique + smoke offscreen à valider sur poste de dev (TSK13).

## Journal

- 2026-11-11 : fiche rédigée au passage en Doing.
- 2026-11-11 : 4 dialogues écrits (BlockDialog avec liste parcours RG042 + condition FN035, TransitionDialog note seule, JourneyDialog, JourneySelectionDialog titre paramétrable) ; `main_window.py` : `_edit_selected_block`, `_edit_selected_transition`, `_edit_journey`, `_set_default_journey` câblés sur les entrées `blocks_edit` / `transitions_edit` / `journeys_edit` / `journeys_set_default` (stubs levés). 44 tests passed. TSK12 passée en Review.
