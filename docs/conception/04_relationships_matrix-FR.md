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

## Révision TSK31 (séance 10, 2ᵉ salve de retours)

- **2.1** : `contextMenuEvent` utilise `event.pos()`/`globalPos()` (`QContextMenuEvent` n'a pas `position()` dans toutes les versions Qt6) — plus d'exception au clic droit.
- **2.2** : la diagonale estompée est repérée par **identité d'agent** (`ai == aj`), pas par index — avec les ordres indépendants (RG070), la cellule « même agent » suit la carte déplacée.
- **2.3** : cellules transparentes (plus de fond/bordure propre) → les lignes de la matrice sont celles de la grille de fond, partout identiques.
- **2.4** : point au centre de **chaque cellule de tout l'espace visible**, peint dans `drawBackground` de la vue (rendu points d'ancrage vue « Agents »).
- **2.5** : la vue applique `theme.WORKSPACE_STYLESHEET` + `WA_StyledBackground` → ascenseurs identiques à la vue « Journeys » (toujours visibles, sombres, fins).
- **3.1** : séparateur = barre pleine 2 px (`relationships_view_separator_height_px`) en `grid_major_color`.
- **3.2** : fente du splitter calée sur la largeur du panneau au resize (`setSizes`) → plus de bande grise à droite du panneau ; panneau en thème sombre (`theme.SIDE_PANEL_STYLESHEET`) ; ascenseur vertical de la liste des blocs toujours visible et stylé façon Journeys, zone liste uniquement.
- Hors vue : vue « Agents » — marge de la 1ʳᵉ carte = écart entre deux cartes (40 px), grille invisible décalée d'autant (`snap_to_grid` offset).

## Révision TSK32 (séance 10) — matrice triangle supérieur + carte Relationship dans la case

- **Problème acté** : la matrice symétrique affichait **2 coches par relation** (cases (i,j) et (j,i)) — confusion pour l'utilisateur. Question combinatoire tranchée : RG035 borne les relations affichées à N(N−1)/2 pour N agents (unicité (bloc, paire) + état dérivé au bloc sélectionné, RG069) ; la matrice absorbe donc la combinatoire, sa taille ne dépendant que de N.
- **Variante retenue** (parmi : 3 colonnes bipartite agents|liens|cartes Relationship, matrice triangle supérieur, hybride) : **matrice triangle supérieur** — lignes et colonnes = mêmes agents, **un seul ordre partagé** (`relationships_view_agent_order`, migration depuis `row_order`/`column_order`), diagonale neutralisée, triangle inférieur vide/estompé/non interactif → **une seule case active par paire** (i < j). Le drag d'une carte d'en-tête réordonne ligne ET colonne simultanément.
- **Carte Relationship dans la case** : `MatrixRelationshipCard` (`relationships_view_card_width/height_px` = 84×72 dans la cellule de 100 px), bordure `relationships_view_card_border_color` #E06666 (couleur Pivot/Condition), libellé = type, infobulle = type + paire + bloc d'ancrage + note (RG054). Au plus une carte par case (RG069 + RG035). Position dérivée de la case, jamais persistée.
- **Interactions** : **plus de clic gauche dans les cases** (création « Undefined » de TSK30 abandonnée) ; **clic droit uniquement** → menu contextuel RG055 (case vide → « New... » pré-rempli paire + bloc courant ; case remplie → Edit/Delete de la relation + « View in Journeys view » FN032) ; menu aussi actif sur les **cartes d'agent** (`agent_context_menu_requested` : « New Relationship... » pré-rempli + Edit/Delete des relations de l'agent).
- **Implémentation** : `relationships_workspace.py` v4 (ordre unique `_order`, cases actives i < j, carte enfant de la case), `ui/nodes/matrix_relationship_card.py` (nouveau), `ProjectLayout.relationships_view_agent_order` (+ migration), `main_window.py` (`_show_relationships_context_menu` retravaillé, `_show_relationships_agent_context_menu`, helpers `_new_relationship_prefilled`/`_edit_relationship_entity`/`_delete_relationship_entity`), config (clés `relationships_view_card_*`, clés `relationships_view_checkbox_*`/`check_color` supprimées), RG070 révisée, `04_interface` §6 réécrite, tests offscreen remaniés.
- **Post-MVP** : si RG035 est levée (plusieurs relations par paire), empiler plusieurs cartes dans la case.
