# TSK15 — Correctif z-order : grille sous les transitions (vue « Journeys »)

- **Créée** : 2026-11-11 — passée en Doing 2026-11-11 (TSK11 en Review) — implémentée et passée en Review 2026-11-11
- **Dépendances** : → #TSK11

## Objectif

Corriger le bug visuel signalé par TSC : après certains déplacements de blocs, les flèches de transition « deviennent grises » et les lignes de la grille apparaissent en surimpression sur les flèches.

## Analyse (cause racine)

- `Connection.setZValue(-1)` (`src/ui/nodes/connection.py:111`) et lignes de grille `setZValue(-1)` (`journeys_workspace.py` `_draw_grid`) : à z égale, Qt peint dans l'ordre d'insertion — le dernier arrivé est au-dessus.
- Au chargement, la grille est dessinée avant l'ajout des connexions → flèches au-dessus (aspect nominal, flèche `connection_color` #CCCCCC).
- À chaque `_draw_grid()` (init, scrollbars `valueChanged`, `resizeEvent`, donc aussi auto-scroll pendant un déplacement de bloc près d'un bord), les nouvelles lignes de grille sont rajoutées **après** les connexions → peintes par-dessus → lignes sombres (#333333/#4A4A4A) sur la flèche claire de 2 px = rendu « gris » avec grille en surimpression.
- Référence planoscript : `agents_workspace.py` met sa grille à z=-2 (`events_workspace.py` partage le latent à -1).

## Travaux réalisés

- `_draw_grid()` (`src/ui/views/journeys_workspace.py`) : les 4 créations de lignes de grille passent à `setZValue(-2)` — strictement sous les connexions (-1), elles-mêmes sous les nœuds (0). Aucun impact modèle, hit-testing (`shape()`, RG053) ou persistance. Couleurs nominales conservées telles quelles (décision TSC : gel des couleurs jusqu'à la séance de tests utilisateur complète).

## Vérifications

- `python -m py_compile src/ui/views/journeys_workspace.py` : OK.
- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` : 44 passed.
- Vérification par grep : plus aucun `setZValue(-1)` sur les lignes de grille ; `Connection` reste à -1.
- Validation visuelle offscreen (rendu QImage avant/après `_draw_grid()`) : à faire sur le poste de dev (libGL absent dans le sandbox).

## Journal

- 2026-11-11 : diagnostic cause racine (z=-1 partagé grille/connexions + ordre d'insertion), correctif z=-2 appliqué, tests OK, TSK15 passée en Review.
