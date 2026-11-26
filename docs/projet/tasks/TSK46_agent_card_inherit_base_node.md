# TSK46 — AgentCardItem hérite de BaseNode (plan TSK43, point 3)

- **Statut** : To do (26-11-2026).
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
