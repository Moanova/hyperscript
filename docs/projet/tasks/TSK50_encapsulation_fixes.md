# TSK50 — Corrections d'encapsulation (plan TSK43, point 7)

- **Statut** : Review (26-11-2026) ; implémentée et pushée sur `dev` sur feu vert TSC séance 12.
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
- 2026-11-26 : **passée en Doing puis implémentée et passée en Review** (feu vert TSC) — (1) `LayoutService._rects_overlap` renommé `rects_overlap` (public) : def + 4 appels internes `cls.` + appel externe `journeys_workspace.py:508` mis à jour. (2) `RelationshipsWorkspace` : nouvelle propriété publique `splitter` ; `main_window.py:724,959` migrés ; 5 usages tests migrés (`mw.relationships_workspace.splitter`, `ws.splitter`) ; l'attribut `_splitter` reste (interne). (3) `FiltersSidePanel._set_anchor_block_silent` → `set_anchor_block_silent` (public), appel `relationships_workspace.py:329` mis à jour. (4) `line._is_grid_line` : **laissé tel quel** — usage strictement intra-module (`_GridLineItem` défini dans `relationships_workspace.py`) + introspection de tests ; pas une fuite cross-classe. Vérifications : py_compile OK, **pyflakes 0 warning sur `src/`**, 0 accès privé cross-classe restant (grep), suite **200 passed + 3 pré-existants hors scope** (identiques à `cc537c1`). Commit+push `dev` effectués (feu vert TSC).
