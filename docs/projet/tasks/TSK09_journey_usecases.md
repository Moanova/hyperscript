# TSK09 — Use cases de gestion des parcours

- **Créée** : 2026-11-11 — passée en Doing 2026-11-11 (TSK08 en Review) — implémentée et passée en Review 2026-11-11
- **Dépendances** : → #TSK08 (services `journey_service`, `journey_sequence_service` en place)

## Objectif

Use cases du package `src/usecases/journey_management/` (reprise adaptée de planoscript, vocabulaire hyperscript) + tests unitaires. Couverture : FN023–FN027, FN038 et RG024, RG034, RG038, RG039, RG043, RG062.

- **Références** : SU005 ; FN023–FN027, FN038 ; RG024, RG034, RG038, RG039, RG043, RG062 ; conception §3/§4 ; séance 03 (création d'un parcours n'active rien — SU005/FN023 révisés séance 02).

## Plan d'implémentation

Package `src/usecases/journey_management/` (Qt-free) :

1. `create_journey_usecase.py` (FN023) : `execute(lb=None, note=None) -> Journey` — nouvel id, lb par défaut « Journey {id} », `default=False`, **non activé** (le parcours actif reste inchangé) ; `set_modified(True)`.
2. `update_journey_usecase.py` (FN024) : `execute(journey, lb=None, note=None)` — libellé et note éditables ; modifié.
3. `activate_journey_usecase.py` (FN026) : `execute(journey)` — `narrative_map.active_journey_id = journey.id` ; modifié.
4. `set_default_journey_usecase.py` (FN038/RG062) : `execute(journey)` — retire le flag `default` du parcours par défaut courant, le pose sur la cible ; **ne modifie pas** `active_journey_id` ; un seul default à tout moment (RG039) ; modifié.
5. `duplicate_journey_usecase.py` (FN025/RG043/RG038) : `execute(journey)` — nouvel id, lb « {lb} (copy) », `default=False`, **non activé** ; copie les rattachements des blocs du parcours source (nouveaux `Journey_node` vers la copie) ; `recompute_all` (RG044) ; modifié.
6. `delete_journey_usecase.py` (FN027) : `execute(journey) -> dict` —
   - RG024 : dernier parcours → `{'success': False, 'reason': 'last_journey'}`, rien n'est modifié (le message explicatif est du ressort de l'UI) ;
   - RG034 : pour chaque `journey_node` du parcours supprimé, si le bloc n'est rattaché à aucun autre parcours, le node est **réaffecté au parcours par défaut** (aucun bloc orphelin), sinon supprimé ;
   - RG039 : si le supprimé était `default`, le plus ancien parcours restant devient default ; si c'était l'actif, le default devient l'actif ;
   - `recompute_all` (RG044) ; modifié.
7. **Non repris de planoscript** : `attach_relation_to_journey_usecase` / `detach_relation_from_journey_usecase` — dans hyperscript le rattachement est sur les **blocs** (RG041), géré par `UpdateBlockUseCase(journey_ids=...)` (RG042, TSK08).

Tests `tests/test_journeys/test_journey_usecases.py` (noms `test_fn02x_*` / `test_rg0xx_*`) : création non activée + modified ; édition ; activation ; set-default (actif inchangé, un seul default) ; duplication (rattachements copiés, non activée RG038) ; suppression (dernier refusé RG024 ; réaffectation RG034 ; default/actif RG039) ; recompute RG044 après chaque opération.

## Vérifications

- `python -m py_compile` sur tous les fichiers créés : OK.
- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` : **40 passed** (33 TSK08 + 7 nouveaux FN023–FN027/FN038).
- Aucun import Qt dans `src/usecases/` (grep).

## Journal

- 2026-11-11 : fiche rédigée au passage en Doing.
- 2026-11-11 : implémentation des 6 use cases + tests ; 40 tests passed. Note : `attach/detach_relation_to_journey_usecase` de planoscript volontairement non repris (rattachement sur les blocs, RG041 — couvert par `UpdateBlockUseCase`, RG042). TSK09 passée en Review.
