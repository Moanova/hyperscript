# TSK24 — Snap des blocs sur la grille à la libération uniquement (Journeys)

- **Statut** : Doing (18-11-2026) → dépend de #TSK11 (Done)
- **Origine** : retour TSC séance 05 (2026-11-18) : le déplacement des blocs narratifs dans la vue « Journeys » produit des saccades à cause du snap magnétique en continu (RG046). Demande : conserver le même fonctionnement mais activer la grille uniquement au relâchement du bouton.

## Décisions actées (feu vert TSC)

1. **Pendant le drag** : position libre, le bloc suit la souris sans aucun snap (suppression du `snap_to_grid` dans `BaseNode.itemChange(ItemPositionChange)`) — les saccades disparaissent.
2. **À la libération** (`mouseReleaseEvent`) : snap sur la grille (`grid_minor_size` 20 px), clampé aux limites de la scène, puis `setPos` (met à jour layout + observateurs → transitions et marquage modifié).
3. **Création toujours snappée** (RG046 inchangé côté création).
4. **Aucune contrainte de position** : pas d'anneau de boîte englobante comme la vue « Agents » (TSK21–TSK23) — TSC a confirmé que les blocs restent libres de placement n'importe où dans la scène ; RG050 (chevauchement) ne s'applique qu'à la création, inchangé.
5. `setPos` programmatique hors drag reste libre (snap uniquement au relâchement souris).

## Plan d'implémentation

1. `src/ui/nodes/base_node.py` v2 : `itemChange` sans snap (accumulation `_free_pos` + clamp scène conservés) ; `mouseReleaseEvent` → snap grille + clamp + `setPos`.
2. Tests offscreen neufs `tests/test_journeys/test_block_drag_offscreen.py` (skip sans Qt) : drag libre pendant le déplacement (237, 193 non snappé), snap à la libération (240, 200), setPos programmatique libre.
3. Spec FR/EN : RG046 (création + libération), `01_user_stories`, `03_features`, `04_interface` §4, matrices RG046/FN017 ; kanban TSK24 Doing → Review.

## Journal

- 2026-11-18 : tâche créée et passée en Doing (TSK11 Done). Pattern identique à TSK21 (cartes Agents) appliqué aux blocs ; pas de contrainte d'anneau (décision TSC confirmée : les blocs restent libres de placement n'importe où dans la scène).
- 2026-11-18 : **travaux réalisés** — `base_node.py` v2 : `itemChange(ItemPositionChange)` sans snap (accumulation `_free_pos` + clamp scène conservés, position libre retournée) ; `mouseReleaseEvent` → snap `snap_to_grid` (grid_minor_size 20) + clamp scène + `setPos` (itemChange met à jour layout + observateurs → transitions, projet modifié). Création toujours snappée (inchangé). Nouveau test offscreen `tests/test_journeys/test_block_drag_offscreen.py` (3 tests : drag libre (237,193) puis snap à la libération (240,200) ; setPos programmatique libre ; libération au bord de scène clampée puis snappée — skippé sans Qt/libGL). Spec FR/EN : RG046 (création + libération), 01_user_stories, 03_features, 04_interface §4, matrices RG046/FN017. py_compile OK, **73 tests passed + 2 skipped**. Passée en Review.
