# TSK52 — Structure : éclater main_window.py (plan TSK43, point 9, post-MVP)

- **Statut** : To do (26-11-2026) — **post-MVP**.
- **Origine** : demande TSC séance 12 — plan de refactorisation TSK43, point 9 (fiche `TSK43_code_review_technical_debt.md`).
- **Dépendances** : → #TSK51 (et tout le plan TSK43) ; à lancer après le MVP.

## Périmètre (constats TSK43)

- `src/ui/main_window.py` = **1 616 lignes** (god object) : construction des menus, handlers par domaine (projet/agents/blocs/transitions/parcours/relations/participations/vues), états de menu, filtres.
- `core/models/view_model.py` = état de vue (layouts) placé dans `core/models` (Qt-free, conforme, mais conceptuellement couche vue).
- Autres gros fichiers : `layout_service.py` 842, `journeys_workspace.py` 817, `connection.py` 731, `relationships_workspace.py` 670.

## Plan d'implémentation (à affiner en conception le moment venu)

1. Extraire la construction des menus dans un module dédié (ex. `ui/menu_builder.py`) ; les handlers par domaine en mixins ou modules (`ui/handlers/*.py`) ; `MainWindow` n'orchestre plus.
2. Décider du placement de `view_model.py` (ex. `ui/view_model.py` ou package `viewmodel/`) — core reste Qt-free et sans état de vue.
3. Optionnel : scinder `layout_service.py` (persistance vs calcul de positions).
4. Conception préalable requise (diagramme de découpage proposé à TSC) avant toute implémentation.
5. Vérifications : py_compile, pyflakes, suite complète (201 passed + 3 pré-existants), smoke offscreen.
6. Kanban → Review après tests. Commit+push sur `dev` uniquement sur demande explicite TSC.

## Journal

- 2026-11-26 : créée en To do (plan TSK43 point 9, demande TSC séance 12) — post-MVP.
