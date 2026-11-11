# TSK14 — Ports conditionnels Début/Fin dans la vue « Journeys »

- **Créée** : 2026-11-11 — passée en Doing 2026-11-11 (TSK10/TSK11 en Review) — implémentée et passée en Review 2026-11-11
- **Dépendances** : → #TSK10, → #TSK11

## Objectif

Rendre la vue « Journeys » cohérente avec la matrice d'enchaînement RG028 au niveau graphique : **bloc Début sans port entrant, blocs Fin sans port sortant** (ports masqués, pas grisés). Spec déjà actée : `docs/specification/04_interface-FR/EN.md` §4 (lignes « Bloc narratif » et « Transition », commit 7df6c5c). Aucun impact modèle : RG025/RG028 interdisent déjà ces transitions, `CreateTransitionUseCase` les refuse.

## Décisions actées (séance n°03, 11-11-2026)

- Port **masqué** (`hide()`), pas grisé ni supprimé : item caché non hit-testable, `get_left/right_port_position()` conservent leur fallback au bord du nœud (jamais atteint en pratique : un port masqué ne peut jamais être extrémité d'une transition valide).
- Visibilité des ports **dérivée de la matrice RG028** (source de vérité unique) via deux helpers Qt-free dans `transition_service.py` : `type_allows_outgoing(typ)` = `ALLOWED_TARGET_TYPES[typ]` non vide ; `type_allows_incoming(typ)` = `typ` présent dans au moins un ensemble de cibles. Vérification : Start (out ✅ / in ❌), Scene (✅/✅), Pivot (✅/✅), Condition (✅/✅), End (❌/✅).
- La création de transition exige toujours port sortant source → port entrant cible ; un clic près du bord d'un bloc sans le port requis est traité comme **hors port** (spec §4 ligne « Transition »).

## Travaux réalisés (plan suivi tel quel)

1. **`src/core/services/transition_service.py`** (Qt-free) : ajouter `type_allows_incoming(block_type)` et `type_allows_outgoing(block_type)` dérivés de `ALLOWED_TARGET_TYPES` (commentaire RG025/RG028).
2. **`tests/test_transitions/test_transition_service.py`** : tests unitaires des deux helpers pour les 5 types + cohérence avec la matrice (End jamais source, Start jamais cible).
3. **`src/ui/nodes/base_node.py`** : ajouter `has_input_port()` / `has_output_port()` (`self.input_port is not None and self.input_port.isVisible()`). Pas de modification de `_init_ports` ni de `_update_port_positions` (ports toujours créés, masqués après coup).
4. **`src/ui/nodes/block_node.py`** : dans `__init__` après `super().__init__`, masquer selon le type via les helpers : `if not type_allows_incoming(block.typ): self.input_port.hide()` ; idem sortant. Type immuable (RG029) → pas de réévaluation nécessaire.
5. **`src/ui/views/journeys_workspace.py`** `_handle_port_selection` : branche clic sur le corps du nœud — n'accepter le bord droit que si `candidate.has_output_port()` et le bord gauche que si `candidate.has_input_port()` (sinon le clic tombe dans « hors port »). La branche ellipse est sûre telle quelle (un item caché n'est jamais retourné par `items()`).
6. **Smoke offscreen** (jetable, non commité) : compléter `/tmp/offscreen_journeys_smoke.py` — visibilité des ports par type, clic près du port masqué d'un Début/Fin = hors port.

## Vérifications

- `python -m py_compile` sur les 5 fichiers modifiés : OK.
- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` : **45 passed** (44 + `test_tsk14_port_visibility_derived_from_matrix`).
- Grep : ports masqués uniquement via `_apply_conditional_ports()` ; `_init_ports`/`_update_port_positions` inchangés.
- Smoke offscreen TSK14 complété (`/tmp/offscreen_journeys_smoke.py`, non commité) — à exécuter sur poste de dev (libGL absent dans le sandbox).

## Journal

- 2026-11-11 : spec actée (commit 7df6c5c) ; TSK14 passée en Doing, plan rédigé ; go TSC → implémentation (helpers matrice + test, `has_input_port/output_port`, masquage `BlockNode._apply_conditional_ports`, garde-fous `_handle_port_selection`) ; py_compile OK, 45 tests passed ; TSK14 passée en Review ; commit + push sur demande TSC.
