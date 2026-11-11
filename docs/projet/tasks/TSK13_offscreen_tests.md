# TSK13 — Tests offscreen de la vue « Journeys » + matrice de traçabilité

- **Créée** : 2026-11-11 — passée en Doing 2026-11-11 (TSK08–TSK12 en Review) — implémentée et passée en Review 2026-11-11
- **Dépendances** : → #TSK11, → #TSK12

## Objectif

Valider la vue « Journeys » par tests ciblés offscreen (scripts jetables, non commités — AGENTS.md) et mettre à jour la matrice de traçabilité `docs/projet/implementation-FR/EN.md`.

## Travaux réalisés

- **Matrice de traçabilité** FR/EN mise à jour (script ciblé par ID) : RG implémentées/testées (RG023–RG029, RG030/031 via la matrice, RG034, RG038–RG041, RG043, RG044, RG058, RG062), RG partielles visuelles (RG046, RG048–RG050, RG053–RG055, RG060 — code présent, rendu à valider offscreen), FN014–FN027/FN035, FN028/FN029 partielles, entrées de menu câblées (`blocks_*`, `transitions_*`, `journeys_*`, `Display > Journey`) vs stubs conservés (`agents_*`, `relationships_*`, `view_*`), SU003/SU006 partial, SU004/SU005 implemented.
- **Smoke offscreen** : script jetable `/tmp/offscreen_journeys_smoke.py` (non commité) — instancie `JourneysWorkspace` offscreen, peuple depuis le modèle, crée un bloc via le use case, vérifie que le nœud affiche le **type** et l'infobulle le **libellé**, crée une transition Start→Scene, vérifie le refus Start→End (matrice RG028), bascule le filtre. **Non exécutable dans le sandbox** (`ImportError: libGL.so.1`) — à lancer sur le poste de dev : `QT_QPA_PLATFORM=offscreen python /tmp/offscreen_journeys_smoke.py`.
- Tests unitaires : complétés (FN021/FN022 + RG029) → **44 passed**.

## Vérifications

- `python -m py_compile` sur tout `src/` : OK.
- Imports locaux résolus (vérification AST) : OK.
- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` : **44 passed**.
- Smoke Qt offscreen : bloqué dans le sandbox (libGL.so.1 absent, pas de droits root) — script prêt, à valider sur poste de dev avec `python src/main.py` (test manuel TSC).

## Journal

- 2026-11-11 : matrice FR/EN mise à jour ; tests unitaires complétés (44 passed) ; smoke offscreen rédigé et tenté (bloqué libGL, noté). TSK13 passée en Review.
