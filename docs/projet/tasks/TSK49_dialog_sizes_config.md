# TSK49 — Tailles des dialogues et boutons en config.json (plan TSK43, point 6)

- **Statut** : Review (26-11-2026) ; implémentée et pushée sur `dev` sur feu vert TSC séance 12.
- **Origine** : demande TSC séance 12 — plan de refactorisation TSK43, point 6 (fiche `TSK43_code_review_technical_debt.md`).
- **Dépendances** : → #TSK44 ; à coordonner avec #TSK45 (base dialogues : les tailles y seront consommées).

## Périmètre (constats TSK43)

~26 nombres magiques `setMinimumSize(W, H)` / `setFixedWidth(100)` en dur dans les 11 dialogues : `about_dialog.py:25,53`, `agent_association_dialog.py:55,70,73`, `agent_dialog.py:51,102,105`, `agent_selection_dialog.py:36,58,62`, `block_dialog.py:71,141,144`, `change_log_dialog.py:24`, `journey_dialog.py:45,83,86`, `journey_selection_dialog.py:42,58,62`, `relationship_dialog.py:60,142,145`, `relationship_selection_dialog.py:46,58,62`, `transition_dialog.py:42,63,66` (AGENTS.md : pas de valeurs UI en dur → `config.json` via `config_loader.get` avec défaut).

## Plan d'implémentation

1. Ajouter des clés dans `src/config/config.json` (ex. `dialog_min_width_px`, `dialog_min_height_px`, `dialog_button_width_px`, ou tailles par dialogue si hétérogènes) avec les valeurs actuelles comme défauts.
2. Remplacer les appels en dur dans les 11 dialogues par `_get_config(...)` (constantes de module ou via la base de #TSK45 si réalisée avant).
3. Vérifications : py_compile, pyflakes sans nouveau warning, tailles identiques (vérification offscreen ou unitaire sur les valeurs lues), suite complète (201 passed + 3 pré-existants).
4. Kanban → Review après tests. Commit+push sur `dev` uniquement sur demande explicite TSC.

## Journal

- 2026-11-26 : créée en To do (plan TSK43 point 6, demande TSC séance 12).
- 2026-11-26 : **passée en Doing puis implémentée et passée en Review** (feu vert TSC) — `config.json` : +15 clés (68 → 83) : `dialog_button_width_px` 100, `dialog_wide_button_width_px` 120, `dialog_form_min_width_px` 525, `dialog_form_min_height_px` 420, `journey_dialog_min_height_px` 300, `relationship_dialog_min_height_px` 460, `transition_dialog_min_height_px` 240, `selection_dialog_min_width/height_px` 400/400, `about_dialog_min_width/height_px` 400/200, `change_log_dialog_min_width/height_px` 500/400, `agent_association_dialog_min_width/height_px` 400/400. `base_dialog.py` : constantes `BUTTON_WIDTH_PX`/`WIDE_BUTTON_WIDTH_PX` ; `FormDialog.MIN_WIDTH_PX/MIN_HEIGHT_PX` et `SelectionDialog.MIN_WIDTH_PX/MIN_HEIGHT_PX` lus via `_get_config` (défauts = valeurs d'avant) ; `_setup_ui(title)` ne prend plus de tailles. Dialogues de formulaire : hauteurs spécifiques en attribut de classe (`MIN_HEIGHT_PX` sur journey/relationship/transition). `about_dialog`, `change_log_dialog`, `agent_association_dialog` : `_get_config` directement + `BUTTON_WIDTH_PX`/`WIDE_BUTTON_WIDTH_PX`. 0 `setMinimumSize(N, N)`/`setFixedWidth(N)` restant dans `ui/dialogs/`. Sonde offscreen : tailles identiques (AgentDialog 525×420, JourneyDialog 525×300, sélection 400×400, boutons 100/120). Vérifications : py_compile OK, **pyflakes 0 warning sur `src/`**, suite **200 passed + 3 pré-existants hors scope** (identiques à `56393bf`). Commit+push `dev` effectués (feu vert TSC).
