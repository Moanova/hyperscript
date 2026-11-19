# TSK29 — Matrice « Relationships » rapprochée du modèle planoscript (révision RG070 séance 09)

- **Statut** : Review (19-11-2026) ; dépend de #TSK27 (Review)
- **Origine** : demande TSC séance 09 — reprendre le modèle de la matrice Agent × State de planoscript (figé `faa8fdd`) pour la matrice Agent × Agent. Note de conception : `docs/conception/04_relationships_matrix-FR/EN.md`.

## Décisions actées (séance 09)

1. Lignes et colonnes **indépendantes** (deux ordres persistés : `relationships_view_row_order` / `relationships_view_column_order` dans `ProjectLayout`, niveau projet) — RG070 révisée FR/EN.
2. Cellules **carrées 100×100** (`relationships_view_cell_size_px` = 100) ; cartes 80×40 centrées → 20 px entre cartes adjacentes en horizontal (vérifié).
3. Cartes d'en-tête au **rendu des blocs narratifs** (80×40, coins `node_corner_radius_px`, bordure sable `block_scene_color`, libellé tronqué + infobulle RG054) — objet technique `MatrixAgentCard` (QGraphicsRectItem custom, pas de ports).
4. **Cellule cliquable** (pas de coche) : clic gauche → création (paire + bloc courant pré-remplis) ou édition (relation existante) selon l'état au bloc sélectionné ; clic droit → menu contextuel. Hors filtre → estompée + non cliquable.
5. Ordre initial **alphabétique** (libellé, repli id) — conservé.
6. Persistance **niveau projet** — conservée.
7. Tests offscreen **re-rédigés**.

## Plan d'implémentation

1. `view_model.py` : `ProjectLayout.relationships_axis_order` → `relationships_view_row_order` + `relationships_view_column_order` (migration : fallback sur l'ancien champ en `from_dict`).
2. `relationship_service.py` : `resolve_axis_order(agents, saved_order)` Qt-free (ordre sauvegardé, puis manquants par (lb, id)).
3. `ui/nodes/matrix_agent_card.py` (nouveau) : `MatrixAgentCard` — 80×40, coins arrondis, bordure sable, libellé tronqué, tooltip, sélection (RG049), drag contraint à l'axe (kind 'row'/'column'), signaux dragged/released.
4. `ui/views/relationships_workspace.py` (réécrit) : `QSplitter` = `_MatrixGraphicsView` (scène custom) + panneau (combos filtres + liste blocs, inchangé). Géométrie C=100, `_CELLS_LEFT=_CELLS_TOP=C`. Cellules = items cliquables (`cell_clicked` signal) + `context_menu_requested`. Drag → cible arrondie, pop/insert, `axis_order_changed(row_order, col_order)` + `workspace_modified`, relayout. Filtres RG048/063/064 (cellules estompées/désactivées).
5. `ui/dialogs/relationship_dialog.py` : présélection création (`default_agent_1_id`, `default_agent_2_id`, `default_block_id`).
6. `main_window.py` : `cell_clicked` → création/édition selon `pair_state_at_block` ; context menu adapté (row/col → ordres) ; `_do_save` persiste les deux ordres ; `_on_tab_changed` inchangé.
7. Tests : `test_relationships_view_logic.py` (+ `resolve_axis_order`, persistance deux ordres) ; `test_relationships_workspace_offscreen.py` re-rédigé (scène, drag row/col, cellule cliquable, filtres).
8. Specs : RG070 révisée, `04_interface` §6/§2, config 100, conception 04, matrices, kanban.

## Journal

- 2026-11-19 : passée en Doing (TSK27 en Review).
- 2026-11-19 : implémentée — `view_model.py` (deux ordres + migration `from_dict`), `relationship_service.resolve_axis_order`, `ui/nodes/matrix_agent_card.py` (nouveau), `relationships_workspace.py` réécrit (scène v2 : `_MatrixCell` cliquable, `_MatrixGraphicsView`, drag contraint à l'axe → `_reorder` + `axis_order_changed(row, col)`), `relationship_dialog.py` pré-remplissable, `main_window.py` (`_on_relationship_cell_clicked`, persistance des deux ordres, menu contextuel via `agent_id_at_row/col`) ; note de conception `04_relationships_matrix-FR/EN.md`, RG070 révisée, `04_interface` §6/§2, config `relationships_view_cell_size_px`=100, matrices FR/EN ; tests : `test_relationships_view_logic.py` (+ resolve_axis_order, deux ordres, migration) et `test_relationships_workspace_offscreen.py` réécrit (scène, clic cellule, drag row/col indépendant, filtres, restauration ordres sauvegardés). Vérifications sandbox : py_compile OK, pyflakes clean, 95 tests passed + 4 skipped (tests Qt offscreen skippés ici, sans libGL — à valider sur le poste de dev). Passée en Review.
- 2026-11-19 (retour TSC, test manuel) : anomalie au démarrage — `ImportError: QToolTip` depuis `PySide6.QtGui` dans `matrix_agent_card.py` (`QToolTip` est dans `PySide6.QtWidgets`, convention du dépôt). Corrigée + grep de contrôle (aucun symbole QtWidgets importé depuis QtGui dans `src/`).
