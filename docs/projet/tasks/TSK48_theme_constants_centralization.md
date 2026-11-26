# TSK48 — Centralisation des constantes visuelles dans theme.py (plan TSK43, point 5)

- **Statut** : To do (26-11-2026).
- **Origine** : demande TSC séance 12 — plan de refactorisation TSK43, point 5 (fiche `TSK43_code_review_technical_debt.md`).
- **Dépendances** : → #TSK44.

## Périmètre (constats TSK43)

Constantes adossées à `config.json` redéfinies en 3 endroits : `_GRID_MINOR_COLOR`/`_GRID_MAJOR_COLOR` dans `ui/views/journeys_workspace.py:47-48`, `ui/views/relationships_workspace.py:120-121`, `ui/widgets/filters_side_panel.py:52`.

## Plan d'implémentation

1. Déplacer ces constantes (et toute constante de couleur/geometry équivalente dispersée) dans `ui/utils/theme.py` comme constantes publiques (`GRID_MINOR_COLOR`, …) lues via `_get_config`.
2. Remplacer les références dans les 3 fichiers par `theme.GRID_MINOR_COLOR` etc.
3. Vérifications : py_compile, pyflakes sans nouveau warning, rendu offscreen (grille, panneau) inchangé, suite complète (201 passed + 3 pré-existants).
4. Kanban → Review après tests. Commit+push sur `dev` uniquement sur demande explicite TSC.

## Journal

- 2026-11-26 : créée en To do (plan TSK43 point 5, demande TSC séance 12).
