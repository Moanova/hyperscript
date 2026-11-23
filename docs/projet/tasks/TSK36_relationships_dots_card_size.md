# TSK36 — Vue « Relationships » : champ de points façon « Agents » + carte Relationship à la taille des cartes Agent

- **Statut** : **Validée TSC et passée en Done 23-11-2026** (option 1 carte validée, option 2 points retenue) ; dépend de #TSK32 (Done), #TSK35 (Done).
- **Origine** : retours TSC séance 11 après test de TSK35 — deux points de la vue « Relationships » à revalider : (1) le point au centre de chaque cellule (TSK31 2.4) donne « un effet bizarre » à l'usage ; (2) la carte Relationship (84×72) est carrée alors que les cartes Agent de la matrice sont rectangulaires (80×40).

## Options proposées par TSC (séance 11)

- **Points** : 1. champ de points en fond selon le même écartement que la vue « Agents » (`agents_view_dot_spacing_px`) ; 2. supprimer complètement les points.
- **Carte** : 1. redimensionner à l'identique des cartes Agent ; 2. carrés plus réduits alignés sur la hauteur des cartes Agent.

**Feu vert TSC pour l'option 1 dans les deux cas** (à valider à l'usage ; l'option 2 reste en repli si le rendu ne convient pas).

## Validation TSC (séance 11, 23-11-2026)

- **Carte** : option 1 **validée** — la carte Relationship reste à 80×40, identique aux cartes Agent de la matrice.
- **Points** : option 1 (champ de points façon « Agents ») jugée « un peu bizarre » → **option 2 retenue et implémentée** : plus aucun point en fond.

## Conception actée (séance 11, option 1)

1. **Points** : `RelationshipsView.drawBackground` peint un **champ de points sur toute la zone visible** à l'espacement `agents_view_dot_spacing_px` (20), même rendu que la vue « Agents » (`agents_view_dot_radius_px`/`agents_view_dot_color`) — même pattern que `agents_workspace.drawBackground`. Le point au centre de chaque cellule (TSK31 2.4) est supprimé. Les lignes de la grille (100 px) restent inchangées.
2. **Carte** : `MatrixRelationshipCard.WIDTH/HEIGHT` = `node_default_width`/`node_default_height` (80×40), **identiques aux cartes d'en-tête `MatrixAgentCard`** ; la carte reste centrée dans sa cellule (`_REL_CARD_W/H` suivent la classe). Clés config `relationships_view_card_width_px`/`height_px` supprimées (plus utilisées).

## Plan d'implémentation

1. `src/ui/views/relationships_workspace.py` : `_DOT_SPACING = agents_view_dot_spacing_px`, boucle `drawBackground` façon vue « Agents » ; docstring.
2. `src/ui/nodes/matrix_relationship_card.py` : `WIDTH/HEIGHT` depuis `node_default_*`.
3. `src/config/config.json` : suppression des 2 clés obsolètes.
4. Tests : `test_dots_painted_with_agents_view_spacing_over_the_whole_visible_area` (pixel : points aux multiples de 20, plus de point au centre de cellule) ; `test_relationship_card_same_size_as_matrix_agent_card` (taille = `MatrixAgentCard`, centrage dans la cellule).
5. Docs : `04_interface` §6 FR/EN, conception 04 FR/EN, kanban, SESSIONS.md.

## Journal

- 2026-11-23 (validation TSC partielle + rework) : carte option 1 **validée** (80×40 conservé) ; points option 1 rejetée → **option 2 implémentée** : suppression du `drawBackground` à points et des constantes `_DOT_SPACING/_DOT_RADIUS/_DOT_COLOR` dans `relationships_workspace.py` (le fond reste `bg_primary` via le background brush, les lignes de grille `_GridLineItem` restent) ; test remané `test_no_dots_in_background_only_grid_lines` (pixels : aucun point, fond `bg_primary`, grille présente), test carte 80×40 conservé ; specs `04_interface` §6 + conception 04 FR/EN. **Vérifications** : py_compile OK ; **152 tests passed + 4 failed pré-existants** (reproductibles arbre propre). Repassée en **Review**. Pas de commit/push (non demandé).
- 2026-11-23 : TSK36 créée et passée en Doing (feu vert TSC = option 1 des deux chantiers) ; fiche initialisée. Implémentation lancée.
- 2026-11-23 : **implémentée** — `relationships_workspace.py` (champ de points `drawBackground` à l'espacement `agents_view_dot_spacing_px`), `matrix_relationship_card.py` (80×40 = `node_default_*`, identique aux cartes Agent), `config.json` (clés `relationships_view_card_width/height_px` supprimées), tests offscreen (+2 nouveaux, 1 remané), specs `04_interface` §6 + conception 04 FR/EN. **Vérifications** : py_compile OK ; config JSON valide ; **152 tests passed + 4 failed pré-existants** (3 `test_block_drag_offscreen.py` + 1 rendu couleur, reproductibles sur l'arbre propre dans ce sandbox) ; nouveaux tests TSK36 OK (points aux multiples de 20 px et plus au centre des cellules, carte 80×40 centrée). Passée en **Review**. Pas de commit/push (non demandé).
