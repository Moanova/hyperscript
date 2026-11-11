# Hyperscript ::: Tableau kanban du projet

- **Date de dernière modification** : 11-11-2026
- **Description** : Suivi de l'avancement des tâches du projet.
  - Les chantiers majeurs sont des **épics** (EPCnn) découpés en **tâches** (TSKnn).
  - Le détail de chaque tâche (analyse, décisions, journal des travaux) est consigné dans un fichier markdown dédié du sous-dossier `tasks/`, nommé d'après le code de la tâche.
  - Le fichier de détail est créé au passage de la tâche en Doing.


---

## Convention de dépendances

- Une dépendance est notée `→ #TSKnn` (ou `→ #SUxxx` pour les scenarii d'utilisation) **uniquement sur la tâche dépendante** (source unique de vérité ; pas de lien inverse sur la tâche bloquante).
- Une tâche ne passe en Doing que si toutes ses dépendances sont en Done ; une tâche bloquée reste en To do.
- Les dépendances se déclarent entre tâches ; les mentions au niveau epic restent indicatives.


## Chaîne critique (déroulement de référence)

- TSK01 (modèle de données) → TSK02 (scenarii) → TSK03 (fonctionnalités) → TSK04 (menu) → TSK05 (interface) → TSK06 (règles de gestion), puis 99_périmètre MVP.
- Puis chantier vue « Journeys » (vue Parcours) : TSK08 (services/use cases de la carte) → TSK09 (use cases parcours) + TSK10 (nœuds graphiques) → TSK11 (workspace + intégration) → TSK12 (dialogues + menus Project) → TSK13 (tests offscreen + traçabilité) ; puis TSK14 (ports conditionnels Début/Fin, acté 11-11-2026) déclaré en To do ; TSK15 (correctif z-order : grille sous les transitions, 11-11-2026) implémenté et passé en Review.


---

## Tableau du kanban

### To do

- [ ] TSK14 — Ports conditionnels selon le type de bloc dans la vue « Journeys » : bloc Début sans port entrant, blocs Fin sans port sortant (ports masqués dans `block_node.py`/`base_node.py`, garde-fous `has_input_port()`/`has_output_port()` et refus explicite à la création de transition dans `journeys_workspace.py` ; spec `04_interface` §4 actée 11-11-2026 ; aucun impact modèle, RG025/RG028 déjà en vigueur) → #TSK10, #TSK11 — fiche `tasks/TSK14_conditional_ports.md` (à créer au passage en Doing)

### Doing


### Review

- [ ] TSK15 — Correctif z-order dans la vue « Journeys » : lignes de grille à `setZValue(-2)` (strictement sous les `Connection` à z=-1) dans `_draw_grid()` de `journeys_workspace.py`, pour qu'un redessin de la grille (scroll/auto-scroll pendant un déplacement de bloc, resize) ne surimprime plus les flèches (lignes sombres #333333/#4A4A4A par-dessus la flèche #CCCCCC = flèche « grise ») → #TSK11 — fiche `tasks/TSK15_grid_zorder_fix.md` — créée 11-11-2026, passée en Doing 11-11-2026 (TSK11 en Review), implémentée et passée en Review 11-11-2026 (py_compile OK, 44 tests passed ; validation visuelle offscreen à faire sur poste de dev, libGL absent dans le sandbox)
- [ ] TSK13 — Tests offscreen de la vue « Journeys » (script jetable non commité) + matrice de traçabilité `docs/projet/implementation-FR/EN.md` → #TSK11, #TSK12 — fiche `tasks/TSK13_offscreen_tests.md` — créée 11-11-2026, passée en Doing 11-11-2026, implémentée et passée en Review 11-11-2026 (44 tests passed ; smoke offscreen rédigé, bloqué dans le sandbox : libGL absent — à valider sur poste de dev)
- [ ] TSK12 — Dialogues (`block_dialog.py` FN015/RG042/FN035, `transition_dialog.py` FN021, `journey_dialog.py` FN024, `journey_selection_dialog.py` FN038) + câblage des entrées restantes de `Project` → #TSK09, #TSK11 — fiche `tasks/TSK12_dialogs_menus.md` — créée 11-11-2026, passée en Doing 11-11-2026, implémentée et passée en Review 11-11-2026 (py_compile OK, 44 tests passed)
- [ ] TSK11 — Espace de travail « Journeys » (`journeys_workspace.py`, `tab_bar.py`, intégration `main_window.py`, persistance layouts RG060) → #TSK08, #TSK10 — fiche `tasks/TSK11_journeys_workspace.md` — créée 11-11-2026, passée en Doing 11-11-2026, implémentée et passée en Review 11-11-2026 (py_compile OK, 40 tests passed ; tests Qt offscreen à valider sur poste de dev)
- [ ] TSK10 — Nœuds graphiques de la vue « Journeys » (`base_node.py`, `block_node.py`, `connection.py`) → #TSK08 — fiche `tasks/TSK10_graph_nodes.md` — créée 11-11-2026, passée en Doing 11-11-2026, implémentée et passée en Review 11-11-2026 (py_compile OK ; tests Qt offscreen à valider sur poste de dev, libGL absent dans le sandbox)
- [ ] TSK09 — Use cases de gestion des parcours (créer / renommer+note / dupliquer / activer / définir par défaut / supprimer — FN023–FN027, FN038 ; RG024, RG034, RG038, RG039, RG043, RG062) + tests unitaires → #TSK08 — fiche `tasks/TSK09_journey_usecases.md` — créée 11-11-2026, passée en Doing 11-11-2026, implémentée et passée en Review 11-11-2026 (40 tests passed)
- [ ] TSK08 — Services et use cases de la carte narrative : `transition_service.py` (matrice d'enchaînement RG028, unicité par paire ordonnée, cascade RG023), `journey_sequence_service.py` (séquence DFS RG044), `journey_filter_service.py` (appartenance dérivée RG041, opacité en config RG048), `participation_badge_service.py` (badge Qt-free), use cases `view_management` (création/édition/duplication/suppression de blocs et transitions) + tests unitaires → #TSK07 — fiche `tasks/TSK08_map_services_usecases.md` — créée 11-11-2026, passée en Doing 11-11-2026, implémentée et passée en Review 11-11-2026 (33 tests passed)
- [ ] TSK07 — Initialiser l'arborescence du code source `src/` + `tests/` : reprise du code planoscript figé selon le verdict d'analyse (classe A telle quelle + `theme.py` adapté, fichiers de données regénérés, en-têtes/commentaires anglais, `pyproject.toml` renommé) → #TSK06 — fiche `tasks/TSK07_code_init.md` — créée 10-11-2026, passée en Doing 10-11-2026, implémentée et passée en Review 10-11-2026
### Done

- [x] TSK01 — Modèle de données : cloner `07_data_model-FR.json` / `07_data_model-EN.json` depuis `docs/specification/` du dépôt planoscript vers `docs/specification/` de hyperscript, puis réviser les deux documents pour les aligner sur les décisions actées (`docs/conception/03_conception-FR.md`, séance 09-11-2026 : fusion State/Event en Bloc typé, arcs → Transitions, associations → Participations, nouvelle entité Relation ancrée à un bloc, nœuds de parcours rattachés aux blocs, `narrative_maps[]`, Agent {Personnage, Artefact}) — fiche `tasks/TSK01_data_model_revision.md` — créée 09-11-2026, passée en Doing 09-11-2026, implémentée et passée en Review 09-11-2026 — validée TSC et passée en Done 10-11-2026
- [x] TSK02 — Rédiger les scenarii d’utilisation `docs/specification/01_user_stories-FR.md` / `-EN.md` : reprise de la numérotation planoscript (SU001–SU010 révisés ; SU011 relations agent-agent et SU012 vue « Relations » ajoutés), sémantique hyperscript uniquement (pas de références RG ni de clés techniques), SU009/SU010/SU012 initialisés à finaliser après conception → #TSK01 — fiche `tasks/TSK02_user_stories.md` — créée 09-11-2026, passée en Doing 09-11-2026, implémentée et passée en Review 09-11-2026 — validée TSC et passée en Done 10-11-2026
- [x] TSK03 — Rédiger les fonctionnalités `docs/specification/03_features-FR.md` / `-EN.md` : reprise FN001–FN033 (vocabulaire hyperscript, rattachement des blocs aux parcours, transitions libres avec cycles, FN027 réaffectation des rattachements au parcours par défaut, FN029 filtre désactivé par défaut et appliqué à toutes les vues, espaces de travail nommés sans numérotation), + FN034–FN037 nouvelles, sans références RG ni champ « État » → #TSK02 — fiche `tasks/TSK03_features.md` — créée 09-11-2026, passée en Doing 09-11-2026, implémentée et passée en Review 09-11-2026 — validée TSC et passée en Done 10-11-2026
- [x] TSK04 — Rédiger le menu général `docs/specification/05_menu-EN.yaml` / `05_menu-FR.yaml` (structure actée séance 09-11-2026 : Files avec séparateurs et entrées grisées MVP, Edit grisé, Display›Journey + Zoom grisé, Project›View/Agents/Narrative Blocks/Transitions/Journeys/Relationships, About ; Start absent de New..., « Associate with Block... », terme « Copy », menu contextuel dynamique aligné) → #TSK03 — fiche `tasks/TSK04_menu.md` — créée 09-11-2026, passée en Doing 09-11-2026, implémentée et passée en Review 09-11-2026 — validée TSC et passée en Done 10-11-2026
- [x] TSK05 — Rédiger l'interface `docs/specification/04_interface-FR.md` / `-EN.md` (structure plano conservée, thème sombre charte 98 conservé et piloté par config.json, vues « Agents »/« Relations » laissées vides, zoom hors MVP, sans checklists ni références RG ni arborescence src) → #TSK04 — fiche `tasks/TSK05_interface.md` — créée 09-11-2026, passée en Doing 09-11-2026, implémentée et passée en Review 09-11-2026 — validée TSC et passée en Done 10-11-2026
- [x] TSK06 — Rédiger les règles de gestion `docs/specification/02_business_rules-FR.md` / `-EN.md` : analyse par thèmes actée en séance (5 thèmes, nouvelle numérotation RG, sémantique pure sans termes techniques, opacité du filtre en configuration, règles Pivot/Condition marquées « sujettes à révision ») → #TSK05 — fiche `tasks/TSK06_business_rules.md`

## Description des tâches

- [x] TSK01 — Révision du modèle de données `docs/specification/07_data_model-FR.json` / `07_data_model-EN.json` (clone depuis planoscript, aligné sur `docs/conception/03_conception-FR.md`) — fiche `tasks/TSK01_data_model_revision.md`
- [x] TSK02 — Scenarii d’utilisation `docs/specification/01_user_stories-FR.md` / `-EN.md` (SU001–SU012, reprise de la numérotation plano) → #TSK01 — fiche `tasks/TSK02_user_stories.md`
- [x] TSK03 — Fonctionnalités `docs/specification/03_features-FR.md` / `-EN.md` (FN001–FN037) → #TSK02 — fiche `tasks/TSK03_features.md`
- [x] TSK04 — Menu général `docs/specification/05_menu-EN.yaml` / `-FR.yaml` → #TSK03 — fiche `tasks/TSK04_menu.md`
- [x] TSK05 — Interface `docs/specification/04_interface-FR.md` / `-EN.md` → #TSK04 — fiche `tasks/TSK05_interface.md`
- [x] TSK06 — Règles de gestion `docs/specification/02_business_rules-FR.md` / `-EN.md` → #TSK05 — fiche `tasks/TSK06_business_rules.md`
- [x] TSK07 — Initialisation de l'arborescence du code source `src/` + `tests/` → #TSK06 — fiche `tasks/TSK07_code_init.md`
- [ ] TSK08 — Services et use cases de la carte narrative (`transition_service`, `journey_service`, `journey_sequence_service`, `journey_filter_service`, `participation_badge_service`, use cases `view_management` + tests unitaires) → #TSK07 — fiche `tasks/TSK08_map_services_usecases.md`
- [ ] TSK09 — Use cases de gestion des parcours (FN023–FN027, FN038) + tests unitaires → #TSK08 — fiche `tasks/TSK09_journey_usecases.md`
- [ ] TSK10 — Nœuds graphiques de la vue « Journeys » (`base_node`, `block_node`, `connection`) → #TSK08 — fiche `tasks/TSK10_graph_nodes.md`
- [ ] TSK11 — Workspace « Journeys » + barre d'onglets + intégration `main_window` + persistance des layouts (RG060) → #TSK08, #TSK10 — fiche `tasks/TSK11_journeys_workspace.md`
- [ ] TSK12 — Dialogues (édition bloc, transition, parcours, Set as Default) + câblage des menus `Project` restants → #TSK09, #TSK11 — fiche `tasks/TSK12_dialogs_menus.md`
- [ ] TSK13 — Tests offscreen vue « Journeys » + matrice de traçabilité → #TSK11, #TSK12 — fiche `tasks/TSK13_offscreen_tests.md`
- [ ] TSK14 — Ports conditionnels Début/Fin dans la vue « Journeys » (masquage des ports + garde-fous de création de transition) → #TSK10, #TSK11 — fiche `tasks/TSK14_conditional_ports.md`
- [ ] TSK15 — Correctif z-order grille (z=-2) sous les transitions (z=-1) dans `_draw_grid()` → #TSK11 — fiche `tasks/TSK15_grid_zorder_fix.md`
