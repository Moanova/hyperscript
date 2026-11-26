# TSK43 — Revue de code / dette technique

- **Statut** : Doing (26-11-2026).
- **Origine** : demande TSC séance 12 — le périmètre MVP étant opérationnel, analyser les éventuelles refactorisations nécessaires et la dette technique de `src/`.

## Axes d'analyse

1. **Code mort** : imports non utilisés, fonctions/méthodes/constantes jamais référencées, stubs (`lambda: None` des entrées grisées MVP), TODO/FIXME/XXX/HACK.
2. **Duplication de code** : corps de fonctions/méthodes identiques ou quasi identiques répétés entre fichiers.
3. **Principes d'implémentation** (AGENTS.md) : architecture UI → use cases → services → modèles ; `core/` Qt-free ; RG058 (l'UI n'écrit jamais le modèle métier directement — écritures via use cases/services) ; pas de valeurs UI en dur (passer par `config.json` via `config.config_loader.get` ou constantes de classe) ; suppression complète du code mort (pas de `_unused`, pas de shims de compatibilité) ; découplage Qt par signaux.
4. **Nommages linguistiques** : identifiants, commentaires et docstrings en anglais (AGENTS.md) vs français ; cohérence objet EN / UI FR (libellés UI français acceptés, `lb`/`typ` sanctionnés par la spec 07_data_model).
5. **Docstrings** : classes et méthodes publiques sans docstring.

## Méthode

- pyflakes sur `src/` (comparé à la base connue : warning pré-existant `Relationship` import non utilisé dans `core/services/preview_service.py`) ;
- greps ciblés (PySide6 dans `src/core/`, écritures directes du modèle dans `src/ui/`, `set_modified` hors use cases/services, TODO/FIXME, stubs) ;
- scripts AST : définitions jamais référencées, corps dupliqués, identifiants non-ASCII, docstrings manquants, commentaires/docstrings en français.

## Résultats

Périmètre analysé : `src/` = 83 fichiers Python, 11 903 lignes (pyflakes 4.1.0, greps ciblés, scripts AST : définitions non référencées, corps dupliqués, identifiants non-ASCII, docstrings, commentaires FR). Base : commit `1506281` (dev, tests 201 passed + 3 pré-existants hors scope).

### 1. Code mort — **constaté, sévérité haute**

- **5 imports non utilisés** (pyflakes) : `src/core/services/preview_service.py:42` (`Relationship`, pré-existant connu), `src/ui/views/preview_workspace.py:37` (`Agent`), `src/ui/views/preview_workspace.py:28` (`typing.List`), `src/ui/nodes/agent_card.py:41` (`QColor`), `src/core/services/layout_service.py:41` (`AgentCardLayout`).
- **28 définitions jamais référencées** dans `src/` ni `tests/` (hors override Qt) :
  - `core/services/layout_service.py` (9) : `get_safe_dir_name` (86), `get_project_dir` (289), `get_layout_dir` (302), `delete_workspace_layout` (387), `workspace_layout_exists` (415), `list_project_layouts` (434, référencée 1× dans tests), `delete_stale_layouts` (464, 2× dans tests), `delete_project_layouts` (513), `create_empty_layout` (551, 1× dans tests) — famille entière de gestion de fichiers de layout morte (seuls `load_/save_project_layout` et `load_/save_workspace_layout` sont utilisés) ;
  - `core/models/view_model.py` (2) : `get_node_layout` (235), `get_connection_layout` (239) ;
  - `ui/nodes/connection.py` (11) : `set_source_node` (615), `set_target_node` (630), `set_transition` (645), `set_style` (654), `set_color` (665), `set_thickness` (682), `set_label` (694), `get_source_node` (704), `get_target_node` (709), `get_label` (714), `get_relation_type` (729) — setters/getters hérités de planoscript jamais appelés ;
  - `ui/nodes/base_node.py` (4) : `add_port` (548), `get_port` (558), `set_note` (609 — **écrit directement `entity.note`, voir §3**), `get_note` (613) ;
  - `ui/views/journeys_workspace.py` (2) : `find_connection` (567), `has_connection_between` (577).
- **Constantes inutilisées** : `theme.py:39 FOCUS_COLOR`, `theme.py:68 NODE_FONT_SIZE_PX` (jamais référencées) ; `relationships_workspace.py:117 _PANEL_WIDTH`, `:131 _SEPARATOR_HEIGHT` (référencées uniquement par des tests).
- **Faux positif à ne pas toucher** : `filters_side_panel.py:332 createHandle` = override `QSplitter` appelé par Qt.
- **Stubs `lambda: None` (10)** dans `main_window.py:230-255` (Export Map, Import Map, Recent Projects, Undo/Redo/Cut/Copy/Paste, Zoom In/Out/Reset) : **intentionnels**, entrées grisées MVP (`MVP_GREYED`, spec `05_menu`) — pas du code mort à supprimer.
- Aucun TODO/FIXME/XXX/HACK dans `src/`.

