# TSK51 — Complétion des docstrings (plan TSK43, point 8)

- **Statut** : To do (26-11-2026).
- **Origine** : demande TSC séance 12 — plan de refactorisation TSK43, point 8 (fiche `TSK43_code_review_technical_debt.md`).
- **Dépendances** : → #TSK44–TSK50 (documenter du code stabilisé, pas du code en cours de refactorisation).

## Périmètre (constats TSK43)

- 9 classes sans docstring : `core/services/about_service.py`, `change_log_service.py`, `ui/dialogs/change_log_dialog.py`, `usecases/file_management/export_project_usecase.py`, `load_project_usecase.py`, `quit_application_usecase.py`, `save_project_usecase.py`, `usecases/journey_management/delete_journey_usecase.py`, `usecases/project_management/create_project_usecase.py`.
- 194/557 méthodes/fonctions sans docstring (35 %) — top : `ui/views/relationships_workspace.py` 33, `core/models/data_model.py` 25 (majoritairement `to_dict`/`from_dict`), `ui/widgets/filters_side_panel.py` 20, `ui/main_window.py` 15, `ui/nodes/agent_card.py` 8.
- Convention AGENTS.md : docstrings en **anglais**.

## Plan d'implémentation

1. Docstrings des 9 classes manquantes (anglais, une ligne + rôle).
2. Méthodes **publiques** sans docstring en priorité (`main_window`, `filters_side_panel`, `relationships_workspace`, workspaces, nodes, use cases publics) ; one-liners pour `to_dict`/`from_dict` de `data_model.py` ; les privées triviales (getters évidents) peuvent rester sans docstring — à valider avec TSC.
3. Vérifications : py_compile, pyflakes sans nouveau warning, suite complète inchangée (201 passed + 3 pré-existants — aucune modification de comportement).
4. Kanban → Review après tests. Commit+push sur `dev` uniquement sur demande explicite TSC.

## Journal

- 2026-11-26 : créée en To do (plan TSK43 point 8, demande TSC séance 12).
