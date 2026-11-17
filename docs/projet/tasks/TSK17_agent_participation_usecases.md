# TSK17 — Services et use cases agents & participations

- **Créée** : 2026-11-17 — passée en Doing 2026-11-17 (TSK08 en Done) — plan d'implémentation établi séance n°04
- **Dépendances** : → #TSK08

## Objectif

Couche modèle/services/use cases de la gestion des agents (SU008, FN031) et des participations agent-bloc (SU008, FN030 ; RG032/RG033), par reprise des use cases planoscript (figé `faa8fdd`) adaptés au vocabulaire hyperscript. Aucun composant Qt : `core/` et `usecases/` restent Qt-free (RG058).

## Ce qui existe déjà (ne pas refaire)

- Modèle : `Agent` (typ `Character`/`Artefact`, `AGENT_TYPES`), `Participation`, `Relationship` dans `src/core/models/data_model.py` ; `Project.get_next_id('agent')` et `NarrativeMap.get_next_id('participation')` opérationnels.
- Cascade RG023 côté bloc déjà en place : `TransitionService.delete_block_cascade()` supprime participations et relations ancrées (`transition_service.py:109-130`).
- `ParticipationBadgeService` (badge + ligne « Agents: »), filtre de parcours dérivé (RG041), clés config `agents_view_*`, stubs de menu `agents_*` dans `main_window.py`.

## Reprise planoscript → hyperscript (mapping)

| Planoscript (`faa8fdd`) | Hyperscript | Adaptation |
|---|---|---|
| `usecases/project_management/create_agent_usecase.py` | `usecases/agent_management/create_agent_usecase.py` | `AGENT_TYPES` depuis `data_model` (Character/Artefact) ; label défaut « Agent {id} » ; style hyperscript (retourne l'entité, `ValueError` sur erreur, `set_modified(True)`) |
| `update_agent_usecase.py` | idem | lb non vide requis ; typ ∈ AGENT_TYPES ; note/content |
| `duplicate_agent_usecase.py` | idem | label « {lb} (copy) » (convention hyperscript FN016) ; **participations et relations non copiées** |
| `delete_agent_usecase.py` | idem | cascade RG033 : participations + relations de l'agent, comptées pour le message de confirmation (la confirmation elle-même est du côté UI) |
| `usecases/agent_association/associate_agent_state_usecase.py` | `usecases/participation_management/associate_participation_usecase.py` | `State_agent_rel` → `Participation` (`state_id`→`block_id`) ; unicité RG032 (idempotent, signale `already_associated`) |
| `dissociate_agent_state_usecase.py` | `dissociate_participation_usecase.py` | idem ; échoue si aucune participation |
| `remove_state_associations_usecase.py` | inutile | cascade bloc déjà dans `TransitionService.delete_block_cascade` (RG023) |
| `update_agent_state_association_usecase.py` | **hors MVP** | la note de participation n'est pas éditable en MVP (comme planoscript SU008) |

## Plan d'implémentation

1. **`src/core/services/participation_service.py`** (Qt-free, pattern `TransitionService`) :
   - `find_participation(narrative_map, block_id, agent_id)` → RG032 ;
   - `participations_of_block(narrative_map, block_id)`, `participations_of_agent(project, agent_id)` ;
   - `cascade_delete_agent(project, agent_id)` → supprime participations + relations référençant l'agent (RG033) et retourne les comptages pour le message UI.
2. **`src/usecases/agent_management/`** (`__init__.py` + 4 use cases) : create / update / duplicate / delete agent, adaptés de planoscript (voir mapping), style hyperscript (comme `create_block_usecase.py`) : validations (`ValueError`), `project.get_next_id('agent')`, `set_modified(True)`.
3. **`src/usecases/participation_management/`** (`__init__.py` + associate / dissociate) : validation agent ∈ projet, bloc ∈ carte courante (MVP : `narrative_maps[0]`) ; unicité RG032 ; `set_modified(True)` ; retourne la `Participation` (ou None / déjà-existante).
4. **Tests unitaires** `tests/test_agents/` (`__init__.py`, `test_agent_usecases.py`, `test_participation_usecases.py`), adaptés de `planoscript/tests/test_agents/` (`test_agent_usecases.py`, `test_agent_state_association.py`, `test_agent_duplication.py`, `test_delete_agent_usecase.py`) : fixture `make_service()` = `ProjectService()` + `CreateProjectUseCase(service).execute()` (pattern `tests/test_blocks/test_block_usecases.py`). Couvre : FN031 (create/update/duplicate/delete, types Character/Artefact, label par défaut, « (copy) », participations non copiées), RG033 (cascade participations + relations + comptage), FN030 (associate/dissociate), RG032 (unicité, idempotence), modified flag.
5. **Matrice de traçabilité** `docs/projet/implementation-FR/EN.md` : lignes FN030/FN031 (et RG032/RG033) passées à `implemented` avec références fichiers/tests.

## Hors périmètre TSK17

Dialogues et menus (TSK18), vue « Agents » et menu contextuel de bloc (TSK19), relations (TSK20), badges (déjà en place côté vue Journeys, alimentés dès que les participations existent).

## Travaux réalisés

1. `src/core/services/participation_service.py` (Qt-free) : `get_agent`, `get_block`, `find_participation` (RG032), `get_block_participations`, `get_agent_participations`, `get_agent_relationships`, `cascade_delete_agent` (RG033 : participations + relations, comptages retournés).
2. `src/usecases/agent_management/` : `CreateAgentUseCase` (label défaut « Agent {id}", typ Character/Artefact), `UpdateAgentUseCase` (None = inchangé, label vide refusé), `DuplicateAgentUseCase` (« {lb} (copy) », participations/relations non copiées), `DeleteAgentUseCase` (RG033 via le service, comptages pour le message UI ; confirmation = responsabilité UI). Style hyperscript (retourne l'entité, `ValueError`), adapté de planoscript.
3. `src/usecases/participation_management/` : `AssociateParticipationUseCase` (RG032 idempotent — retourne la participation existante), `DissociateParticipationUseCase` (None si aucune participation). Note de participation non éditable en MVP (comme planoscript).
4. `tests/test_agents/` : `test_agent_usecases.py` (9 tests : FN031 create/update/duplicate/delete, RG033 cascade) + `test_participation_usecases.py` (5 tests : FN030 associate/dissociate, RG032 idempotence, helpers du service), adaptés de `planoscript/tests/test_agents/`.
5. Matrice de traçabilité `docs/projet/implementation-FR/EN.md` : RG032/RG033 → `implemented`, FN030/FN031/SU008 → `partial` (UI en TSK18/TSK19).

## Vérifications

- `python -m py_compile` sur les 9 fichiers créés : OK.
- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` : **59 passed** (45 existants + 14 nouveaux).
- Vérif AST : aucun import Qt dans `core/`/`usecases/` (RG058) : OK.

## Journal

- 2026-11-17 : tâche créée et passée en Doing ; plan établi d'après l'analyse de reprise planoscript (séance n°04). Implémentation réalisée sur feu vert TSC (feu vert reçu dans la séance) : 59 tests passed, tâche passée en Review.
