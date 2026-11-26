# TSK44 — Nettoyage du code mort (plan TSK43, point 1)

- **Statut** : Review (26-11-2026) ; implémentée et pushée sur `dev` sur feu vert TSC séance 12.
- **Origine** : demande TSC séance 12 — plan de refactorisation TSK43, point 1 (fiche `TSK43_code_review_technical_debt.md`).
- **Dépendances** : aucune (première tâche du plan).

## Périmètre (constats TSK43)

- 5 imports inutilisés (pyflakes) : `core/services/preview_service.py:42` (`Relationship`), `ui/views/preview_workspace.py:28` (`List`), `:37` (`Agent`), `ui/nodes/agent_card.py:41` (`QColor`), `core/services/layout_service.py:41` (`AgentCardLayout`).
- 28 définitions jamais référencées : `core/services/layout_service.py` ×9 (`get_safe_dir_name` 86, `get_project_dir` 289, `get_layout_dir` 302, `delete_workspace_layout` 387, `workspace_layout_exists` 415, `list_project_layouts` 434, `delete_stale_layouts` 464, `delete_project_layouts` 513, `create_empty_layout` 551), `core/models/view_model.py` ×2 (`get_node_layout` 235, `get_connection_layout` 239), `ui/nodes/connection.py` ×11 (615–729 : setters/getters planoscript), `ui/nodes/base_node.py` ×4 (`add_port` 548, `get_port` 558, `set_note` 609 — écrit directement `entity.note`, écart RG058, `get_note` 613), `ui/views/journeys_workspace.py` ×2 (`find_connection` 567, `has_connection_between` 577).
- Constantes mortes : `ui/utils/theme.py:39 FOCUS_COLOR`, `:68 NODE_FONT_SIZE_PX` ; `ui/views/relationships_workspace.py:117 _PANEL_WIDTH`, `:131 _SEPARATOR_HEIGHT` (référencées uniquement par des tests).
- Références test-only à ajuster : `list_project_layouts`, `delete_stale_layouts`, `create_empty_layout`, `_PANEL_WIDTH`, `_SEPARATOR_HEIGHT` dans `tests/`.

## Plan d'implémentation

1. Supprimer les 28 définitions + 4 constantes + 5 imports (AGENTS.md : suppression complète, pas de `_unused`, pas de shim de compatibilité).
2. Mettre à jour les tests référençant les symboles supprimés.
3. Vérifications : pyflakes 0 warning, py_compile, suite offscreen complète (attendu : 201 passed + 3 pré-existants `test_block_drag_offscreen.py` hors scope).
4. Kanban → Review après tests. Commit+push sur `dev` uniquement sur demande explicite TSC.

## Journal

- 2026-11-26 : créée en To do (plan TSK43 point 1, demande TSC séance 12).
- 2026-11-26 : **passée en Doing** (feu vert TSC séance 12) — implémentation lancée ; push sur `dev` dans la foulée.
- 2026-11-26 : **implémentée et passée en Review** — 28 définitions supprimées, 4 constantes (`theme.py` `FOCUS_COLOR`/`NODE_FONT_SIZE_PX`, alias `_PANEL_WIDTH`/`_SEPARATOR_HEIGHT` de `relationships_workspace.py`), 5 imports inutilisés, `self.ports` (base_node.py) supprimé avec `add_port`/`get_port` ; tests ajustés : `test_project_layout_file_excluded_from_map_layouts` supprimé (testait uniquement `create_empty_layout`/`list_project_layouts`/`delete_stale_layouts`), `test_relationships_workspace_offscreen.py` importe désormais les constantes réelles `PANEL_WIDTH_PX`/`SEPARATOR_HEIGHT_PX` depuis `ui.widgets.filters_side_panel`. Vérifications : py_compile OK, **pyflakes 0 warning sur `src/`**, **200 tests passed + 3 pré-existants hors scope** (`test_block_drag_offscreen.py`, reproductibles sur arbre propre `1506281`). Note : pyflakes signale 7 warnings pré-existants dans `tests/` (hors périmètre TSK44). Commit+push `dev` effectués (feu vert TSC).
