# TSK45 — Factorisation des dialogues (plan TSK43, point 2)

- **Statut** : To do (26-11-2026).
- **Origine** : demande TSC séance 12 — plan de refactorisation TSK43, point 2 (fiche `TSK43_code_review_technical_debt.md`).
- **Dépendances** : → #TSK44 (ne pas factoriser du code mort).

## Périmètre (constats TSK43)

- `_add_buttons` identique ×4 (11 instructions, AST identique) : `ui/dialogs/agent_dialog.py:97`, `block_dialog.py:136`, `journey_dialog.py:78`, `relationship_dialog.py:137`.
- `_setup_ui` identique ×3 (20 instructions) : `agent_selection_dialog.py:36`, `journey_selection_dialog.py:39`, `relationship_selection_dialog.py:43`.
- `_setup_ui` quasi identique ×3 : `agent_dialog.py:48`, `journey_dialog.py:42`, `relationship_dialog.py:57`.

## Plan d'implémentation

1. Extraire une base/mixin de dialogue (ex. `ui/dialogs/base_dialog.py`) portant `_add_buttons` (boutons OK/Cancel standard, tailles via config — voir #TSK49) et le squelette `_setup_ui` des dialogues de sélection (liste + recherche éventuelle + boutons).
2. Faire hériter `AgentDialog`/`BlockDialog`/`JourneyDialog`/`RelationshipDialog` et les 3 `*_selection_dialog` de cette base ; ne garder que le spécifique (champs du formulaire, remplissage de la liste).
3. Vérifications : py_compile, pyflakes sans nouveau warning, tests offscreen des dialogues existants (pas de changement de comportement attendu — refactorisation pure), suite complète (201 passed + 3 pré-existants).
4. Kanban → Review après tests. Commit+push sur `dev` uniquement sur demande explicite TSC.

## Journal

- 2026-11-26 : créée en To do (plan TSK43 point 2, demande TSC séance 12).
