# TSK08 — Services et use cases de la carte narrative

- **Créée** : 2026-11-11 — passée en Doing 2026-11-11 (TSK07 en Review) — implémentée et passée en Review 2026-11-11
- **Dépendances** : → #TSK07 (squelette code, modèles `data_model`/`view_model`, `project_service`, `layout_service` en place)

## Objectif

Fournir la couche métier de la carte narrative consommée par la vue « Journeys » (TSK10/TSK11) et les vues suivantes, **sans aucune dépendance Qt dans `src/core/` et `src/usecases/`** (RG058) :

- `transition_service.py` : matrice d'enchaînement RG028, unicité par paire ordonnée, cascades RG023 ;
- `journey_sequence_service.py` : séquence de lecture DFS RG044 ;
- `journey_filter_service.py` : appartenance dérivée RG041 + visibilité RG048 ;
- `participation_badge_service.py` : logique du badge de participations (Qt-free, testable) ;
- use cases `view_management/` : création/édition/duplication/suppression de blocs et de transitions ;
- tests unitaires associés.

- **Références** : SU003/SU004/SU006 ; FN014–FN022, FN028/FN029 ; RG023, RG025–RG031, RG040–RG044, RG047, RG048, RG058 ; `docs/conception/03_conception-*.md` §3/§4 (matrice actée séance 03) ; `docs/specification/04_interface-*.md` §4.

## Points actés à prendre en compte (séance 03)

