# TSK28 — Évolutions mineures (demande TSC séance 09)

- **Statut** : Doing (19-11-2026) → Review (19-11-2026) ; dépend de #TSK27 (Review)

## Évolutions actées (TSC, séance 09)

1. **Ordre des vues inversé : « Agents » avant « Journeys »** dans la barre d'onglets. La **vue active par défaut reste « Journeys »** (inchangé, `04_interface` §3).
2. **Type « Undefined »** ajouté en tête de la liste des types de relations (type par défaut « non précisé »), avec sa couleur.

## Modifications réalisées

- `src/ui/main_window.py` : `TabBar(["Agents", "Journeys", "Relationships", "Export"])`.
- `src/config/config.json` : `relationship_types` = `["Undefined", "friend", "ally", "rival", "enemy", "romantic", "family"]` ; `relationship_type_colors` += `"Undefined": "#9E9E9E"`.
- Spec FR/EN : `04_interface` §3 (ordre d'affichage inversé, défaut inchangé, note TSK28) ; `05_menu` FR/EN (sous-menu Vue : Agents avant Parcours/Journeys, notes TSK28).
- Test : `tests/test_relations/test_relationship_service.py` (`test_fn037_types_read_from_config` : « Undefined » en tête, valide).
- Matrices `implementation-FR/EN.md` : entrées `Projet/Project › Vue › Agents` et `Parcours/Journeys` inversées + notes TSK28.

## Journal

- 2026-11-19 : passée en Doing (TSK27 en Review). Modifications réalisées ; config JSON valide ; py_compile OK ; **93 tests passed + 4 skipped** (offscreen Qt sans libGL — à valider sur poste de dev). Passée en Review 19-11-2026.
