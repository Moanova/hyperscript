# TSK11 — Espace de travail « Journeys » + barre d'onglets + intégration main_window

- **Créée** : 2026-11-11 — passée en Doing 2026-11-11 (TSK08/TSK09/TSK10 en Review) — implémentée et passée en Review 2026-11-11
- **Dépendances** : → #TSK08 (services/use cases), → #TSK10 (nœuds graphiques)

## Objectif

Livrer la vue « Journeys » fonctionnelle dans le MVP : `journeys_workspace.py` (QGraphicsView), `tab_bar.py`, intégration dans `main_window.py` (onglets, actions Project câblées sur les use cases, menu Display > Journey dynamique, filtre FN029, menu contextuel dynamique RG055, persistance des layouts RG060 au save/load).

- **Références** : 04_interface §3/§4 ; FN014–FN022, FN026, FN028, FN029 ; RG045–RG055, RG060 ; décisions séance 03 (onglets en anglais, menus contextuels dynamiques alignés — pas de libellés en dur comme plano `show_context_menu`).

## Travaux réalisés

- `src/ui/views/journeys_workspace.py` (neuf, adapté de plano `events_workspace.py`) : grille 20/80 redessinée sur la zone visible, scène 4000×4000 extensible, auto-scroll à 50 px du bord en drag, scrollbars toujours visibles, sélection unique (RG049), création de transition par tracé port sortie → port entrée (signal `transition_created`, jamais d'écriture du modèle — RG058), filtre de parcours (opacité `journey_filter_opacity` en config, items hors filtre désactivés — RG048), clic droit sélectionne l'item puis émet `context_menu_requested` (RG055), `populate_from_layout` / `populate_default` / `collect_workspace_layout` (RG060), badges de participations rafraîchis depuis le modèle, `next_free_position` (RG050 + snap RG046).
- `src/ui/widgets/tab_bar.py` (reprise plano, onglets « Journeys », « Agents », « Relationships », « Export » ; « Journeys » actif par défaut).
- `src/ui/main_window.py` : tab bar au-dessus des pages empilées (welcome / Journeys / placeholders Agents-Relationships-Export), `_init_workspace()` à la création/ouverture de projet (layout sauvegardé RG060 sinon positions par défaut), `_do_save` persiste le layout, `_close_project` démonte le workspace ; actions câblées : `blocks_new_*` (FN014), `blocks_copy` (FN016), `blocks_delete` (FN018 + cascade RG023), `transitions_new` (FN020), `transitions_delete` (FN022), `journeys_new/copy/delete` (FN023/FN025/FN027), `Display > Journey` dynamique cochable « All journeys » + un item par parcours (FN026/FN029/RG048, non persisté RG047) ; menu contextuel construit **à partir des QAction du menu général** (`menu.addAction(self.menu_actions[key])` — mêmes libellés/raccourcis/états, RG055) ; `workspace_modified` → `set_modified` (FN017).
- Corrections de résidus plano dans `layout_service.py` : `create_empty_layout` (`nodes=` → `block_nodes`/`transition_connections`), `create_connection_layout` (style ARROW par défaut + `relation_id`).
- `view_model.py` : `ConnectionLayout.style` par défaut ARROW (transition = flèche dirigée 2 px).

## Hors périmètre TSK11

Dialogues d'édition (TSK12) : `blocks_edit`, `transitions_edit`, `journeys_edit`, `journeys_set_default` restent des stubs ; menus Agents/Relationships stubs (vues hors MVP). Vue Export : tâche ultérieure.

## Vérifications

- `python -m py_compile` sur tous les fichiers UI modifiés/créés : OK.
- Vérification statique des imports locaux (AST) : OK.
- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` : **40 passed**.
- Tests Qt offscreen (instanciation réelle des composants) : **non exécutables dans le sandbox** (libGL.so.1 absent) — à valider sur poste de dev (TSK13).

## Journal

- 2026-11-11 : implémentation workspace + tab bar + main_window + corrections layout_service/view_model ; py_compile OK, 40 tests passed. TSK11 passée en Review.
