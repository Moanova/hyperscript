# TSK50 — Corrections d'encapsulation (plan TSK43, point 7)

- **Statut** : To do (26-11-2026).
- **Origine** : demande TSC séance 12 — plan de refactorisation TSK43, point 7 (fiche `TSK43_code_review_technical_debt.md`).
- **Dépendances** : → #TSK44.

## Périmètre (constats TSK43)

Accès à des membres privés depuis d'autres classes :
- `LayoutService._rects_overlap(...)` appelé depuis `ui/views/journeys_workspace.py:627` ;
- `relationships_workspace._splitter` accédé depuis `ui/main_window.py:724,959` ;
- `panel._set_anchor_block_silent(...)` appelé depuis `ui/views/relationships_workspace.py:335` ;
- `line._is_grid_line = True` depuis `relationships_workspace.py:537,544` (même module, `_GridLineItem` interne — à valider).

## Plan d'implémentation

1. `LayoutService` : renommer `_rects_overlap` en `rects_overlap` (public) ou ajouter un wrapper public ; mettre à jour l'appel.
2. `RelationshipsWorkspace` : exposer le splitter via une propriété publique (ex. `splitter`) ; mettre à jour `main_window.py`.
3. `FiltersSidePanel` : renommer `_set_anchor_block_silent` en méthode publique (ex. `set_anchor_block_silent`) ; mettre à jour l'appel.
4. `_is_grid_line` : décider (flag interne au module) — le laisser si interne à `relationships_workspace.py`, sinon propriété.
5. Vérifications : py_compile, pyflakes sans nouveau warning, suite complète (201 passed + 3 pré-existants). Aucun changement de comportement.
6. Kanban → Review après tests. Commit+push sur `dev` uniquement sur demande explicite TSC.

## Journal

- 2026-11-26 : créée en To do (plan TSK43 point 7, demande TSC séance 12).
