# TSK25 — Relation agent-agent non dirigée (révision RG035 / modèle de données)

- **Statut** : Doing (18-11-2026) → dépend de #TSK01 (Done) ; TSK20 (relations CRUD) en dépend
- **Origine** : décision TSC séance 05 (2026-11-18), pendant la conception de la vue « Relationships » (SU012) : aucune justification documentée de la directivité (RG035 « dirigée » actée en preconception sans « parce que » ; seule trace sémantique : l'exemple « A —type→ B ») ; la liste de types MVP (`relationship_types` : friend, ally, rival, enemy, romantic, family) est entièrement symétrique ; l'unicité RG035 portait déjà sur une paire non ordonnée. → levée de la contrainte de directivité.

## Décision actée (TSC)

- La relation entre deux agents est **non dirigée** : la paire est non ordonnée, stockée de façon canonique triée (`agent_1_id` < `agent_2_id`), donc (A, B) = (B, A).
- Si un type asymétrique devait apparaître post-MVP (mentor, dette…), une orientation optionnelle pourra être réintroduite sans casser le modèle de paire.
- Conséquence pour la vue « Relationships » (SU012) : arêtes **non dirigées** entre agents.

## Modifications réalisées

- `src/core/models/data_model.py` : `Relationship` — champs `agent_a_id`/`agent_b_id` renommés `agent_1_id`/`agent_2_id`, `__post_init__` canonicalise la paire (tri), docstring mise à jour.
- `src/core/services/participation_service.py` : cascade RG033 et `get_agent_relationships` sur les nouveaux champs.
- Tests : 3 fixtures renommées (`test_transition_service.py`, `test_journey_filter_service.py`, `test_agent_usecases.py`).
- Spec FR/EN : RG035 (`02_business_rules`), SU011 (`01_user_stories` + exemple « relation de ce type entre A et B »), FN034 (`03_features`), `07_data_model` JSON (champs `agent_1_id`/`agent_2_id`, descriptions, required), conception (`03_conception` §3 et précisions), matrices `implementation-FR/EN.md` (ligne RG035).
- Kanban : TSK25 créée en Doing ; TSK20 dépend désormais de #TSK25.
- Aucun projet sauvegardé ne contient de relations (fonctionnalité non implémentée) : aucun impact de migration.

## Journal

- 2026-11-18 : tâche créée et passée en Doing (TSK01 Done). Toutes les modifications ci-dessus réalisées : JSON des data models valides, py_compile OK, **73 tests passed + 2 skipped** (offscreen Qt skippés sans libGL). Aucune occurrence résiduelle de `agent_a_id`/`agent_b_id` hors fiches historiques (TSK01 annotée). Passée en Review 18-11-2026.
