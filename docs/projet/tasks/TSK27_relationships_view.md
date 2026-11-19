# TSK27 — Vue « Relationships » (matrice agent×agent + panneau latéral)

- **Statut** : Doing (19-11-2026) → Review (19-11-2026) ; dépend de #TSK20 (Done), #TSK26 (Done)
- **Origine** : maquette actée séance 06 (SU012/FN036, `04_interface` §6, RG069/RG070, `05_menu` context_menu, FN032). Dernière tâche restante du kanban.

## Implémentation réalisée

- `core/services/relationship_service.py` : + `block_min_rank` (min des `sequence_order` multi-parcours), `pair_state_at_block` (RG069 : état dérivé de la paire au bloc = dernier ancrage de rang ≤, rang minimal multi-parcours), `ordered_anchor_block_ids` existait déjà (TSK20).
- `core/models/view_model.py` : `ProjectLayout.relationships_axis_order` (RG070, persistance `layouts/project.json`).
- `src/config/config.json` : `relationships_view_panel_width_px` 260, `relationships_view_cell_size_px` 64, `relationship_type_colors` (map type→couleur).
- `ui/views/relationships_workspace.py` (nouveau) : `QSplitter` = matrice `QTableWidget` lecture seule (en-têtes déplaçables, symétrique, diagonale désactivée, cellule = type + couleur config, tooltip note) + panneau droit (combos filtre parcours/agent miroirs du menu Display + liste des blocs par rang minimal restreinte aux visibles RG064). Cellule hors filtre → désactivée (RG048/RG063/RG064) ; filtre agent actif → agents non concernés estompés + cellules de paires ne les impliquant pas désactivées (création interdite, RG069). Drag d'en-tête → `axis_order_changed` + `workspace_modified` (persisté au save). Signaux uniquement vers MainWindow (RG058).
- `ui/views/journeys_workspace.py` : + signal `selection_changed` (émis dans `_select_item_only`/`_clear_all_selections`), + `focus_block` (RG056/FN032).
- `ui/main_window.py` : création du workspace dans `_init_workspace` (populate avec le project layout), destruction dans `_teardown_workspace`, `_on_tab_changed` transmet le bloc sélectionné dans Journeys s'il est dans les filtres actifs sinon Start (RG068/RG069), `_set_journey_filter_active`/`_set_agent_filter` poussent vers la vue (resync panneau), `_update_menu_state` → `refresh()` de la vue, `_do_save` persiste l'ordre des axes (RG070), menu contextuel cellule (`relationships_new/edit/delete` + « View in Journeys view » → `_view_relationship_anchor_in_journeys` : focus sur le bloc d'ancrage de l'état de la cellule), `_block_in_active_filters`.
- Tests : `tests/test_relations/test_relationships_view_logic.py` (5 tests Qt-free : min rank, état dérivé, persistance ordre axes, visibilité filtres RG048/RG063) + `test_relationships_workspace_offscreen.py` (4 tests offscreen : forme/ordre initial, cellule=état dérivé + Start par défaut, filtres, moveSection → axis_order_changed + persistance).

## Journal

- 2026-11-19 : passée en Doing (TSK20/TSK26 en Review puis Done). Implémentation réalisée ; py_compile OK ; **93 tests passed + 3 skipped** (offscreen Qt sans libGL — à valider sur poste de dev). Passée en Review 19-11-2026.
- 2026-11-19 (retour TSC, test manuel) : anomalie à l'ouverture ET à la création d'un projet — `AttributeError: self.relationships_page` dans `_init_workspace` (`main_window.py`) : la page « Relationships » était créée en variable locale dans `__init__` (stockée seulement dans `view_pages`), sans attribut. **Corrigée** : `self.relationships_page` créé comme attribut de page dans `__init__` (« Export » seul reste en placeholder) + test de fumée offscreen `tests/test_relations/test_main_window_smoke_offscreen.py` (création de projet via MainWindow → 3 workspaces construits, ancre = Start).
- 2026-11-19 (retour TSC n°2) : seconde anomalie au chargement d'un projet préexistant — `NameError: QListWidgetItem` dans `relationships_workspace._rebuild_block_list` (nom utilisé mais non importé). **Corrigée** (import ajouté, imports inutilisés retirés) ; contrôle `pyflakes` sur tout `src/` : plus aucun nom non défini.
- Choix d'implémentation : filtre agent actif → une cellule est désactivée si la paire n'implique pas l'agent filtré (création interdite pour les agents estompés, RG069) ; déplacement d'en-tête synchronise ligne et colonne (matrice symétrique) puis rebuild complet.
