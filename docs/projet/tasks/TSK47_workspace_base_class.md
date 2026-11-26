# TSK47 — Classe de base des workspaces graphiques (plan TSK43, point 4)

- **Statut** : Review (26-11-2026) ; implémentée et pushée sur `dev` sur feu vert TSC séance 12.
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
- 2026-11-26 : **passée en Doing puis implémentée et passée en Review** (feu vert TSC) — `src/ui/views/base_workspace.py` créé : `BaseGraphicsWorkspace(QGraphicsView, QObject)` avec `_init_view()` (frame, contexte menu, scène + fond, stylesheet, scène 4000×4000, scrollbars toujours visibles, `centerOn(2000,2000)`, hook `_on_scroll_changed`, NoDrag, antialiasing), `_set_scene_rect`, `_expand_scene_to_include` (version non clampée), `ensure_visible`, `add_item_at`, `mouseMoveEvent` + `_auto_scroll_on_drag`, `viewportEvent` (avale l'événement ToolTip), signaux `workspace_modified`/`context_menu_requested`. `AgentsWorkspace` : hérite, garde `drawBackground` (points), `resizeEvent`, `_expand_scene_to_include` clampé à 0 (TSK30 2.1, test `test_agents_workspace_offscreen` conservé), cartes, sélection, menu contextuel. `JourneysWorkspace` : hérite, garde `_draw_grid`/`resizeEvent`/`showEvent`, `_on_scroll_changed` → `_draw_grid`, mode création de transition (`mouseMoveEvent` appelle `QGraphicsView.mouseMoveEvent` explicitement pour préserver l'ordre trace → auto-scroll), filtres, `_select_item_only`/`_clear_all_selections` (inchangés : émission `selection_changed` + test `isEnabled` spécifiques). Export ajouté dans `ui/views/__init__.py`. Vérifications : py_compile OK, **pyflakes 0 warning sur `src/`**, scan AST **0 groupe de corps dupliqué** entre base/agents/journeys, suite **200 passed + 3 pré-existants hors scope** (identiques à `4070b94`). Commit+push `dev` effectués (feu vert TSC).