- **Matrice d'enchaînement RG028** : Début → {Scène, Pivot} ; Scène → {Scène, Pivot, Fin} ; Pivot → {Condition} ; Condition → {Scène, Fin} ; Fin → aucune transition sortante. Cycles autorisés (ex. Scène → Pivot → Condition → la même Scène). **Ne pas reprendre** de planoscript : `ArcService.would_create_cycle` (interdiction de cycle) et la promotion Scène → Pivot (supprimée).
- **Appartenance dérivée RG041** : le rattachement est stocké sur les blocs uniquement (`Journey_node`) ; une transition appartient à un parcours ssi ses deux blocs y appartiennent, une participation/relation ssi son bloc d'ancrage y appartient. Aucune donnée de rattachement sur les transitions.
- **Rattachement des nouveaux blocs RG040** : parcours actif si le filtre de parcours est activé, parcours par défaut sinon. Le flag « filtre actif » est un état de session UI non persisté (RG047) : passé **en paramètre** aux use cases, jamais lu depuis le modèle.
- **Filtre RG048/FN029** : désactivé par défaut à l'ouverture d'un projet, non persisté, ne marque pas la carte modifiée ; opacité des éléments estompés lue en configuration → **ajouter la clé `journey_filter_opacity` (0.25) dans `src/config/config.json`** (RG059).
- **RG058** : toute modification du modèle passe par use cases/services — ne pas reprendre `Connection.create_arc_or_association` / `delete_arc_or_association` de planoscript (écriture directe du modèle depuis l'UI, bug `connection.py:811`).
- **Badge de participations** : comportement plano conservé tel quel (masqué à 0, « 9+ » au-delà de 9, ligne « Agents: … » en infobulle, max 3 noms puis « +n more »), dans un service Qt-free ; remplissage fixe `badge_bg_color` quelle que soit la couleur du type.
- Le type d'un bloc est immuable (RG029) ; Start unique, auto-créé, jamais supprimable ni duplicable (RG025).

## Plan d'implémentation

### 1. `src/core/services/transition_service.py` (nouveau)

- `ALLOWED_TARGET_TYPES = {"Start": {"Scene", "Pivot"}, "Scene": {"Scene", "Pivot", "End"}, "Pivot": {"Condition"}, "Condition": {"Scene", "End"}, "End": set()}` — `# RG028:` en commentaire.
- `can_create_transition(narrative_map, from_block_id, to_block_id) -> bool` : blocs existants, type de la cible autorisé par la matrice pour le type de la source, aucune transition existante pour la paire ordonnée (unicité, RG028).
- `create_transition(narrative_map, from_block_id, to_block_id, note=None) -> Optional[Transition]` : retourne None si refusé ; sinon crée la `Transition` (id via `narrative_map.get_next_id('transition')`) et marque le projet modifié via `ProjectService.set_modified(True)` (hook `on_modified` déjà câblé dans MainWindow).
- `delete_transition(narrative_map, transition_id)` : suppression simple — avec RG041, aucun `journey_node` ne référence une transition.
- `delete_block_cascade(narrative_map, block_id) -> dict` (RG023) : supprime le bloc, ses transitions entrantes et sortantes, ses participations, ses relations ancrées et ses `journey_node` ; retourne le détail des suppressions pour le message d'information (FN018).
- Helpers `transitions_from(narrative_map, block_id)` / `transitions_to(...)` (utilisés par la séquence et le filtre).

### 2. `src/core/services/journey_sequence_service.py` (nouveau)

- `recompute_all(narrative_map)` et `recompute_journey(narrative_map, journey_id)` — `# RG044:` : DFS depuis l'unique bloc Start (RG025), en ne suivant que les transitions du parcours (deux blocs rattachés à ce parcours, RG041), branches explorées par id de transition **croissant**, mémoïsation des cycles, repli déterministe (ordre de création) pour les blocs inatteignables ; écrit `sequence_order` sur les `journey_node` du parcours. Recalcul à chaque modification du graphe et au chargement du projet (RG044).

### 3. `src/core/services/journey_filter_service.py` (nouveau, Qt-free)

- `visible_block_ids(narrative_map, journey_id=None)` : None = tous les blocs ; sinon uniquement les blocs rattachés au parcours.
- `visible_transition_ids(...)` : transitions dont **les deux** blocs sont visibles (RG041).
- `visible_participation_ids(...)` / `visible_relationship_ids(...)` : élément visible ssi son bloc d'ancrage est visible (RG041).
- Opacité des éléments estompés lue via `config_loader.get("journey_filter_opacity", 0.25)` (RG048/RG059).

### 4. `src/core/services/participation_badge_service.py` (nouveau, Qt-free)

- Reprise de plano `agent_badge_service.AgentBadgeService`, renommé : `badge_visible(count)` (count > 0), `badge_text(count)` (« 9+ » au-delà de `BADGE_MAX_DISPLAY_COUNT = 9`), `tooltip_agents_line(labels)` (« Agents: a, b, c +n more », `TOOLTIP_MAX_NAMES = 3`).

### 5. `src/usecases/view_management/` (nouveau package)

- `create_block_usecase.py` (FN014) : `execute(typ, lb=None, filter_active=False)` — typ ∈ BLOCK_TYPES \ {"Start"} (RG025) ; lb par défaut = nom du type ; rattachement RG040 : parcours actif (`narrative_map.get_active_journey()`) si `filter_active`, parcours par défaut (`default=True`) sinon ; crée le `Journey_node` correspondant, puis recalcule la séquence (RG044). Le use case ne touche qu'au modèle (la position x/y est du layout, TSK11).
- `update_block_usecase.py` (FN015, RG042) : `execute(block, lb, note, content, condition=None, journey_ids=None)` — typ non modifiable (RG029) ; `condition` accepté uniquement si `typ == "Condition"` (validation déjà dans `Block.__post_init__`, FN035) ; `journey_ids` : liste cochée des parcours, **non vidable** (le dernier est conservé), option désactivée côté dialogue si un seul parcours (RG042).
- `duplicate_block_usecase.py` (FN016) : nouvel id, lb « {lb} (copy) » (application unilingue anglais), rattachement RG040 ; Start non duplicable (RG025).
- `delete_block_usecase.py` (FN018) : Start non supprimable (RG025) ; cascade via `transition_service.delete_block_cascade` (RG023) ; retourne le détail pour la confirmation UI.
- `create_transition_usecase.py` (FN020) : délègue à `transition_service.can_create_transition` / `create_transition` ; marque modifié.
- `update_transition_usecase.py` (FN021) : note uniquement — **pas de condition sur la transition** (portée par le bloc Condition).
- `delete_transition_usecase.py` (FN022) : suppression + modifié (la confirmation est du ressort de l'UI).
- `__init__.py` : exporte les use cases (pattern des packages existants).

### 6. Configuration

- Ajouter `"journey_filter_opacity": 0.25` dans `src/config/config.json` (RG048).

### 7. Tests unitaires (nouveaux, sans Qt)

- `tests/test_transitions/test_transition_service.py` : matrice RG028 (chaque paire autorisée / interdite — ex. Début→Fin refusé, Fin→x refusé, Condition→Condition refusé, Début→Pivot et Condition→Fin **autorisés**), unicité par paire ordonnée, cycles autorisés (Scène→Pivot→Condition→Scène), cascade RG023, suppression de transition. Noms `test_rg028_*`, `test_rg023_*`.
- `tests/test_journeys/test_journey_sequence_service.py` : DFS depuis Start, branches par id de transition croissant, mémoïsation des cycles, repli déterministe des blocs inatteignables (RG044) — `test_rg044_*`.
- `tests/test_journeys/test_journey_filter_service.py` : visibilité dérivée blocs/transitions/participations (RG041), filtre désactivé = tout visible (RG048).
- `tests/test_blocks/test_block_usecases.py` : création (typ choisi, immuable RG029 ; Start non créable RG025), rattachement RG040 (filtre actif → parcours actif, sinon défaut), édition (condition uniquement sur Condition), duplication (Start non duplicable, suffixe « (copy) »), suppression (Start interdite, cascade RG023).
- `tests/test_blocks/test_participation_badge_service.py` : `badge_visible`, « 9+ », ligne « Agents: … ».
- `tests/conftest.py` : fixture de projet neuf via `CreateProjectUseCase` (déjà en place, à étendre si besoin).

## Hors périmètre TSK08

- Nœuds et workspace (UI) : TSK10/TSK11. Use cases de gestion des parcours (`journey_management`) : TSK09. Dialogues et câblage des menus : TSK12. Tests offscreen UI : TSK13.

## Point de spécification à corriger (à traiter avec TSK09)

- SU004 / FN022 : « la suppression d'une transition supprime ses rattachements aux parcours » est un **résidu planoscript** — avec RG041 l'appartenance est dérivée (rattachements sur les blocs uniquement), il n'y a rien à supprimer côté parcours. À aligner dans `01_user_stories` / `03_features` FR/EN.

## Critères de sortie

- `python -m py_compile` sur tous les fichiers créés/modifiés : OK.
- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` : 8 tests existants + nouveaux tests, tous passants.
- Aucun import Qt dans `src/core/` et `src/usecases/` (vérifiable par grep).
- Commentaires d'ID `# RGxxx:` / `# FNxxx:` présents sur chaque règle/fonctionnalité implémentée (convention de la matrice de traçabilité).

## Vérifications

- `python -m py_compile` sur tous les fichiers créés : OK.
- `QT_QPA_PLATFORM=offscreen python -m pytest tests/ -q` : **33 passed** (8 TSK07 + 25 nouveaux : matrice RG028, unicité, cycles, cascade RG023, séquence RG044, filtre RG041/RG048, use cases blocs FN014–FN018, badge).
- Aucun import Qt dans `src/core/` et `src/usecases/` (vérifié par grep) — RG058.
- `journey_filter_opacity: 0.25` ajouté dans `src/config/config.json` (RG048).

## Journal

- 2026-11-11 : rédaction du plan d'implémentation ; kanban : TSK08 passée en Doing, TSK08–TSK13 déclarées (TSK09–TSK13 en To do avec dépendances).
- 2026-11-11 : implémentation (5 services : `transition_service`, `journey_service`, `journey_sequence_service`, `journey_filter_service`, `participation_badge_service` ; 7 use cases `view_management` ; 4 modules de tests). 33 tests passed. TSK08 passée en Review.