### 2. Duplication de code — **constatée, sévérité moyenne**

- **`_add_buttons` identique ×4** (11 instructions, AST identique) : `dialogs/agent_dialog.py:97`, `block_dialog.py:136`, `journey_dialog.py:78`, `relationship_dialog.py:137`.
- **`_setup_ui` identique ×3** (20 instructions) : `agent_selection_dialog.py:36`, `journey_selection_dialog.py:39`, `relationship_selection_dialog.py:43` ; **`_setup_ui` quasi identique ×3** : `agent_dialog.py:48`, `journey_dialog.py:42`, `relationship_dialog.py:57`.
- **`AgentCardItem` duplique `BaseNode`** : `agent_card.py:50` hérite de `QGraphicsRectItem` au lieu de `BaseNode` → corps dupliqués : `update_layout` (171/261), `_rounded_path` (206/331), `paint` (220/345), `hoverEnterEvent` (279/393), `hoverLeaveEvent` (290/410).
- **Workspaces agents/journeys dupliqués** (pas de classe de base commune, toutes deux `QGraphicsView, QObject`) : `ensure_visible`, `add_item_at`, `viewportEvent` (`agents_workspace.py:187/194/228` vs `journeys_workspace.py:226/233/275`).
- **Constantes config dupliquées ×3** : `_GRID_MINOR_COLOR`/`_GRID_MAJOR_COLOR` redéfinies dans `journeys_workspace.py:47-48`, `relationships_workspace.py:120-121`, `filters_side_panel.py:52` (centralisables dans `theme.py`).

### 3. Principes d'implémentation — **globalement respectés, 4 écarts**

- ✅ `core/`, `usecases/`, `config/` **100 % Qt-free** (0 import PySide6/PyQt) ; aucun import de `ui` depuis `core`/`usecases`.
- ✅ UI → use cases : **29 appels `.execute(`** dans `src/ui/` ; écritures métier via use cases (RG058).
- ✅ Services appelés depuis l'UI en **lecture seule** (`current_project`, `is_modified`, `file_path`, filtres, `PreviewService`, `LayoutService` de calcul) ; couleurs/thème 100 % via `config.json` (`_get_config` avec défaut) hors valeur par défaut de `ui_utils.create_colored_icon`.
- ⚠️ **(RG058) écriture directe du modèle depuis l'UI** : `ui/nodes/base_node.py:611` `self.entity.note = note` — méthode morte (aucun appelant), à supprimer purement et simplement.
- ⚠️ `main_window.py:865` `project_service.set_modified(True)` dans `_on_workspace_modified` : seul appel de service mutateur depuis l'UI — pattern FN017 sanctionné (signal workspace → MainWindow), mais contourne un use case (pas de `MoveBlockUseCase` ; la position vit dans le view-model de layout).
- ⚠️ **Fuites d'encapsulation** (accès privés cross-classes) : `LayoutService._rects_overlap` appelé depuis `journeys_workspace.py:627` ; `relationships_workspace._splitter` depuis `main_window.py:724,959` ; `panel._set_anchor_block_silent` depuis `relationships_workspace.py:335` ; `line._is_grid_line = True` depuis `relationships_workspace.py:537,544`.
- ⚠️ **Valeurs UI en dur** (AGENTS.md : passer par `config.json`) : ~26 nombres magiques `setMinimumSize(W, H)` / `setFixedWidth(100)` répartis dans les 11 dialogues (`about_dialog.py:25,53`, `agent_association_dialog.py:55,70,73`, `agent_dialog.py:51,102,105`, `agent_selection_dialog.py:36,58,62`, `block_dialog.py:71,141,144`, `change_log_dialog.py:24`, `journey_dialog.py:45,83,86`, `journey_selection_dialog.py:42,58,62`, `relationship_dialog.py:60,142,145`, `relationship_selection_dialog.py:46,58,62`, `transition_dialog.py:42,63,66`).
- ℹ️ `core/models/view_model.py` = état de vue (layouts) placé dans `core/models` — Qt-free donc conforme à la règle, mais conceptuellement de la couche vue.
- ℹ️ `main_window.py` = **1 616 lignes** (god object ; puis `layout_service.py` 842, `journeys_workspace.py` 817, `connection.py` 731, `relationships_workspace.py` 670).

### 4. Nommages linguistiques — **conformes**

- **0 identifiant non-ASCII** dans `src/` ; noms de classes/méthodes/args en anglais (termes domaine EN : `Agent`, `Block`, `Journey`, `note`…) ; `lb`/`typ` = abréviations FR sanctionnées par la spec `07_data_model`.
- Commentaires : 1 454 au total, **1 seul avec vocabulaire français** (`agent_association_dialog.py:53`) ; docstrings : 446, **0 en français** — convention AGENTS.md (anglais) respectée. Les libellés UI en français sont sanctionnés (spec FR).

