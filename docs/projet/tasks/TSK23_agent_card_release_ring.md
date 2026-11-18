# TSK23 — Dépôt d'une carte contraint à l'anneau de la boîte englobante

- **Statut** : Doing (18-11-2026) → dépend de #TSK22 (en Review)
- **Origine** : retour TSC séance 05 (2026-11-18) : après TSK21/TSK22, l'utilisateur peut encore déposer une carte dans une cellule isolée, non adjacente au groupe. Ce n'est pas un bug de la boîte englobante (celle-ci est calculée sur les positions courantes à la création) : le dépôt était volontairement libre. TSC choisit la contrainte par boîte englobante (option 2) plutôt que l'adjacence à une carte (option 1) pour éviter le cas particulier de la carte unique.

## Décision actée (feu vert TSC)

- **RG065 (évolution TSK23)** : à la libération d'un déplacement, la cellule de dépôt doit se trouver dans la **boîte englobante des autres cartes élargie d'une cellule** de chaque côté (anneau de 1 cellule) ; la boîte du groupe ne peut donc grandir que d'une cellule par déplacement. Si la cellule visée est hors de cette zone (ou occupée), la carte est ramenée sur la **cellule libre la plus proche dans la zone autorisée** (intersection avec les limites de la scène).
- **Carte unique** : aucune autre carte → aucune contrainte, placement libre sur n'importe quelle cellule (évite le cas particulier signalé par TSC).
- La création (TSK22, ancre à droite de la boîte englobante) reste inchangée.

## Plan d'implémentation

1. `src/ui/nodes/agent_card.py` v3 : `_cell_snap_target` — bornes effectives = intersection limites scène × (boîte englobante des autres cartes + 1 cellule) quand il y a d'autres cartes ; snap cellule, clamp dans ces bornes, puis `find_nearest_free_position` avec ces bornes.
2. Tests offscreen v4 : drag lointain ramené dans l'anneau (ex. (200, 280) au lieu de (3200, 3080)), carte unique déplacée librement loin, création à côté du groupe déplacé dans la zone autorisée, tests existants re-vérifiés.
3. Spec FR/EN : RG065 (+ phrase dépôt contraint), `04_interface` §5, matrices ; kanban TSK23 Doing → Review.

## Journal

- 2026-11-18 : tâche créée et passée en Doing (TSK22 en Review). Option 2 retenue (boîte englobante des autres cartes + anneau d'une cellule) ; l'option 1 (adjacence à une carte) écartée à cause du cas carte unique.
- 2026-11-18 : **travaux réalisés** — `agent_card.py` v3 : `_cell_snap_target` calcule les bornes effectives = limites scène ∩ (boîte englobante des autres cartes + 1 cellule de chaque côté ; aucune autre carte → scène entière), clamp du snap cellule dans ces bornes, puis `find_nearest_free_position` avec ces bornes. Tests offscreen v4 : +2 tests (drag lointain (3000,3000) ramené à (200, 280) dans l'anneau ; carte unique déplacée librement à (1000, 980)), test TSK22 ajusté (déplacement dans la zone autorisée → création à (600, 140)) ; valeurs attendues vérifiées hors Qt via `LayoutService` (snap_to_grid/find_nearest_free_position). Spec FR/EN : RG065 (+ phrase dépôt contraint), 04_interface §5, matrices. py_compile OK, **73 tests passed + 1 skipped** (offscreen Qt skippé sans libGL dans le sandbox — à valider sur poste de dev). Passée en Review.
