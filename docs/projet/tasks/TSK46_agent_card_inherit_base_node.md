# TSK46 — AgentCardItem hérite de BaseNode (plan TSK43, point 3)

- **Statut** : Review (26-11-2026) ; implémentée et pushée sur `dev` sur feu vert TSC séance 12.
- **Origine** : demande TSC séance 12 — plan de refactorisation TSK43, point 3 (fiche `TSK43_code_review_technical_debt.md`).
- **Dépendances** : → #TSK44 (suppression des méthodes mortes de `base_node.py` d'abord).

## Périmètre (constats TSK43)

`ui/nodes/agent_card.py:50` : `AgentCardItem(QGraphicsRectItem)` duplique `BaseNode` au lieu d'en hériter — corps identiques : `update_layout` (171 vs `base_node.py:261`), `_rounded_path` (206 vs 331), `paint` (220 vs 345), `hoverEnterEvent` (279 vs 393), `hoverLeaveEvent` (290 vs 410).

## Plan d'implémentation

1. Faire hériter `AgentCardItem` de `BaseNode` (comme `BlockNode` → `TypedNode` → `BaseNode`) ou extraire une base commune `QGraphicsRectItem` ; supprimer les 5 méthodes dupliquées, ne garder que le spécifique (accents sable, label agent, observateurs de position déjà sur `BaseNode`).
2. Vérifier le rendu offscreen (capture) : carte agent identique à l'actuel.
3. Vérifications : py_compile, pyflakes sans nouveau warning, tests offscreen agents (`agents_workspace`, drag, sélection), suite complète (201 passed + 3 pré-existants).
4. Kanban → Review après tests. Commit+push sur `dev` uniquement sur demande explicite TSC.

## Journal

- 2026-11-26 : créée en To do (plan TSK43 point 3, demande TSC séance 12).
- 2026-11-26 : **passée en Doing puis implémentée et passée en Review** (feu vert TSC) — `AgentCardItem(BaseNode)` : hérités `update_layout`, `_rounded_path`, `boundingRect`, `shape`, `paint`, `mousePressEvent`, `mouseMoveEvent`, `hoverEnterEvent`, `hoverLeaveEvent`, `_apply_outline`, `set_selected_appearance`, `register/unregister/_notify_position_observers` ; surcharges conservées : `_init_label`/`_position_label` (deux textes label_item + type_item, label BaseNode réutilisé comme label_item), `_init_ports` (None, RG066), `_type_border_color` (bordure sable), `update_entity_data`, `mouseReleaseEvent` (snap cellule RG065, en bypassant `BaseNode.mouseReleaseEvent` via `QGraphicsRectItem.mouseReleaseEvent`), `_cell_snap_target`, `itemChange` (z-value 1.0/0.0 sur sélection uniquement ; le clamp de position vient de `BaseNode.itemChange`). `DEFAULT_WIDTH/HEIGHT = WIDTH/HEIGHT` pour le fallback de `BaseNode.__init__`. `base_node.py` : `self.layout.color` → `getattr(self.layout, "color", None)` (`AgentCardLayout` n'a pas `color`) + docstring à jour. Constantes publiques conservées (`WIDTH`, `CELL_WIDTH`, `GRID_OFFSET_X`… utilisées par les tests). Vérifications : py_compile OK, **pyflakes 0 warning sur `src/`**, scan AST **0 groupe de corps dupliqué** entre agent_card/base_node/block_node, suite **200 passed + 3 pré-existants hors scope** (identiques à `9168291`). Diff : +50/−189. Commit+push `dev` effectués (feu vert TSC).
