# TSK39 — Retours de test TSC (séance 12, 26-11-2026)

- **Statut** : Doing (26-11-2026) ; dépend de #TSK37, #TSK38 (Done 26-11-2026).
- **Origine** : retours de test manuel TSC après la séance 11 — 24 points : menu général 1.1–1.11, vue « Relationships » 2.1–2.4, vue « Journeys » 3.1–3.3, vue « Preview » 4.1–4.4.

## Analyse des retours (causes racines vérifiées dans le code)

### 1) Menu général (`src/ui/main_window.py` sauf mention)

| Retour | Cause racine | Modification |
|---|---|---|
| 1.1 `Project > View` inactif | Les 4 entrées `view_journeys/view_agents/view_relationships/view_preview` sont des stubs `lambda: None` (`:258-262`, note « Stub » du YAML `05_menu`) | Câbler chaque entrée sur `tab_bar.setCurrentTab(<vue>)` (émet `currentChanged` → `_on_tab_changed` → `pages.setCurrentWidget`) via un handler `_switch_view(name)` ; retirer les notes « Stub » de `05_menu` FR/EN |
| 1.2 New/Copy agent sans bascule | `_new_agent` (`:1043`) / `_copy_agent` (`:1073`) créent sans changer de vue | `setCurrentTab("Agents")` après création/duplication |
| 1.3 « Associate with Block... » | `agents_associate` n'est que AGENT_DEPENDENT (actif dès qu'un agent existe, quelle que soit la vue/sélection) ; libellés divergents : menu « Associate with Block... » (`:268`) vs menu contextuel de bloc « Associate agents... » codé en dur dans `_show_workspace_context_menu` | Activer seulement si onglet courant == « Journeys » ET sélection courante est un `BlockNode` ; libellé « Add Participation » pour l'entrée du menu général et celle du menu contextuel de bloc (le menu contextuel de la vue « Agents » reprend `src.text()`, il suit automatiquement) |
| 1.4 New/Copy bloc sans bascule | `_create_new_block` (`:764`) / `_duplicate_selected_block` (`:836`) ne basculent pas | `setCurrentTab("Journeys")` avant la création |
| 1.5/1.6/1.7 grisement Blocks/Transitions | `blocks_*`/`transitions_*` = PROJECT_DEPENDENT uniquement ; `_update_menu_state` (`:332`) ignore l'onglet actif et la sélection, et n'est rappelée ni sur `selection_changed` (`_on_journeys_selection_changed` `:750`) ni sur changement d'onglet (`_on_tab_changed` `:718`) | Nouveaux jeux d'activation : onglet « Journeys » requis pour `transitions_new/edit/delete` et `blocks_edit/copy/delete` ; sélection `BlockNode` requise pour `blocks_edit/copy/delete` et `agents_associate`, `Connection` pour `transitions_edit/delete` ; appeler `_update_menu_state()` dans `_on_journeys_selection_changed` et `_on_tab_changed` |
| 1.8 Journeys New/Edit/Delete sans fenêtre | `_new_journey` (`:902`) exécute `create_journey_usecase.execute()` sans dialogue ; `_delete_journey` (`:922`) supprime le parcours actif sans sélection ni confirmation ; `_edit_journey` (`:1370`) OK (ouvre `JourneyDialog`) | New → `JourneyDialog()` mode création (entity=None) puis `execute(lb, note)` ; Delete → `JourneySelectionDialog` (choix du parcours) + `QMessageBox.question` avant `delete_journey_usecase.execute` |
| 1.9 `Project > Journeys > Copy` à supprimer | Action `journeys_copy` (`:286`), entrée PROJECT_DEPENDENT (`:313`), `_copy_journey` (`:915-921`), `DuplicateJourneyUseCase` (`:128` + `usecases/journey_management/`), entrée « Copier » du YAML, test FN025 | Suppression complète (code mort retiré, pas de shim) : action + jeu d'activation + méthode + use case + export `__init__` + fichier + tests + YAML FR/EN + FN025 dans `03_features` |
| 1.10 New relation sans bascule | `_new_relationship` (`:1201`) ne bascule pas | `setCurrentTab("Relationships")` avant l'ouverture du dialogue |
| 1.11 Edit/Delete relation : type au lieu du parcours | `RelationshipSelectionDialog._refresh_list` (`relationship_selection_dialog.py:76`) affiche `A <-> B @ bloc (rel.typ)` | Remplacer le `(typ)` final par le(s) parcours du bloc d'ancrage : `JourneyService.attachment_journey_ids(nm, rel.block_id)` + labels des journeys, ex. `A <-> B @ bloc (J1, J2)` |

### 2) Vue « Relationships »