### 5. Docstrings manquants — **constaté, sévérité basse/moyenne**

- **194 / 557 méthodes ou fonctions sans docstring (35 %)** ; **9 / 87 classes sans docstring** (`about_service.py`, `change_log_service.py`, `change_log_dialog.py`, `export_project_usecase.py`, `load_project_usecase.py`, `quit_application_usecase.py`, `save_project_usecase.py`, `delete_journey_usecase.py`, `create_project_usecase.py`).
- Top fichiers (méthodes sans docstring) : `relationships_workspace.py` 33, `data_model.py` 25 (majoritairement `to_dict`/`from_dict` de dataclasses), `filters_side_panel.py` 20, `main_window.py` 15, `agent_card.py` 8.

## Plan de refactorisation proposé

Aucune modification de code dans cette tâche — plan à valider avec TSC, exécution en tâche(s) dédiée(s) (commit+push sur demande explicite, comme d'habitude).

1. **Code mort (rapide, sans risque)** : supprimer les 28 définitions mortes + `FOCUS_COLOR`/`NODE_FONT_SIZE_PX` + les 5 imports inutilisés (AGENTS.md : suppression complète, pas de shim) ; supprimer/adapter les références test-only (`list_project_layouts`, `delete_stale_layouts`, `create_empty_layout`, `_PANEL_WIDTH`, `_SEPARATOR_HEIGHT` dans `tests/`). En particulier `BaseNode.set_note` (écriture directe du modèle, §3).
2. **Duplication dialogues** : extraire une base/mixin de dialogue (ex. `ui/dialogs/base_dialog.py` avec `_add_buttons` et le squelette `_setup_ui` des 3 dialogues de sélection) — en héritent ensuite `AgentDialog`/`BlockDialog`/`JourneyDialog`/`RelationshipDialog` et les 3 `*_selection_dialog`.
3. **Duplication nœuds** : faire hériter `AgentCardItem` de `BaseNode` (ou extraire une base `QGraphicsRectItem` commune) pour supprimer les 5 méthodes dupliquées.
4. **Duplication workspaces** : extraire une `BaseGraphicsWorkspace(QGraphicsView, QObject)` avec `ensure_visible`/`add_item_at`/`viewportEvent` partagés par `AgentsWorkspace` et `JourneysWorkspace`.
5. **Constantes visuelles** : centraliser `_GRID_*_COLOR` et consorts dans `ui/utils/theme.py` (déjà adossés à `config.json`).
6. **Valeurs UI en dur** : clés `config.json` pour tailles mini des dialogues et largeurs de boutons (ex. `dialog_min_width/height`, `button_width_px`), remplacées dans les 11 dialogues.
7. **Encapsulation** : rendre public `LayoutService.rects_overlap` (ou wrapper public), exposer le splitter par propriété, renommer `_set_anchor_block_silent` en API publique du panneau.
8. **Docstrings** : compléter les 9 classes sans docstring et les méthodes publiques sans docstring (priorité `main_window`, `filters_side_panel`, `relationships_workspace`) ; one-liners pour `to_dict`/`from_dict` de `data_model.py`.
9. **Structure (post-MVP, plus lourd)** : éclater `main_window.py` (1 616 lignes) en modules (construction des menus, handlers par domaine) ; déplacer `view_model.py` hors de `core/models` si souhaité (conforme Qt-free entre-temps).

Ordre proposé : 1 → 2/3/4 (petits blocs indépendants) → 5/6/7 → 8 → 9. Chaque bloc = une tâche kanban avec tests de non-régression (suite offscreen : 201 passed + 3 pré-existants).

## Journal

- 2026-11-26 : créée en To do puis passée en Doing (demande TSC séance 12) ; analyse lancée (read-only — aucun changement de code prévu dans cette tâche).
- 2026-11-26 : **analyse terminée** — résultats ci-dessus (pyflakes, greps, scripts AST sur `src/`, 83 fichiers / 11 903 lignes) : code mort confirmé (28 defs + 2 constantes + 5 imports), duplication confirmée (dialogues ×4/×3, `AgentCardItem` vs `BaseNode`, workspaces), 4 écarts de principes (écriture modèle `base_node.py:611`, `set_modified` UI, fuites d'encapsulation, ~26 nombres magiques dans les dialogues), nommages conformes (0 identifiant non-ASCII, commentaires/docstrings anglais), docstrings manquants (194/557 méthodes, 9/87 classes). Plan de refactorisation proposé en 9 points, sans modification de code. Aucun commit/push (non demandé).
