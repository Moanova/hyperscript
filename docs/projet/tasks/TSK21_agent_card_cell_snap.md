# TSK21 — Snap des cartes agent sur cellule invisible à la libération (évolution RG065)

- **Statut** : Doing (18-11-2026) → dépend de #TSK19b (en Review)
- **Origine** : retour TSC séance 05 (2026-11-18) sur le déplacement des cartes dans la vue « Agents » (TSK19b, couloirs RG065 séance 04)

## Demande TSC

Contraindre le positionnement des cartes de la vue « Agents » de sorte qu'après un déplacement par l'utilisateur, la carte ne puisse reposer qu'à l'intérieur d'une **cellule d'une grille non matérialisée** (les points `agents_view_dot_*` restent purement décoratifs).

## Décisions actées (séance 05, feu vert TSC)

1. **Suppression du couloir** (verrouillage d'axe, `AXIS_LOCK_THRESHOLD_PX`) : drag 2D libre, déplacements en diagonale possibles ; aucun snap en cours de drag (le snap « magnétique » en continu avait été rejeté en séance 04).
2. **Snap à la libération uniquement** (`AgentCardItem.mouseReleaseEvent`) : la carte se positionne sur la cellule la plus proche d'une grille invisible ancrée sur l'origine de la scène, taille `agents_view_cell_width`×`agents_view_cell_height` = **200×140** (config.json ; 200 = 10×20 et 140 = 7×20, multiples de l'espacement des points 20 px pour rester cohérent visuellement avec le fond de points).
3. **Cellule occupée** : la carte est poussée sur la **cellule libre la plus proche** (scan en anneaux, distance de Chebyshev — `LayoutService.find_nearest_free_position`, nouveau).
4. **Snap aussi à la création et au chargement** (`AgentsWorkspace.create_agent_card` / `next_free_card_position`) : invariant « toute position de carte est une origine de cellule », donc positions persistées (RG067) toujours sur cellule.
5. `setPos` programmatique hors drag reste libre (pas de snap dans `itemChange`) — la contrainte ne s'applique qu'au déplacement utilisateur.

## Plan d'implémentation

1. `src/config/config.json` : nouvelles clés `agents_view_cell_width` 200, `agents_view_cell_height` 140.
2. `src/core/services/layout_service.py` : nouveau `find_nearest_free_position(x, y, w, h, existing_rects, step_x, step_y, bounds, max_radius)` (scan en anneaux de la grille de cellules, bornes scène optionnelles).
3. `src/ui/nodes/agent_card.py` : suppression du couloir (`_drag_start`, `_lock_axis`, `AXIS_LOCK_THRESHOLD_PX`, bloc de projection d'axe dans `itemChange`) ; `CELL_WIDTH`/`CELL_HEIGHT` (config) ; `mouseReleaseEvent` → snap sur cellule + cellule libre la plus proche (`_cell_snap_target`) + `setPos` + `update_layout` + notification des observateurs.
4. `src/ui/views/agents_workspace.py` : `_CELL_WIDTH`/`_CELL_HEIGHT` ; `next_free_card_position` et `create_agent_card` snappent sur cellule et utilisent `find_nearest_free_position` ; docstrings.
5. Tests : `tests/test_agents/test_agents_workspace_offscreen.py` (drag diagonal libre, snap à la libération, cellule occupée, placement initial sur cellules, z-order, layout) ; `tests/test_agents/test_project_layout.py` (`find_nearest_free_position`, snap cellule).
6. Spec FR/EN : RG065 (`02_business_rules`), `04_interface` §2/§5, SU009 (`01_user_stories`), matrices `implementation-FR/EN.md` ; kanban (TSK21 Doing → Review).

## Journal

- 2026-11-18 : tâche créée et passée en Doing (TSK19b en Review). Décisions actées ci-dessus (analyse séance 05 : options cellule = carte + gouttière 200×140 ancrée sur l'origine scène ; snap à la libération ; cellule occupée → cellule libre la plus proche ; couloir supprimé pour permettre les diagonales — TSC a explicitement préféré la suppression du couloir).
- 2026-11-18 : **travaux réalisés** — `config.json` : clés `agents_view_cell_width` 200 / `agents_view_cell_height` 140 ; `layout_service.py` : nouveau `find_nearest_free_position` (scan en anneaux, distance de Chebyshev, bornes scène) ; `agent_card.py` v2 : couloir supprimé (`_drag_start`/`_lock_axis`/`AXIS_LOCK_THRESHOLD_PX` retirés), `itemChange` = limites scène + accumulation `_free_pos` sans snap, `mouseReleaseEvent` → `_cell_snap_target` (snap cellule + cellule libre la plus proche) + `setPos` + `update_layout` + notification ; `agents_workspace.py` v2 : `next_free_card_position`/`create_agent_card` snappent sur cellule (`snap_to_grid` pas de cellule + `find_nearest_free_position`), snap aussi au chargement des positions sauvegardées ; tests : `test_agents_workspace_offscreen.py` v2 réécrit (8 tests : scène, placement sur cellules sans chevauchement, setPos programmatique libre, drag diagonal 2D + snap à la libération, cellule occupée → cellule libre, z-order, layout persisté ; skippés sans Qt/libGL comme avant) + `test_project_layout.py` (snap_to_grid cellule, find_nearest_free_position ×2) ; spec FR/EN : RG065, 04_interface §2/§5, SU009, matrices implementation. py_compile OK, **73 tests passed, 1 skipped** (module offscreen Qt skippé dans le sandbox — libGL absent, à valider sur poste de dev). Passée en Review.