| Retour | Cause racine | Modification |
|---|---|---|
| 2.1 « View in Journeys view » actif sur cellule vide | `_show_relationships_context_menu` (`main_window.py`) ajoute `view_action` sans condition | `view_action.setEnabled(rel is not None)` |
| 2.2 la bascule n'a pas lieu (onglet coché, page inchangée) | `_view_relationship_anchor_in_journeys` appelle `tab_bar.forceCurrentTab("Journeys")`, qui **ne réémet pas** `currentChanged` (`tab_bar.py:100-112`) → `_on_tab_changed`/`pages.setCurrentWidget` jamais appelés | `setCurrentTab("Journeys")` (avec émission) — même correction pour 1.2/1.4/1.10 |
| 2.3 carte d'agent supprimé restant dans la matrice et déplaçable partout | `RelationshipsWorkspace._relayout()` (`relationships_workspace.py:467`) n'ajoute/repositionne que les cartes d'en-tête : `refresh()` nettoie `_order` mais jamais `_row_cards`/`_col_cards` ni la scène → carte fantôme draggable (`_on_card_dragged` sans contrôle) et `ValueError` au release (`order.index(agent_id)` dans `_reorder`) | Dans `_relayout()` : supprimer de la scène et des dicts les cartes dont l'id est hors `_order`, et les cellules d'indices ≥ len(`_order`) ; garde dans `_on_card_released` (agent hors `_order` → ignorer) |
| 2.4 panneau latéral : type au lieu des parcours | `FiltersSidePanel.rebuild_block_list` (`filters_side_panel.py:250`) libelle toujours `f"{b.lb} ({b.typ})"`, quel que soit le filtre | Filtre sur un parcours précis : `f"{b.lb} ({', '.join(labels des parcours attachés)})"` via `JourneyService.attachment_journey_ids` (à la place du type) ; « All journeys » : type conservé `f"{b.lb} ({b.typ})"` (décision TSC confirmée, cf. ci-dessous) |

### 3) Vue « Journeys »

| Retour | Cause racine | Modification |
|---|---|---|
| 3.1 pas d'ajout de participations depuis le dialogue Edit des blocs | `BlockDialog` (`block_dialog.py`) n'a que la liste « Journeys » (RG042) | Ajouter une liste cochable « Agents » (agents du projet, participants actuels cochés via `ParticipationService.get_block_participations`), `agent_ids` dans `get_values()` ; dans `_edit_selected_block`, après `update_block_usecase`, appliquer associate/dissociate pour atteindre l'ensemble coché (mêmes use cases que `_on_participation_toggled`) puis `_refresh_participation_badges()` |
| 3.2 champs « Condition kind »/« Artefact ref »/« Condition label » à supprimer | Portés par `BlockDialog._setup_condition_fields`/`get_condition` (`:125-146,168-176`), le modèle `Block.condition` + `CONDITION_KINDS` (`data_model.py:30,97-110`) et `update_block_usecase.py:36-42` | **Retrait complet du modèle** (décision TSC séance 12) : supprimer `condition` + validation + `CONDITION_KINDS` de `data_model.py`, le paramètre `condition` de `update_block_usecase`, les champs du dialogue, le rendu Preview (4.3), les specs `07_data_model`/FN035 et les tests concernés |
| 3.3 les nouveaux blocs ne suivent pas la zone visible | `next_free_creation_position()` (`journeys_workspace.py:586-602`) s'ancre toujours sur le bloc Start (position fixe, indépendante du scroll) | Calculer la zone visible courante `self.mapToScene(self.viewport().rect()).boundingRect()` et y prendre la première position libre snappée (scan row-major via `LayoutService.find_first_free_cell` avec `bounds` = zone visible) ; repli sur l'ancrage Start si la zone visible est pleine |

### 4) Vue « Preview » (`src/core/services/preview_service.py`)

| Retour | Cause racine | Modification |
|---|---|---|
| 4.1 pas d'affichage des participations | `_block_html` (`:213-236`) rend lb(typ)/content/transitions/relations, jamais les agents participants | Ligne des agents participants (labels) entre le `Content` et les relations, via `ParticipationService.get_block_participations(nm, block_id)` |
| 4.2 relations pas sous la liste des agents | Les relations ancrées sont déjà rendues sous le bloc (`:231-236`) | Avec 4.1 inséré avant, l'ordre devient content → agents → relations ; ajuster si besoin |
| 4.3 champs de condition affichés | Rendu `Condition kind: ref_agent_id=…, label=…` (`:219-222`) | Supprimé avec 3.2 (retrait complet) |
| 4.4 type d'agent non affiché | Section b) : lb seul (`:111-114`) ; section g) : type en `<em>` séparé (`:134-138`) | `lb (typ)` dans la liste b) (lien conservé) et dans l'en-tête g) (le `<em>typ</em>` séparé est supprimé) |

## Décisions actées (séance 12, TSC)

1. **3.2** : retrait complet de la condition structurée **hors du modèle** (`Block.condition`, `CONDITION_KINDS`, validation, use case, dialogue, preview, specs, tests) — « afin de simplifier le modèle ».
2. **2.4 (confirmé TSC séance 12)** : filtre sur un parcours précis dans le panneau latéral → parcours du bloc entre parenthèses **à la place du type** ; « All journeys » → **type de bloc conservé** (comportement actuel inchangé). La formulation du retour 2.4 était ambiguë ; la validation TSC tranche pour la conservation du type sur « All journeys ».
3. **Bascule de vue par action utilisateur** = `TabBar.setCurrentTab` (avec émission de `currentChanged`), jamais `forceCurrentTab` (sans émission), réservé à la restauration de l'onglet par défaut à l'ouverture d'un projet.
4. **1.9** : suppression complète de la duplication de parcours (code mort retiré, pas de shim de compatibilité).

