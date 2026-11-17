# TSK19a — Filtre agent dans la vue « Journeys » (FN039, RG063/RG064)

- **Créée** : 2026-11-17 — passée en Doing 2026-11-17 (TSK11 Done, TSK17 en Review)
- **Dépendances** : → #TSK11, → #TSK17

## Objectif

Ajouter un **filtre agent** sur la vue « Journeys », avec le même effet visuel que le filtre de parcours (RG048) : sous filtre actif, seuls les blocs auxquels l'agent participe restent pleinement visibles (transitions dont les deux blocs sont visibles, participations/relations dont le bloc d'ancrage est visible), les autres sont estompés et non interactifs. Décisions actées séance 04 :

- **Intersection** quand filtre de parcours + filtre agent sont actifs ensemble (RG064).
- Les filtres (parcours **et** agent) ne s'appliquent **pas** à la vue « Agents » (agents de niveau projet) — RG048/FN029 mis à jour.
- Filtre agent désactivé par défaut à l'ouverture, non persisté, ne marque pas modifié (RG047/RG063).

## Plan d'implémentation

1. **`src/core/services/agent_filter_service.py`** (Qt-free, pattern `JourneyFilterService`) : `visible_block_ids(narrative_map, agent_id)` = blocs avec une participation de l'agent (via `ParticipationService`) ; `visible_transition_ids(narrative_map, agent_id)` = transitions dont les deux blocs sont visibles ; `visible_participation_ids` / `visible_relationship_ids` (bloc d'ancrage visible). Opacité réutilisée : `journey_filter_opacity` (config, RG048).
2. **Tests unitaires** (`tests/test_agents/test_agent_filter_service.py`) : visibilité par agent, transitions aux deux extrémités visibles, combinaison avec le filtre de parcours (intersection RG064 — la combinaison vit côté workspace, le service fournit les deux ensembles).
3. **`src/ui/views/journeys_workspace.py`** : généraliser le filtre existant — `journey_filter_active` reste, ajout de `agent_filter_agent_id` (None = off) ; `_item_in_filter(item)` = filtre de parcours (si actif) **ET** filtre agent (si actif, via `AgentFilterService`) ; `set_agent_filter(agent_id_or_None)` ; `apply_journey_filter()` → renommée/généralisée en `apply_filters()` (garder `apply_journey_filter` comme alias ou renommer proprement — code mort interdit). La vue « Agents » (TSK19b) n'appelle pas ces filtres (RG048).
4. **`src/ui/main_window.py`** : menu dynamique `Display › Agent` (pattern `_rebuild_journey_menu`) : « All agents » (`agent_list_all_label` config) cochée par défaut + une entrée cochable par agent ; `self.agent_filter_agent_id` (None = off, RG047 non persisté) ; `_activate_agent` applique `set_agent_filter` + rebuild des deux menus filtres ; `menu_actions['agent_filter']` ajouté à `PROJECT_DEPENDENT` ; à l'ouverture du projet : filtre agent off.
5. **Specs déjà à jour** (séance 04) : FN039, RG063/RG064, RG047/RG048, RG048→vues carte uniquement, `05_menu` Display › Agent, SU006/SU008, matrice de traçabilité (lignes FN039/RG063-067/Display›Agent créées). À compléter après implémentation : statuts `implemented` + références code/tests.

## Vérifications prévues

- `py_compile` sur les fichiers modifiés ; `pytest` : 59 + nouveaux tests du service.
- Smoke offscreen (poste de dev) : filtre agent sur la vue Journeys (estompage), intersection avec le filtre de parcours, menu Display › Agent, non-persistance.

## Journal

- 2026-11-17 : fiche créée au passage en Doing ; conception actée séance 04 (filtre agent type filtre de parcours, intersection RG064, non appliqué à la vue « Agents »).
- 2026-11-17 : **travaux réalisés** — `core/services/agent_filter_service.py` (Qt-free, `filter_opacity()` réutilise `journey_filter_opacity`, `visible_block_ids/transitions/participations/relationships` dérivés des participations via `ParticipationService`, RG041 deux extrémités) + `tests/test_agents/test_agent_filter_service.py` (5 tests : off/all, par agent, transitions deux extrémités, ancrage participations/relations, intersection RG064 avec `JourneyFilterService`) ; `journeys_workspace.py` généralisé (`agent_filter_agent_id`, `_item_in_filter` = ET des filtres actifs, `set_agent_filter()`, `apply_journey_filter()` renommée `apply_filters()` partout) ; `main_window.py` : menu dynamique `Display › Agent` (`_rebuild_agent_menu`, « All agents » via `agent_list_all_label` + une entrée cochable par agent), `_set_agent_filter()`, reset à l'ouverture, rebuild après CRUD agent, `agent_filter` dans `PROJECT_DEPENDENT` ; docstring `journey_filter_service.py` (vues de la carte uniquement) ; matrices FR/EN (RG063/RG064/FN039/Display›Agent → implemented, RG048 → vues carte). py_compile OK, **64 tests passed** ; rendu visuel (estompage, intersection, menu) à valider offscreen sur poste de dev. Passée en Review.
