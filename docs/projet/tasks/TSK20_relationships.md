# TSK20 — Relations agent-agent (use cases CRUD + dialogue + menu `Project › Relationships`)

- **Statut** : Doing (19-11-2026) → Review (19-11-2026) ; dépend de #TSK17 (Done), #TSK25 (Review), #TSK26 (Review)
- **Périmètre** : FN034, RG035 (durcie séance 06), SU011, FN037. La vue « Relationships » (SU012/FN036) et son menu contextuel restent **TSK27** (décision TSC séance 08).

## Règles implémentées

- RG035 durcie (séance 06) : relation binaire, **deux agents distincts** (pas d'auto-relation — complément TSC séance 08), non dirigée (paire non ordonnée stockée triée, TSK25), typée (liste `relationship_types` de config.json, FN037), ancrée à exactement un bloc ; **unicité par (bloc, paire)** — le lien bloc–relation est unique pour le MVP.
- FN034/SU011 : création (choix des 2 agents, du type, du bloc d'ancrage), édition (type, bloc d'ancrage, note, contenu — la paire est fixe), suppression avec confirmation ; doublons (bloc, paire) empêchés ; toute opération marque le projet comme modifié.
- Liste des blocs d'ancrage du dialogue ordonnée par **rang minimal sur tous les parcours** (ex æquo par id) — même règle que le panneau de la vue « Relationships » (RG069, décision TSC séance 08).

## Plan suivi

1. Service Qt-free `core/services/relationship_service.py` : types config (FN037), `check_pair` (agents distincts), paire canonique (TSK25), `find_relationship` (unicité (bloc, paire)), `get_block_relationships`/`get_pair_relationships`, `ordered_anchor_block_ids` (rang minimal, RG069 — réutilisé par TSK27).
2. Use cases `usecases/relationship_management/` : create (None si doublon, ValueError si entrée invalide), update (re-vérifie l'unicité si le bloc d'ancrage change), delete.
3. Dialogues `ui/dialogs/` : `relationship_dialog.py` (création/édition ; combos agents désactivés à l'édition), `relationship_selection_dialog.py` (liste « A <-> B @ bloc (type) » pour Edit.../Delete...).
4. Câblage `main_window.py` : `relationships_new/edit/delete` branchés sur les use cases ; `TWO_AGENTS_DEPENDENT` (New... ≥ 2 agents), `RELATIONSHIP_DEPENDENT` (Edit.../Delete... ≥ 1 relation) ; confirmation + info bar.
5. Tests `tests/test_relations/` (12 tests).
6. Spec FR/EN : RG035/SU011/FN034 complétées « deux agents distincts » + ordre de la liste d'ancrage ; matrices `implementation-FR/EN.md`.

## Modifications réalisées

- `src/core/services/relationship_service.py` (nouveau).
- `src/usecases/relationship_management/` : `__init__.py`, `create_`/`update_`/`delete_relationship_usecase.py` (nouveaux).
- `src/ui/dialogs/relationship_dialog.py`, `relationship_selection_dialog.py` (nouveaux) + exports `ui/dialogs/__init__.py`.
- `src/ui/main_window.py` : imports, 3 use cases instanciés, entrées menu câblées, `TWO_AGENTS_DEPENDENT`/`RELATIONSHIP_DEPENDENT` + `_update_menu_state`, méthodes `_select_relationship`/`_new_relationship`/`_edit_relationship`/`_delete_relationship`.
- `tests/test_relations/` : `__init__.py`, `test_relationship_service.py` (4 tests), `test_relationship_usecases.py` (8 tests).
- Spec FR/EN : RG035, SU011, FN034 (deux agents distincts ; ordre liste d'ancrage RG069) ; matrices RG035/FN034/FN037/SU011 → implemented, entrées menu `relationships_*` → implemented.
- Cascades RG023 (bloc) et RG033 (agent) déjà en place (`transition_service.delete_block_cascade`, `participation_service.cascade_delete_agent`) — vérifiées, aucun changement.

## Journal

- 2026-11-19 : passée en Doing (TSK17 Done ; TSK25/TSK26 en Review). Implémentation + tests : py_compile OK, **88 tests passed + 2 skipped** (offscreen Qt skippés sans libGL — à valider sur poste de dev). Passée en Review 19-11-2026. Hors périmètre acté : vue et menu contextuel « Relationships » → TSK27.
