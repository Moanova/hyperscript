# TSK26 — Règle RG068 : le bloc Start appartient à tous les parcours (rattachement non modifiable)

- **Statut** : Doing (19-11-2026) → Review (19-11-2026) ; dépend de #TSK09 (Done) ; TSK20 en dépend (→ #TSK26)
- **Origine** : décision TSC séance 06 (2026-11-19), pendant la conception de la vue « Relationships » (SU012) : la vue sélectionne le bloc Start par défaut, ce qui suppose qu'il appartienne à tous les parcours (sinon il serait hors filtre actif). RG068 rédigée dans `02_business_rules` FR/EN (séance 06), RG042 complétée (liste désactivée pour le Start).

## Règle actée (RG068, séance 06)

- Le bloc Début appartient à **tous les parcours** de la carte narrative ; l'auteur ne peut jamais modifier ce rattachement.
- À la création d'un parcours, le bloc Début y est automatiquement rattaché.
- Dans le dialogue d'édition du bloc Début, la liste des parcours est désactivée (RG042).
- La suppression d'un parcours ne le concerne jamais (RG034).

## Plan d'implémentation

1. `core/services/journey_service.py` — `set_block_attachments` : garde RG068 (si le bloc est Start, la liste cible doit contenir tous les parcours de la carte, sinon `ValueError`).
2. `usecases/journey_management/create_journey_usecase.py` — rattacher le Start au nouveau parcours + `JourneySequenceService.recompute_journey` (RG044).
3. `ui/dialogs/block_dialog.py` — liste des parcours désactivée aussi quand `block.typ == "Start"`.
4. Tests unitaires `tests/test_journeys/test_journey_usecases.py` : 3 tests `test_rg068_*`.
5. Aucun changement sur `duplicate_journey_usecase` (RG043 : le Start étant partout, il est copié avec) ni `delete_journey_usecase` (RG034 : ne concerne jamais le Start) — vérifié.
6. Matrices `implementation-FR/EN.md` : ligne RG068 → `implemented`.

## Modifications réalisées

- `src/core/services/journey_service.py` : garde RG068 dans `set_block_attachments` (docstring mise à jour).
- `src/usecases/journey_management/create_journey_usecase.py` : rattachement auto du Start au nouveau parcours + recompute RG044 ; imports `JourneyService`/`JourneySequenceService`.
- `src/ui/dialogs/block_dialog.py` : `journeys_list.setEnabled(False)` aussi pour le bloc Start (RG068), en plus du cas « un seul parcours » (RG042).
- `tests/test_journeys/test_journey_usecases.py` : `import pytest` + 3 tests (`test_rg068_start_attached_to_every_new_journey`, `test_rg068_start_attachments_not_editable`, `test_rg068_start_kept_when_journey_deleted`) ; docstring mise à jour.
- Kanban : TSK26 créée en To do (séance 06) → Doing → Review ; TSK20 → #TSK26 ; matrices RG068 `implemented`.

## Journal

- 2026-11-19 : tâche passée en Doing (TSK09 Done). Implémentation et tests réalisés : py_compile OK, **76 tests passed + 2 skipped** (offscreen Qt skippés sans libGL — à valider sur poste de dev, conforme aux séances précédentes). Passée en Review 19-11-2026.
