# TSK31 — Retours de test TSC (séance 10, 2ᵉ salve) : marges, rendu matrice, ascenseurs, panneau latéral

- **Statut** : Review (20-11-2026) ; dépend de #TSK30 (Review)
- **Origine** : 8 nouveaux retours TSC après test de TSK30 (notés 1.1, 2.1–2.5, 3.1–3.2) + remarque de conception sur la matrice (2 coches par relation, voir « Point ouvert »).

## Analyse des 8 points (cause racine)

| Retour | Symptôme | Cause racine |
|---|---|---|
| 1.1 (vue Agents) | 1ʳᵉ carte collée au coin (0,0) | `next_free_card_position` ancre le scan sur l'origine (0,0) et la carte est posée au coin haut-gauche de sa cellule (pas de marge à gauche/haut, alors qu'entre deux cartes l'écart vaut cellule−carte = 40 px). |
| 2.1 | Exception au clic droit sur cellule/carte : `'QContextMenuEvent' object has no attribute 'position'` | `_MatrixGraphicsView.contextMenuEvent` (`relationships_workspace.py`) appelle `event.position()` — `QContextMenuEvent` n'est pas un `QSinglePointEvent` dans toutes les versions Qt6 : il expose `pos()`/`globalPos()` (`QPoint`). Les vues Journeys/Agents ne sont pas concernées (elles passent par le signal `customContextMenuRequested(pos)`). |
| 2.2 | Le « fond noir » de la diagonale (même agent en ligne et colonne) ne suit pas la carte déplacée horizontalement | `_rebuild_cells` estompe la diagonale **par index** (`i == j`) ; avec les ordres lignes/colonnes indépendants (RG070), la cellule « même agent » est à `(rang_ligne(A), rang_colonne(A))` — estompée seulement si les deux rangs sont égaux. Correctif : estomper par **identité d'agent** (`ai == aj`). |
| 2.3 | Lignes/colonnes de la matrice plus épaisses que le reste de la grille | `_MatrixCell.paint` remplit le fond et trace une bordure 1 px `#383838` décalée de 2 px (`_CELL_MARGIN`) par rapport aux lignes de grille (multiples de 100) → double ligne apparente. Les lignes de grille (z=-2) passent sous les cellules (z=0). Correctif : cellule transparente (pas de fond ni de bordure), la grille traverse la matrice. |
| 2.4 | Points centraux uniquement dans la matrice | Le point est peint dans `_MatrixCell.paint` (cellules uniquement). Correctif : points peints dans `drawBackground` de la vue sur **toute la zone visible** (centres des cellules 100 px), comme les points d'ancrage de la vue « Agents ». |
| 2.5 | Ascenseurs de la matrice d'apparence/comportement différents de Journeys | `_MatrixGraphicsView` n'a pas de stylesheet → ascenseurs natifs (clairs). Journeys/Agents appliquent `theme.WORKSPACE_STYLESHEET` (= `SCROLLBAR_STYLESHEET` + fond) + `WA_StyledBackground`. Correctif : idem. |
| 3.1 | Séparateur filtres/liste peu visible | `QFrame` HLine 1 px `border_color` #383838 sur fond #2D2D2D. Correctif : barre pleine 2 px (config `relationships_view_separator_height_px`) en `grid_major_color` #4A4A4A. |
| 3.2 | Marge gris clair à droite du panneau, sur toute la hauteur y compris les filtres | Reproduit offscreen : le `QSplitter` alloue 274 px à la fente du panneau (son `sizeHint`) alors que le panneau est clampé à `setFixedWidth(260)` → **bande de 14 px de fond de splitter (gris clair natif) à droite**, sur toute la hauteur. Ce n'est PAS une place de scrollbar. Correctif : `setSizes` au `resizeEvent` pour caler la fente à 260 (le panneau remplit exactement), handle de splitter stylé sombre, contenu du panneau en thème sombre (`theme`-`DIALOG_STYLESHEET`), et ascenseur vertical de la **liste des blocs** toujours visible (`ScrollBarAlwaysOn`) et stylé façon Journeys — il n'occupe que la zone liste, jamais la zone filtres. |

## Point ouvert (re-conception, hors implémentation TSK31)

