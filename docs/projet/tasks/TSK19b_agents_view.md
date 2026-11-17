# TSK19b — Vue « Agents » re-conçue : points d'ancrage + cartes agent (RG065/RG066/RG067)

- **Créée** : 2026-11-17 — en To do (passera en Doing quand TSK19a sera en Review/Done)
- **Dépendances** : → #TSK11, → #TSK17, → #TSK18

## Objectif

Remplacer le placeholder de l'onglet « Agents » par un espace de travail dédié, re-conçu séance 04 (SU009) — **la matrice agents × blocs de planoscript n'est pas reprise** :

- fond `bg_primary` **identique à la vue « Journeys »**, mais habillé de **points d'ancrage** à la place d'une grille (espacement `agents_view_dot_spacing_px`, rayon `agents_view_dot_radius_px`, couleur `agents_view_dot_color` ; dessinés sur la zone visible uniquement, dans `drawBackground` — pas d'items, donc pas de piège de z-order) (RG065) ;
- chaque agent du projet = une **carte** `AgentCardItem` (`agents_view_card_width`×`agents_view_card_height` = 160×100, plus grande qu'un bloc 80×40, **sans ports**), affichant libellé + type, note en infobulle au survol (RG054), **sans badge de comptage** (participations/relations traitées dans d'autres vues, RG066) ;
- cartes déplaçables librement, position **toujours forcée sur le point d'ancrage le plus proche** (`LayoutService.snap_to_grid(value, grid_size=dot_spacing)`) (RG065) ; sélection unique (RG049) ; hit-testing `shape()` (RG053) ; infobulles immédiates (RG054) ;
- menu contextuel carte aligné sur le menu applicatif (RG055) : Edit.../Copy/Delete.../Associate with Block... (handlers TSK18 réutilisés) ;
- entrée « Associate agents... » ajoutée au **menu contextuel de bloc** dans la vue « Journeys » (FN030) → réutilise `_open_association_dialog(block)` (TSK18) ;
- **filtres (parcours/agent) non appliqués à cette vue** (RG048/RG063) ;
- positions des cartes persistées **au niveau projet** : nouveau `ProjectLayout` (`agent_cards: {agent_id: {x, y}}`) dans `view_model.py`, sauvegardé/chargé via `LayoutService.save_project_layout/load_project_layout` dans `{projet}/layouts/project.json` — **structure conforme au modèle métier** (agents = niveau projet, distinct des layouts par carte) (RG067). Au chargement : cartes recréées depuis `project.agent`, positions reprises du layout ou placement libre (`find_non_overlapping_position` sur la trame de points).

## Plan d'implémentation

1. `src/core/models/view_model.py` : `AgentCardLayout` (agent_id, x, y, w, h) + `ProjectLayout` (agent_cards dict, to_dict/from_dict).
2. `src/core/services/layout_service.py` : `save_project_layout(project_filepath, layout)` / `load_project_layout(project_filepath)` → fichier `layouts/project.json` (niveau projet, RG067) ; `snap_to_grid(value, grid_size)` réutilisé pour le snap sur points.
3. `src/ui/nodes/agent_card.py` : `AgentCardItem(QGraphicsRectItem)` — rectangle arrondi (rayon `node_corner_radius_px`), libellé + type (QGraphicsTextItem), couleurs thème ; `shape()` élargie (RG053) ; sélection unique + `set_selected_appearance` (pattern BaseNode, tirets `node_selection_dash_pattern`) ; `itemChange(ItemPositionChange)` : snap sur point + contraintes scène + expansion 4 directions ; `hoverEnterEvent` infobulle immédiate (note) + swalling ToolTip côté vue ; **aucun port** ; déplaçable.
4. `src/ui/views/agents_workspace.py` : `AgentsWorkspace(QGraphicsView)` — fond `bg_primary`, `drawBackground` dessine les points sur la zone visible, scène 4000×4000 extensible 4 directions, scrollbars toujours visibles, populate depuis `project.agent` + positions layout, `collect_project_layout()`, signaux vers MainWindow pour menus contextuels (RG058/RG055) et modifications (RG060 persistance au save).
5. `src/ui/main_window.py` : remplacer le placeholder « Agents » par `AgentsWorkspace` ; au save : `save_project_layout` ; à l'ouverture : `load_project_layout` + populate ; context menus (carte agent → agents_edit/copy/delete/associate handlers TSK18 avec l'agent de la carte ; grille vide → agents_new) ; onglet « Agents » : aucun filtre appliqué ; menu contextuel de bloc « Associate agents... » dans la vue Journeys (FN030) ; `_update_menu_state` inchangé côté filtres.
6. Tests : unitaires sur `ProjectLayout` (sérialisation) et le snap sur points ; `pytest` ; smoke offscreen (poste de dev) : rendu QImage de la vue (points, cartes), déplacement snappé, persistance save/reopen, menu contextuel.
7. Specs déjà à jour (séance 04) : `04_interface` §5, SU009, RG065–RG067, RG048, FN030, matrices. À compléter : statuts + références après implémentation.

## Hors périmètre

Filtre agent (TSK19a) ; relations (TSK20) ; vue « Relationships » ; badge de comptage (supprimé par décision TSC).

## Journal

- 2026-11-17 : fiche créée avec le plan ; tâche en To do (dépendances TSK11 Done, TSK17/TSK18 en Review).
