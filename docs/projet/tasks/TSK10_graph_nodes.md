# TSK10 — Nœuds graphiques de la vue « Journeys »

- **Créée** : 2026-11-11 — passée en Doing 2026-11-11 (TSK08/TSK09 en Review)
- **Dépendances** : → #TSK08 (modèle, services, use cases en place)

## Objectif

Reprendre les objets graphiques de planoscript (`ui/nodes/`) adaptés au modèle hyperscript, pour la vue « Journeys » uniquement (la matrice Agents est hors périmètre) :

- `src/ui/nodes/base_node.py` — reprise de plano `base_node.py`, adapté :
  - le nœud affiche le **type** du bloc (Start/Scene/Pivot/Condition/End), plus de libellé tronqué à 8 caractères (décision séance 03) ;
  - infobulle au survol = **libellé + note** (RG054 + décision séance 03) ;
  - bordure colorée par type via `theme.block_color(typ)` (code couleur acté séance 03 : Start #E5C07B, Scene #A7C957, Pivot #D19A66, Condition #E06666, End #F0F0F0) ;
  - conservés de plano : ports entrant/sortant (8 px, `journeys_view_port_size_px`), snap sur la grille au déplacement (RG046 via `LayoutService.snap_to_grid`), hit-testing par `shape()` élargie (RG053), sélection (RG049), infobulle immédiate `QToolTip.showText` dans `hoverEnterEvent`, `itemChange` (sélection + position + observateurs).
- `src/ui/nodes/block_node.py` — **fusion** de plano `state_node.py` + `event_node.py` en un seul nœud `BlockNode(TypedNode)` :
  - badge de participations conservé tel quel de plano (décision séance 03) : coin inférieur droit, 2/3 dedans / 1/3 dehors, Ø `journeys_view_badge_diameter_px` (16 px), remplissage fixe `badge_bg_color` #E5C07B, bordure `badge_border_color`, texte `badge_text_color`, masqué à 0, « 9+ », non cliquable, ligne « Agents: … » dans l'infobulle via `ParticipationBadgeService` (TSK08) ; `refresh_participation_badge(count, agent_labels)` ;
  - **pas** de badge « événements/transitions » en vue Journeys (plano ne l'avait qu'en vue Agents).
- `src/ui/nodes/connection.py` — reprise de plano `connection.py`, adapté :
  - entité `Transition` (ports source droite → cible gauche), flèche 2 px `connection_color`, suit les déplacements des blocs, non déplaçable, routage évitant les blocs étrangers (RG052), hit-testing par `shape()` (RG053), infobulle note au survol (RG054) ;
  - **supprimés** : `create_arc_or_association` / `delete_arc_or_association` (écriture directe du modèle depuis l'UI — interdit RG058, bug plano `connection.py:811`) ; toute modification passe par les use cases TSK08.
- `src/ui/nodes/__init__.py` : exports.

- **Références** : 04_interface §4 ; RG045–RG055 ; FN014–FN022 ; conception §4 ; décisions séance 03 (couleurs, type affiché, badge).

## Points actés à prendre en compte

- Code couleur par type en config (`block_*_color`) — valeurs à confirmer après tests visuels, mêmes teintes.
- Type affiché dans le nœud ; libellé + note en infobulle ; troncature à 8 caractères supprimée.
- Badge sur **tous** les blocs (pas seulement certains types comme plano), remplissage fixe #E5C07B.
- AGENTS.md patterns à conserver : hit-testing `shape()` + `boundingRect()` élargi ; infobulle immédiate dans `hoverEnterEvent` (le workspace avale l'événement ToolTip automatique) ; feedback de sélection via `itemChange(ItemSelectedChange)` → `set_selected_appearance`.
- Aucune valeur en dur : dimensions/couleurs via `config.json` (RG059).

## Hors périmètre TSK10

Workspace (TSK11), tab bar (TSK11), dialogues (TSK12), `matrix_card.py` (vue Agents, hors MVP des vues).

## Vérifications (sandbox : pas de libGL → pas d'instanciation Qt)

- `python -m py_compile` sur tous les fichiers : OK.
- Revue statique des imports (PySide6 uniquement dans `src/ui/`).
- Tests offscreen Qt à valider sur poste de dev (TSK13).

## Journal

- 2026-11-11 : fiche rédigée au passage en Doing.
