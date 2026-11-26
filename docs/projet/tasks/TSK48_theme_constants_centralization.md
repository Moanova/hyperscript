# TSK48 — Centralisation des constantes visuelles dans theme.py (plan TSK43, point 5)

- **Statut** : Review (26-11-2026) ; implémentée et pushée sur `dev` sur feu vert TSC séance 12.
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
- 2026-11-26 : **passée en Doing puis implémentée et passée en Review** (feu vert TSC) — `theme.py` : ajout de `LINK_COLOR`, `GRID_MINOR_COLOR`, `GRID_MAJOR_COLOR` (avec les mêmes défauts qu'avant). Remplacements : `_BG_PRIMARY` → `theme.BG_PRIMARY` (`base_workspace.py`, `relationships_workspace.py` ; définitions supprimées aussi dans `agents_workspace.py`/`journeys_workspace.py` où elles étaient devenues mortes après TSK47), `_GRID_MINOR_COLOR`/`_GRID_MAJOR_COLOR` → `theme.GRID_*` (`journeys_workspace.py`, `relationships_workspace.py`, `filters_side_panel.py`), `_BORDER_COLOR` → `theme.BORDER_COLOR` (`filters_side_panel.py` ; def morte supprimée dans `relationships_workspace.py`), `_BG_SURFACE` → `theme.BG_SURFACE`, `_TEXT_SECONDARY` → `theme.TEXT_SECONDARY` (`filters_side_panel.py`), `_LINK_COLOR` → `theme.LINK_COLOR` (`preview_workspace.py`). Constantes mono-fichier laissées en local (`_DOT_*`, `_CELL_*`, `_GRID_*_SIZE`, `_TEMP_CONNECTION_COLOR`, `_CELL_HIT_WIDTH`, libellés `_ALL_*_LABEL`). Imports `_get_config`/`theme` devenus inutilisés supprimés (`preview_workspace.py`, `agents_workspace.py`). Aucun test ne référençait ces constantes. Vérifications : py_compile OK, **pyflakes 0 warning sur `src/`**, suite **200 passed + 3 pré-existants hors scope** (identiques à `936feb9`). Commit+push `dev` effectués (feu vert TSC).
