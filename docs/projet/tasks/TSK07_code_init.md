# TSK07 — Initialisation de l'arborescence du code source

- **Créée** : 2026-11-10 — passée en Doing 2026-11-10 — implémentée et passée en Review 2026-11-10
- **Dépendances** : → #TSK06 (spécifications revues en séance du 10-11-2026)

## Objectif

Initialiser `src/` et `tests/` de hyperscript en reprenant le code planoscript figé (commit `faa8fdd`) selon le verdict d'analyse de reprise (séance du 10-11-2026) :

- **Classe A (reprise telle quelle)** : `config_loader.py`, `user_state_loader.py`, `ui_utils.py`, `about_service.py`, `change_log_service.py`, `about_dialog.py`, `change_log_dialog.py`, `tests/conftest.py`, métadonnées projet.
- **Classe B (diff localisé)** : `theme.py` (couleurs par type de bloc au lieu de state/event) — repris car dépendance des dialogues de la classe A.
- **Classe C (à réécrire)** : modèle de données, fenêtre principale, vues, nœuds, autres dialogues, use cases métier — **non repris** dans cette initialisation.

## Travaux réalisés

- Arborescence créée selon AGENTS.md : `src/config/`, `src/core/models/`, `src/core/services/`, `src/usecases/`, `src/ui/{utils,dialogs,nodes,views,widgets}/`, `tests/` (avec `__init__.py` ; `src/core/services/__init__.py` n'exporte que les services existants).
- Fichiers repris (classe A + theme.py) avec les modifications minimales : en-têtes « Application : Hyperscript », commentaires/docstrings en anglais (convention AGENTS.md), `about_service.py` : fallback « Hyperscript », `about_dialog.py` : titre lu depuis `about.json` (plus de « Planoscript » en dur), `conftest.py` : options/env `HYPERSCRIPT_*`, nom de fenêtre par défaut « Hyperscript », `pyproject.toml` : `name = "hyperscript"`.
- `theme.py` : `STATE_COLOR`/`EVENT_COLOR` → `BLOCK_START/SCENE/PIVOT/CONDITION/ENDING_COLOR` + `BLOCK_TYPE_COLORS` + `block_color()` ; usages d'accent dans les stylesheets sur `BLOCK_SCENE_COLOR`.
- Suite (fichiers classe B) : nouveau `src/core/models/data_model.py` (modèle 07_data_model : Project/NarrativeMap/Agent/Block/Transition/Participation/Relationship/Journey/Journey_node, `FORMAT_VERSION`, pas de `file_path` dans le modèle — FN005), `view_model.py` adapté (`BlockType`, `WorkspaceLayout.block_nodes`/`transition_connections`, `RelationType` supprimé — types de relations en config, FN037), `layout_service.py` repris tel quel (674 lignes, seuls `NodeType`→`BlockType` et les références RG plano remappées : RG046/RG050/RG036), `project_service.py` adapté (création RG013, save/load JSON unique + `format_version`, rejet des fichiers incompatibles RG009/RG010/RG016, `file_path` en état applicatif), `usecases/project_management/create_project_usecase.py` (RG037/RG025/RG040 : parcours par défaut activé, bloc Start unique, aucun bloc orphelin), `src/main.py` (garde single-instance `hyperscript-single-instance`, RG015/FN001), `src/ui/main_window.py` squelette (barre de menus selon `05_menu-EN.yaml` avec stubs `menu_actions[...]`, entrées grisées MVP désactivées RG007/RG008, About/Change Log fonctionnels, New Project... fonctionnel), `tests/test_project/test_project_service.py` (5 tests), `conftest.py` + `sys.path` src, `config.json` + `app_window_title`/`window_min_width`/`window_min_height`.
- Fichiers de données régénérés dans `src/config/` : `config.json` (clés plano conservées ; `state_color`/`event_color` → 5 couleurs de types de bloc ; `projects_default_dir` → `~/HyperscriptProjects` ; `events_view_*` → `journeys_view_*` ; ajout `relationship_types` pour FN037 ; `log_level` → WARNING), `about.json` (Hyperscript), `change_log.json` (entrée initiale), `recent_projects.json` (liste vide), `user_state.json` (`last_project_dir` vide — la valeur plano était un chemin local personnel).

## Décisions / points à valider

- Couleurs par type de bloc narratif : valeurs plano réparties (Start/Scène `#E5C07B`, Pivot/Condition `#D19A66`, Fin `#F0F0F0`) — **à valider en phase de conception** (04_interface le prévoit).
- `relationship_types` : liste initiale EN à valider (`friend, ally, rival, enemy, romantic, family`) — FN037.
- `main.py` (classe B, garde single-instance) non repris ici : nécessite `ui/main_window.py` (classe C) pour être exécutable.

## Vérifications

- `python -m py_compile` sur tous les fichiers Python créés : OK.
- Import des packages et instanciation offscreen (`QT_QPA_PLATFORM=offscreen`) de `AboutDialog` / `ChangeLogDialog` : OK (titres « Hyperscript » / « Change Log »).
- `python -m pytest tests/ -q` : collecte OK, aucun test encore (exit « no tests ran »).

## Journal

- 2026-11-10 : analyse de reprise planoscript (verdict A/B/C) ; initialisation de l'arborescence (classe A + theme.py + données) ; vérifications OK. TSK01–TSK06 validées TSC et passées en Done ; TSK07 maintenue en Doing pour la suite de l'initialisation.
- 2026-11-10 (suite) : reprise classe B — data_model.py (nouveau), view_model.py, layout_service.py, project_service.py, create_project_usecase.py, main.py, main_window.py (squelette menu) + tests test_project (5 tests). Vérifications : `py_compile` OK, `pytest tests/ -q` = 5 passed, smoke modèle/service OK. Lancement GUI non testable dans le sandbox (libGL absent) — à valider en GUI sur poste de dev. TSK07 reste en Doing.
- 2026-11-10 (fin) : reprise/adaptation de `ui/main_window.py` (point C, shell uniquement) + scripts associés — `usecases/file_management/` (load/save/quit), `ui/widgets/info_bar.py`, `ProjectService.close_project()` (l'UI ne touche pas au modèle directement) ; workspaces laissés en placeholder (tâche suivante). Menu conforme à `05_menu-EN.yaml` (stubs `menu_actions`, entrées grisées MVP désactivées RG007, Save désactivé si non modifié RG006, confirmations FN002/FN006/FN010, dialogues About FN003/FN004). + tests `test_file_usecases.py` (3 tests). Vérifications : `py_compile` OK, `pytest tests/ -q` = 8 passed, imports main_window résolus (statique). Commit + push sur `dev` ; TSK07 passée en Review.
