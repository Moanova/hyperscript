# Conception — Matrice « Relationships » (agent × agent), rapprochement du modèle planoscript

- **Date** : 2026-11-19 (séance 09, TSK29)
- **Contexte** : la vue « Relationships » (TSK27) utilisait un `QTableWidget` read-only avec en-têtes movable natifs et un ordre partagé lignes/colonnes. TSC souhaite se rapprocher de la matrice Agent × State de planoscript (figé `faa8fdd` : `src/ui/views/agents_workspace.py` + `src/ui/nodes/matrix_card.py`), avec des adaptations actées.

## Références planoscript (figé faa8fdd)

- Scène custom : `AgentsWorkspace(QWidget)` + `_MatrixGraphicsView(QGraphicsView)` ; cellules 120×80 (`agents_view_cell_width/height`) ; en-têtes = cartes (`MatrixCardItem` 80×40) : states en 1ʳᵉ ligne (colonnes), agents en 1ʳᵉ colonne (lignes) ; cases à cocher (`MatrixCheckItem`) centrées aux intersections ; grille en fond, zone visible, lignes non interactives.
- Réordonnancement : drag de la carte d'en-tête **contraint à son axe** ; à la libération, cible arrondie, `pop`/`insert`, `_persist_visual_order()`, `_relayout()` complet.
- Ordre : `resolve_matrix_order(entities, saved_order, pinned_first_id)` (Qt-free) ; persistance `agents_view_row_order`/`column_order` dans le `WorkspaceLayout` (par carte narrative chez plano).

## Décisions actées (TSC, séance 09)

1. **Lignes et colonnes indépendantes** (comme plano) : deux ordres persistés séparés — `relationships_view_row_order` et `relationships_view_column_order` dans `ProjectLayout` (niveau projet, RG067 — les agents sont niveau projet RG057, contrairement à plano). **RG070 révisée** en conséquence.
2. **Cellules carrées** : `relationships_view_cell_size_px` = **100** (cellule 100×100). Cartes agent 80×40 centrées → 10 px de chaque côté, soit **20 px entre cartes adjacentes en horizontal** (vérifié), 60 px en vertical.
3. **Cartes agent au rendu des blocs narratifs** : 80×40 (`node_default_width/height`), coins `node_corner_radius_px`, bordure **sable** `block_scene_color` (cohérence vue « Agents », RG066), libellé tronqué + infobulle (RG054), hit-testing `shape()` (RG053). Objet technique distinct de `BlockNode` (pas de ports) : `MatrixAgentCard` (QGraphicsRectItem custom).
4. **Cellule cliquable** (pas de coche) : clic gauche sur la cellule (A, B) → dialogue de **création** (paire A-B + bloc courant pré-remplis) si aucune relation, ou d'**édition** de la relation existante (état dérivé au bloc sélectionné) ; clic droit → menu contextuel (`Project › Relationships` + « View in Journeys view »). Plano utilisait une case à cocher (association binaire oui/non) — inadapté ici car une relation est typée + ancrée (choix type/ancre nécessaires).
5. **Ordre initial conservé** : alphabétique (libellé, repli id) — RG070 inchangé sur ce point (plano utilisait l'id croissant).
6. **Persistance au niveau projet** : oui (ProjectLayout, `layouts/project.json`).
7. **Tests offscreen re-rédigés** : oui.

## Maquette géométrique (TSK29)

- Scène : cellules carrées C=100 ; zone des cellules décalée de C en x et y (`_CELLS_LEFT = _CELLS_TOP = C`) ; cartes colonne en haut (y = (C−40)/2 = 30, x = C + col·C + 10) ; cartes ligne à gauche (x = 10, y = C + row·C + 30) ; cellule (row, col) = rect (C + col·C, C + row·C, C, C).
- Grille : lignes espacées de C, zone visible uniquement, z = -2, couleurs `grid_minor_color`/`grid_major_color`, non interactives.
- Cellule : fond `relationship_type_colors[typ]` (repli `block_scene_color`), texte = type centré, infobulle = note ; vide = fond discret ; diagonale désactivée ; hors filtre = estompé (`journey_filter_opacity`) + non cliquable.
- Drag : carte d'en-tête contrainte à son axe pendant le drag ; libération → cible = `round((pos − C − offset)/C)`, clamp, `pop`/`insert`, persistance des deux ordres (signaux), relayout complet.
- Ordre initial/résolution : `resolve_axis_order(agents, saved_order)` Qt-free (dans `relationship_service.py`) : ordre sauvegardé (ids valides) puis manquants par (libellé, id).

## Écarts volontaires vs planoscript

- Persistance au niveau **projet** (pas par carte narrative) — RG057/RG067.
- Cellule = indicateur cliquable (type + couleur), pas de case à cocher — RG035 (typée + ancrée).
- Ordre initial alphabétique (pas id croissant).
- Panneau latéral (filtres + liste des blocs, 3ᵉ dimension) conservé — propre à hyperscript.

## Révision TSK30 (séance 10, retours de test TSC)

- **Ancrage haut gauche + défilement** : alignement `AlignLeft|AlignTop` de la vue, scène d'au moins 4000×4000 ancrée sur (0, 0) et croissant uniquement vers la droite/le bas ; barres de défilement toujours visibles ; la grille couvre **toute la zone visible** (lignes `_GridLineItem` non interactives — `shape()` vide mais `boundingRect()` réelle — redessinées au scroll et au resize). La fenêtre reste réductible (pas de minimum relevé par la vue).
- **Cellule = case à cocher** (retour au modèle plano, remplace la décision 4 de la séance 09) : contour centré (`relationships_view_checkbox_size`/`relationships_view_checkbox_color`) + **cercle de fond plein or** (`relationships_view_check_color`) quand la paire a une relation ; **point au centre de chaque cellule** (rendu des points d'ancrage de la vue « Agents ») ; le **type + la note figurent en infobulle** au survol. Clic gauche : cellule vide → **création directe « Undefined »** (paire + bloc courant, sans dialogue), cellule remplie → dialogue d'édition ; clic droit → menu contextuel (inchangé, RG055).
- **Correctifs** : infobulle des cartes d'en-tête sans 3ᵉ argument `QWidget` (`QToolTip.showText(pos, texte)`, l'item n'est pas un widget) + `hideText` au `hoverLeaveEvent` ; hit-testing des cartes/cellules en coordonnées locales (`mapFromScene` avant `shape().contains`) — le drag lignes/colonnes et les clics de cellule refonctionnent.
- **Panneau latéral** : séparateur horizontal après le filtre agent ; la combo de parcours émet l'id choisi (`None` = « All journeys ») et le `MainWindow` **active ce parcours** (FN026) + filtre (FN029), comme « Display > Journey » ; resync du panneau après chaque CRUD de parcours.
- **Hors matrice** : vue active par défaut « Agents » à la création/ouverture d'un projet (révise TSK28) ; vue « Agents » : création sur la première cellule libre depuis (0, 0) en balayage ligne par ligne, espace extensible droite/bas uniquement (scène clampée à 0 en gauche/haut).