## Plan d'implémentation

1. `src/ui/main_window.py` — menus et bascules : (1.1) handler `_switch_view(name)` câblé sur les 4 entrées `Project > View` ; (1.2/1.4/1.10) `setCurrentTab(...)` dans `_new_agent`/`_copy_agent`/`_create_new_block`/`_duplicate_selected_block`/`_new_relationship` ; (1.3/1.5/1.6/1.7) nouveaux jeux d'activation dans `_update_menu_state` (onglet actif via `tab_bar.currentTab()`, sélection via `_get_selected_item()`) + rappel de `_update_menu_state()` dans `_on_journeys_selection_changed` et `_on_tab_changed` ; (1.3) libellé « Add Participation » (`:268` et entrée contextuelle du bloc dans `_show_workspace_context_menu`) ; (1.8) `_new_journey` → `JourneyDialog` mode création, `_delete_journey` → `JourneySelectionDialog` + confirmation ; (1.9) suppression de `journeys_copy`/`_copy_journey`/`duplicate_journey_usecase` ; (2.1) `view_action.setEnabled(rel is not None)` ; (2.2) `setCurrentTab("Journeys")` dans `_view_relationship_anchor_in_journeys`.
2. `src/usecases/journey_management/` — supprimer `duplicate_journey_usecase.py` + son export dans `__init__.py` ; tests `tests/test_journeys/test_journey_usecases.py` (FN025) à retirer.
3. `src/ui/dialogs/relationship_selection_dialog.py` — (1.11) libellé `A <-> B @ bloc (parcours…)` via `JourneyService.attachment_journey_ids`.
4. `src/ui/views/relationships_workspace.py` — (2.3) `_relayout()` supprime les cartes/cellules hors `_order` (`scene.removeItem`) ; garde dans `_on_card_released`.
5. `src/ui/widgets/filters_side_panel.py` — (2.4) libellé du bloc : `lb (parcours…)` quand un parcours précis est filtré, `lb (typ)` sur « All journeys » (décision §2).
6. `src/ui/dialogs/block_dialog.py` + `main_window._edit_selected_block` — (3.1) liste cochable « Agents » + `agent_ids` dans `get_values()` + application associate/dissociate + `_refresh_participation_badges()`.
7. Retrait de la condition structurée (3.2/4.3) : `src/core/models/data_model.py` (`condition`, `CONDITION_KINDS`, validation `__post_init__`), `src/usecases/view_management/update_block_usecase.py` (paramètre `condition`), `block_dialog.py` (`_setup_condition_fields`, `get_condition`, paramètre `artefact_agents`), `preview_service.py` (rendu condition `:219-222`) ; tests : `tests/test_blocks/test_block_usecases.py` (FN035), `tests/test_project/test_project_service.py` (`test_block_condition_only_on_condition_type`), `tests/test_preview/test_preview_service.py` (`test_condition_block_renders_its_condition` + helper `condition=`).
8. `src/ui/views/journeys_workspace.py` — (3.3) `next_free_creation_position()` ancré sur la zone visible courante (`mapToScene(viewport().rect())` + `LayoutService.find_first_free_cell` borné), repli ancrage Start.
9. `src/core/services/preview_service.py` — (4.1) ligne des agents participants sous le `Content` ; (4.2) ordre content → agents → relations ; (4.4) `lb (typ)` sections b) et g).
10. Specs FR/EN : `05_menu` (View activé, « Add Participation », sous-menu Parcours sans « Copier », note du menu contextuel), `03_features` (FN025 supprimée, FN035 révisée, FN030 libellé), `04_interface` (dialogue bloc : liste Agents, plus de champs condition ; §6 panneau Relationships ; §7 Preview), `07_data_model` (plus de `condition` sur Block), `02_business_rules` si une RG y fait référence, matrices `docs/projet/implementation-FR/EN.md`.
11. Tests : unitaires (use cases, services) + offscreen (états des menus selon onglet/sélection, bascules 1.1/1.2/1.4/1.10/2.2, `view_action` grisé sur cellule vide, matrice sans carte fantôme après suppression d'agent, libellé du panneau selon le filtre, `BlockDialog` liste Agents + participations appliquées, `next_free_creation_position` dans la zone visible, preview : participants/relations/ordre/`lb (typ)`/plus de condition) ; `python -m py_compile` sur chaque fichier modifié ; suite complète `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q`.
12. Kanban (TSK39 → Review après implémentation) + SESSIONS.md. Commit/push sur demande explicite de TSC uniquement.

## Journal

- 2026-11-26 : TSK39 créée en To do (analyse des 24 retours livrée, consignée dans SESSIONS.md séance 12) ; TSK37/TSK38 validées TSC et passées en Done ; TSK39 passée en **Doing**, fiche initialisée (analyse + décisions actées + plan ci-dessus). Implémentation sur feu vert TSC.
