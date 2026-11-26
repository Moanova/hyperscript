# TSK47 — Classe de base des workspaces graphiques (plan TSK43, point 4)

- **Statut** : To do (26-11-2026).
- **Origine** : demande TSC séance 12 — plan de refactorisation TSK43, point 4 (fiche `TSK43_code_review_technical_debt.md`).
- **Dépendances** : → #TSK44.

## Périmètre (constats TSK43)

`AgentsWorkspace` et `JourneysWorkspace` sont toutes deux `QGraphicsView, QObject` sans base commune et dupliquent : `ensure_visible` (`agents_workspace.py:187` vs `journeys_workspace.py:226`), `add_item_at` (194 vs 233), `viewportEvent` (228 vs 275).

## Plan d'implémentation

1. Extraire `BaseGraphicsWorkspace(QGraphicsView, QObject)` dans `ui/views/` (ex. `base_workspace.py`) avec `ensure_visible`, `add_item_at`, `viewportEvent` et les attributs communs (scène, grille) ; faire hériter `AgentsWorkspace` et `JourneysWorkspace`.
2. Ne déplacer que le code strictement identique ; le spécifique reste dans chaque workspace.
3. Vérifications : py_compile, pyflakes sans nouveau warning, tests offscreen des deux vues (grille au premier affichage TSK34, drag, filtres), suite complète (201 passed + 3 pré-existants).
4. Kanban → Review après tests. Commit+push sur `dev` uniquement sur demande explicite TSC.

## Journal

- 2026-11-26 : créée en To do (plan TSK43 point 4, demande TSC séance 12).