La matrice symétrique affiche **2 coches par relation** (cellules (A,B) et (B,A)) — confusion signalée par TSC. Pistes pour la re-conception à venir : n'afficher la coche que dans le **triangle supérieur** (matrice non symétrique visuellement), ou rendre la matrice dirigée, ou revenir à une liste de relations. À trancher en séance de conception (nouvelle note `docs/conception/`), hors scope de TSK31.

## Plan d'implémentation

1. `layout_service.py` : `snap_to_grid(value, grid_size, offset=0)` (offset par défaut 0 — les autres vues ne changent pas).
2. `agent_card.py` : `GRID_OFFSET_X/Y = CELL_WIDTH−WIDTH / CELL_HEIGHT−HEIGHT` (marges = écart entre deux cartes, calculés depuis config) ; `_cell_snap_target` snappe avec offset.
3. `agents_workspace.py` : `next_free_card_position` ancre `find_first_free_cell` sur `(offset_x, offset_y)` ; `create_agent_card` snappe avec offset.
4. `relationships_workspace.py` :
   - 2.1 : `contextMenuEvent` utilise `event.pos()` / `event.globalPos()`;
   - 2.2 : diagonale estompée par `ai == aj` dans `_rebuild_cells`;
   - 2.3 : `_MatrixCell.paint` sans fond ni bordure (transparent), overlay estompé + case à cocher conservés;
   - 2.4 : `_MatrixGraphicsView.drawBackground` peint les points au centre de chaque cellule 100 px de la zone visible (et plus dans `_MatrixCell.paint`);
   - 2.5 : `setStyleSheet(theme.WORKSPACE_STYLESHEET)` + `WA_StyledBackground` sur la vue;
   - 3.1 : séparateur = barre pleine 2 px `grid_major_color` (`relationships_view_separator_height_px`);
   - 3.2 : `self._splitter.setSizes(...)` au `resizeEvent` (fente panneau = 260 exact), stylesheet sombre du splitter/panneau, `block_list` : ascenseur vertical `AlwaysOn`, horizontal `AlwaysOff`.
5. `config.json` : `relationships_view_separator_height_px: 2`.
6. `theme.py` : `SIDE_PANEL_STYLESHEET` (fond `bg_surface` + règles sombres labels/combos/liste/scrollbars, dérivé de `DIALOG_STYLESHEET`).
7. Tests : attentes placement agents décalées de (+40, +40) + test offset de snap ; test diagonale par identité (ordres divergents) ; test `contextMenuEvent` via `QContextMenuEvent` ; test points dans `drawBackground` hors matrice ; test ascenseurs stylés/politiques ; test pas de gap splitter (`splitter.sizes()`); test séparateur 2 px; test ascenseur liste toujours visible. Rendu vérifié par captures d'image offscreen.
8. Docs : fiche TSK31, kanban, `04_interface` §5/§6 FR/EN (marge 1ʳᵉ carte, ascenseurs, points, séparateur), SESSIONS.md.

## Journal

- 2026-11-20 : TSK31 créée et passée en Doing (TSK30 en Review). Analyse des 8 points ci-dessus (diagnostics par rendu offscreen + sondage de pixels + repro isolé du slack QSplitter de 14 px). Point ouvert noté : 2 coches par relation en matrice symétrique → re-conception à part.
- 2026-11-20 : **implémentée** — `layout_service.snap_to_grid(offset=...)`, `agent_card.py` (`GRID_OFFSET_X/Y` = cellule−carte), `agents_workspace.py` (scan ancré sur la marge), `relationships_workspace.py` (2.1 `event.pos()`, 2.2 diagonale par identité, 2.3 cellules transparentes, 2.4 `drawBackground` points partout, 2.5 `WORKSPACE_STYLESHEET`, 3.1 séparateur 2 px, 3.2 `setSizes` + `SIDE_PANEL_STYLESHEET` + ascenseur liste `AlwaysOn`), `theme.py` (`SIDE_PANEL_STYLESHEET`), `config.json` (`relationships_view_separator_height_px`), tests (+6 offscreen TSK31, attentes agents recalées +40/+40, `snap_to_grid` offset), specs 04_interface §5/§6 FR/EN + conception 04 FR/EN. **Vérifications** : py_compile OK, pyflakes clean, **132 tests passed** (+3 pré-existants hors scope) ; rendu vérifié par captures offscreen (lignes matrice = grille partout, points partout, ascenseurs sombres, séparateur 2 px #4A4A4A, gap splitter = 0, cartes agent à (40,40)/(240,40)/(440,40)). Passée en Review. Commit + push `dev`.
