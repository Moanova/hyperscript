# TSK18 — Dialogues agents + câblage du menu `Project › Agents`

- **Créée** : 2026-11-17 — passée en Doing 2026-11-17 (TSK17 en Review)
- **Dépendances** : → #TSK17

## Objectif

Rendre fonctionnelles les entrées du menu `Project › Agents` (New.../Edit.../Copy/Delete.../Associate with Block...) via trois dialogues repris de planoscript et adaptés, et connecter les use cases TSK17 (`agent_management`, `participation_management`). RG058 : l'UI ne touche jamais le modèle — les dialogues émettent des signaux ou retournent des valeurs, `MainWindow` applique les use cases.

## Plan d'implémentation

1. `src/ui/dialogs/agent_dialog.py` (reprise plano, ~131 l) : création (`entity=None`, `default_label`) + édition ; champs Label / **Type** (combo `AGENT_TYPES` — le type agent reste éditable, FN031, contrairement au bloc TSK16) / Note / Content ; `get_values()` → `{lb, typ, note, content}` ; validation label non vide (pattern `BlockDialog._validate`).
2. `src/ui/dialogs/agent_selection_dialog.py` (pattern `JourneySelectionDialog`, TSK12) : liste des agents, Ok désactivé sans sélection, `get_selected_agent()` — utilisé par Edit/Copy/Delete/Associate tant que la vue « Agents » (TSK19) n'existe pas.
3. `src/ui/dialogs/agent_association_dialog.py` (reprise plano, ~135 l, **adapté RG058**) : liste cochable des agents avec statut de participation pour un bloc ; signaux `participation_toggled(agent_id, checked)` et `agent_create_requested(values)` ; bouton « New agent... » (création + association en une opération, FN030) ; `refresh(agents, participating_ids)` + `set_status(text)` appelés par MainWindow après application des use cases. **Chez planoscript le dialogue appelait les use cases directement — interdit ici.**
4. `src/ui/dialogs/__init__.py` : exporter les 3 dialogues.
5. `src/ui/main_window.py` :
   - instancier les 6 use cases TSK17 dans `__init__` ;
   - remplacer les stubs `agents_*` par les handlers : `_new_agent`, `_edit_agent`, `_copy_agent`, `_delete_agent` (confirmation avec comptages participation/relations RG033 + message info bar), `_associate_agent_with_block` (sélection agent → bloc sélectionné dans la vue Journeys → dialogue d'association ; signaux appliqués via les use cases, puis `refresh_all_participation_badges()`) ;
   - `_update_menu_state()` : nouvel ensemble `AGENT_DEPENDENT` (`agents_edit/copy/delete/associate`) activé seulement si projet ouvert **et** au moins un agent.
6. Specs : note dans `05_menu-EN/FR.yaml` sur le libellé « Associate with Block... » (menu) vs « Associate agents... » (menu contextuel de bloc, FN030, TSK19) ; matrice `implementation-FR/EN.md` : FN031 → `implemented`, FN030 reste `partial` (matrice + menu contextuel en TSK19).

## Travaux réalisés

1. `src/ui/dialogs/agent_dialog.py` : création/édition agent (Label/Type combo `AGENT_TYPES`/Note/Content, `get_values()`, validation label non vide) — reprise planoscript adaptée.
2. `src/ui/dialogs/agent_selection_dialog.py` : sélection d'agent (pattern `JourneySelectionDialog`), utilisé par Edit/Copy/Delete/Associate.
3. `src/ui/dialogs/agent_association_dialog.py` : liste cochable des agents pour un bloc, **conforme RG058** — signaux `participation_toggled(agent_id, checked)` / `agent_create_requested(values)` au lieu des appels directs aux use cases de planoscript ; « New agent... » (création + association, FN030) ; `refresh()` / `set_status()` appelés par MainWindow.
4. `src/ui/dialogs/__init__.py` : exports des 3 dialogues.
5. `src/ui/main_window.py` : 6 use cases TSK17 instanciés ; stubs `agents_*` remplacés par les handlers (`_new_agent`, `_edit_agent`, `_copy_agent`, `_delete_agent` avec confirmation RG033 comptée, `_associate_agent_with_block` → `_open_association_dialog`, `_on_participation_toggled`, `_on_agent_create_requested`, `_refresh_participation_badges`) ; nouvel ensemble `AGENT_DEPENDENT` dans `_update_menu_state()` (entrées agent exigeant ≥ 1 agent).
6. Specs : note de libellé dans `05_menu-EN/FR.yaml` (« Associate with Block... » au menu vs « Associate agents... » au menu contextuel de bloc, TSK19) ; matrice FR/EN : FN031 → `implemented`, FN030 → `partial` (matrice + menu contextuel en TSK19).

## Vérifications

- `python -m py_compile` sur les 5 fichiers : OK ; `yaml.safe_load` sur `05_menu-EN/FR.yaml` : OK.
- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` : **59 passed** (pas de nouveau test unitaire, TSK18 est de l'UI).
- Smoke offscreen jetable (non commité) à valider sur poste de dev : CRUD agent via les handlers (message de cascade RG033), bascule de participation via le dialogue → participation créée + badge du bloc rafraîchi. libGL absent dans le sandbox.

## Journal

- 2026-11-17 : fiche créée au passage en Doing ; plan établi séance n°04. Implémentation réalisée sur feu vert TSC : 59 tests passed, tâche passée en Review.
