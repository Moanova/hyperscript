# TSK16 — Retours de tests visuels TSC (couleurs, libellés, position Start, dialogue)

- **Créée** : 2026-11-17 — passée en Doing 2026-11-17 (TSK10/TSK11/TSK12 en Review)
- **Dépendances** : → #TSK10, → #TSK11, → #TSK12

## Objectif

Prendre en compte les premiers retours de tests manuels TSC sur la version en cours (séance n°04, 17-11-2026) : nouvelle palette (sable/or/rouge), position du bloc Start à la création de la carte, tirets de sélection plus courts, survol des transitions en sable fixe, renommages de menus, suppression de la ligne « Type » du dialogue d'édition.

## Grille de lecture des couleurs (actée)

| Terme TSC | Hex | Clé config |
|---|---|---|
| vert | `#A7C957` | `block_scene_color` (avant) |
| sable | `#E5C07B` | `block_start_color` (avant) |
| or | `#D19A66` | `block_pivot_color` (avant) |
| rouge | `#E06666` | `block_condition_color` |
| blanc | `#F0F0F0` | `block_ending_color` (avant) |

## Décisions actées (séance n°04, 17-11-2026)

- Point 14 (infobulle « libellé + note ») **ignoré** : déjà implémenté (`base_node.py` `update_entity_data`, RG054) — à vérifier visuellement, pas de changement de code.
- Point 6 **validé** : Pivot et Condition auront le même contour `#E06666` (rouge) ; ils restent distingués par le type affiché dans le nœud.
- Badges de participation (`badge_*_color`) : **hors périmètre**, revus avec la logique des agents.
- Les retours « vert → sable » (lien accueil, scrollbars, soulignement d'onglet, contour Scène) suivent automatiquement le changement de `block_scene_color` → `#E5C07B` (usages existants de `BLOCK_SCENE_COLOR`).
- Point 3 : position du bloc Start à la création de la carte = x `grid_major_size` (80, bord gauche + un pas majeur), y = centre de la scène + (`grid_major_size` − hauteur du nœud)/2 = 2020 (bloc de 40 px centré dans le pas majeur [2000, 2080]), snappé grille (RG046).

## Plan d'implémentation

1. `src/config/config.json` : `block_start_color` `#D19A66`, `block_scene_color` `#E5C07B`, `block_pivot_color` `#E06666`, `block_ending_color` `#E5C07B` (`block_condition_color` inchangé) ; nouvelles clés `connection_hover_color: "#E5C07B"` et `selection_dash_pattern: [4.0, 4.0]`.
2. `src/ui/utils/theme.py` : fallbacks des 5 couleurs de type alignés sur config.json (les fallbacks Scène/Condition étaient incohérents) + constante `CONNECTION_HOVER_COLOR` ; commentaire de palette mis à jour.
3. `src/ui/nodes/base_node.py` : tirets de sélection lus dans config (`selection_dash_pattern`, ex. `[6.0, 4.0]` → `[4.0, 4.0]`) via une constante de classe.
4. `src/ui/nodes/connection.py` : survol = trait plein en `connection_hover_color` (sable fixe) au lieu de la teinte du type du premier bloc ; `_type_tint_color()` supprimé (code mort), commentaires de classe mis à jour.
5. `src/ui/views/journeys_workspace.py` `populate_default()` : le bloc Start (création de la carte) est placé au bord gauche + un pas majeur, centré verticalement dans un pas majeur ; les autres blocs gardent la colonne centrale.
6. `src/ui/main_window.py` : menu `Project > Blocks` (ex-« Narrative Blocks ») ; menu contextuel sur la grille : sous-menu « New Block » + action dédiée « New Transition » (mêmes handlers que le menu applicatif) ; commentaire aligné.
7. `src/ui/dialogs/block_dialog.py` : suppression de la ligne « Type: » (RG029 : type immuable, déjà porté par le titre de la fenêtre) + docstring.
8. Specs FR/EN : `05_menu-EN/FR.yaml` (nom « Blocks »/« Blocs », section `context_menu` explicitée), `02_business_rules` RG055 (libellés propres autorisés dans le menu contextuel), `03_features` (références « Project › Blocks › … »), `04_interface` §2 (palette actée avec termes TSC), `docs/projet/implementation-FR/EN.md` (lignes de menu).

## Travaux réalisés

1. `src/config/config.json` : `block_start_color` `#D19A66`, `block_scene_color` `#E5C07B`, `block_pivot_color` `#E06666`, `block_ending_color` `#E5C07B` (`block_condition_color` `#E06666` inchangé) ; nouvelles clés `connection_hover_color: "#E5C07B"` et `node_selection_dash_pattern: [4.0, 4.0]`.
2. `src/ui/utils/theme.py` : fallbacks des 5 couleurs de type alignés sur config.json (les fallbacks Scène `#E5C07B` / Condition `#D19A66` étaient incohérents avec config) + constante `CONNECTION_HOVER_COLOR` ; commentaire de palette mis à jour (sable/or/rouge, Pivot = Condition volontairement).
3. `src/ui/nodes/base_node.py` : constante de classe `SELECTION_DASH_PATTERN` (config `node_selection_dash_pattern`), utilisée par `_apply_outline()` à la place du `[6.0, 4.0]` en dur ; docstring ajusté.
4. `src/ui/nodes/connection.py` : `HOVER_COLOR = theme.color("connection_hover_color", ...)` ; `_hover_pen()` en sable fixe ; `_type_tint_color()` supprimé (code mort) ; commentaires de classe et de `hoverEnterEvent` ajustés.
5. `src/ui/views/journeys_workspace.py` `populate_default()` : le bloc Start est placé à x = `grid_major_size` snappé (80), y = centre de la scène + (`grid_major_size` − `node_default_height`)/2 snappé → (80, 2020) pour une scène 4000×4000 ; les autres blocs gardent la colonne centrale (1800, 1800 + i·120).
6. `src/ui/main_window.py` : menu `Project > Blocks` (ex-« Narrative Blocks ») ; menu contextuel sur la grille vide : sous-menu « New Block » (4 types, actions du menu applicatif) + action dédiée « New Transition » → `self._start_transition_creation`.
7. `src/ui/dialogs/block_dialog.py` : ligne « Type: » supprimée (RG029 ; le titre « Edit Block ({typ}) » conserve le rappel) + docstring.
8. Spécifications FR/EN mises à jour : `05_menu-EN/FR.yaml` (« Blocks »/« Blocs », section `context_menu` explicitée avec « New Block » / « New Transition »), `02_business_rules` RG055 (libellés propres autorisés sur la grille vide), `03_features` (références « Project › Blocks › … »), `04_interface` §2 (palette actée + ligne accents), §3 (soulignement d'onglet), §4 (position par défaut du Début, tirets de sélection, survol des transitions, menus contextuels), §9 (lien d'accueil), point ouvert n°1 ; `docs/projet/implementation-FR/EN.md` (lignes FN014/FN015/FN018 + table des menus).
9. Point 14 (infobulle libellé + note) : **ignoré** selon décision TSC — déjà implémenté (`base_node.py` `update_entity_data`, RG054).

## Vérifications

- `python -m py_compile` sur les 6 fichiers Python modifiés : OK ; `json.tool` sur `config.json` : OK ; `yaml.safe_load` sur `05_menu-EN/FR.yaml` : OK.
- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` : **45 passed**.
- Vérification hors-ligne (config + `LayoutService`, Qt-free) : palette = `#D19A66/#E5C07B/#E06666/#E06666/#E5C07B`, `connection_hover_color` `#E5C07B`, `node_selection_dash_pattern` `[4.0, 4.0]` ; position Start calculée = (80, 2020).
- Smoke offscreen Qt (rendu QImage : bloc sélectionné, survol de transition, page d'accueil, onglet actif, menu contextuel, dialogue sans ligne Type, position du Start) : **à exécuter sur le poste de dev** (libGL absent dans le sandbox, PySide6 non importable ici).

## Journal

- 2026-11-17 : fiche créée au passage en Doing ; plan établi d'après l'analyse des retours TSC (séance n°04). Implémentation réalisée dans la foulée (points 1-13 hors point 14 ignoré), tests 45 passed, tâche passée en Review.
