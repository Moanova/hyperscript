# SESSIONS.md — Hyperscript

Journal de session :
- informations structurants échangées lors des séances de réalisation sous Vibe Code avec le concepteur produit (TSC), décisions prises et anomalies traitées.
Complément de `AGENTS.md` (règles de travail) et de `docs/project/kanban.md` (suivi des tâches).

Les entrées sont ajoutées dans l'ordre antechronologique.


--

## Séance n°03 (2026-11-11)

### Travaux
- Analyse de la reformulation des règles d'enchaînement des types de blocs narratifs (matrice source → cibles) : vérification de cohérence interne (coquille « entrantes/sortantes » relevée sur la règle Condition ; contradictions Début→Pivot et Condition→Fin levées par décision TSC) et alignement avec RG025–RG031, SU003/SU004, FN020/FN035, `07_data_model`, `03_conception` §3/§4.
- Mises à jour des spécifications FR/EN : `02_business_rules` (RG025 complétée, RG027, RG028 réécrite avec la matrice, RG030 et RG031 réécrites, mentions « sujettes à révision » levées), `01_user_stories` (SU003/SU004), `03_features` (FN020, FN035 sans la promotion), `07_data_model` (description de `Transition`), `03_conception` (matrice ajoutée en §4, promotion et invariant de degré du Pivot supprimés), `docs/projet/implementation-FR/EN.md` (lignes RG028/RG030/RG031/FN035 + date), `src/core/models/data_model.py` (docstring de `Transition`).
- Matrice d'enchaînement actée : Début → {Scène, Pivot} ; Scène → {Scène, Pivot, Fin} ; Pivot → {Condition} ; Condition → {Scène, Fin} ; Fin → aucune. Cycles autorisés (ex. Scène → Pivot → Condition → la même Scène).
- Kanban : TSK08–TSK13 déclarées (chantier vue « Journeys ») ; TSK08 passée en Doing (TSK07 en Review) avec fiche `docs/projet/tasks/TSK08_map_services_usecases.md` (plan d'implémentation : `transition_service` matrice RG028 + cascades RG023, `journey_sequence_service` RG044, `journey_filter_service` RG041/RG048, `participation_badge_service`, use cases `view_management` + tests unitaires ; ajout de la clé `journey_filter_opacity` dans `config.json`) ; TSK09–TSK13 en To do avec dépendances (TSK09/TSK10 → #TSK08 ; TSK11 → #TSK08,#TSK10 ; TSK12 → #TSK09,#TSK11 ; TSK13 → #TSK11,#TSK12).
- Rendu visuel des blocs (suite de séance) : code couleur par type acté (Début #E5C07B, Scène #A7C957, Pivot #D19A66, Condition #E06666, Fin #F0F0F0 — valeurs à confirmer après les premiers tests visuels, mêmes teintes : gris sombre, blanc cassé, or, sable…) ; le nœud affiche le **type** du bloc, libellé et note en infobulle au survol ; badge de participations conservé tel quel de planoscript (coin inférieur droit 2/3-1/3, Ø 16 px, remplissage fixe #E5C07B, masqué à 0, « 9+ », ligne « Agents: … » en infobulle), présent sur tous les blocs ; onglets nommés en anglais (« Journeys », « Agents », « Relationships », « Export »). Mises à jour : `04_interface` FR/EN (§3 onglets, §4 bloc narratif, §9 points 1-2), `src/config/config.json` (`block_scene_color` #A7C957, `block_condition_color` #E06666), `src/ui/utils/theme.py` (note conservée : valeurs définitives à confirmer après les premiers tests visuels).

### Choix actés
- Début → Pivot autorisé (entrantes du Pivot : Début ou Scène) ; Condition → Fin autorisée (sortantes de la Condition : Scène ou Fin ; entrantes de la Fin : Scène ou Condition).
- Promotion automatique Scène → Pivot supprimée (ex-RG030) : le type du bloc reste choisi à la création et immuable (RG029) ; une Scène à plusieurs transitions sortantes reste une Scène.
- ET entre conditions abandonné (Condition → Condition interdit par la matrice) ; le OU (plusieurs Condition issus d'un même Pivot) est conservé.
- Seuils « carte finalisée et cohérente » (1 ou n) : contrôle de cohérence hors MVP ; en MVP, la création d'une transition n'est refusée que si la paire ordonnée de blocs existe déjà ou si la paire de types n'est pas dans la matrice (RG028, SU004, FN020).
- Onglets de la barre d'onglets nommés en anglais dans l'UI (« Journeys », « Agents », « Relationships », « Export ») — point ouvert de la séance n°02 levé ; `04_interface-FR.md` reporté en conséquence (noms affichés en anglais, même en version FR, comme les entrées de menu).
- Code couleur des types de blocs : palette chaude (or #E5C07B, vert olive #A7C957, cuivre #D19A66, rouge #E06666, blanc cassé #F0F0F0) ; valeurs définitives à confirmer après les premiers tests visuels, dans les mêmes teintes.
- Badge de participations : remplissage fixe `badge_bg_color` (#E5C07B), quelle que soit la couleur du type du bloc ; apparence, position (coin inférieur droit 2/3-1/3) et comportement (masqué à 0, « 9+ », ligne « Agents: … » en infobulle) conservés de planoscript.
- Nœud de bloc : affiche le type ; libellé et note déplacés en infobulle au survol (la troncature à 8 caractères de planoscript disparaît).
- Ports conditionnels actés (→ TSK14) : bloc Début sans port entrant, blocs Fin sans port sortant dans la vue « Journeys » — ports masqués (pas grisés), garde-fous `has_input_port()`/`has_output_port()` à la création de transition (un clic près du bord d'un bloc sans le port requis = hors port) ; aucun impact modèle (RG025/RG028 déjà en vigueur). Mises à jour : `04_interface` FR/EN §4 (lignes « Bloc narratif » et « Transition ») ; kanban : TSK14 déclaré en To do (→ #TSK10, #TSK11).
- Bug visuel signalé par TSC (flèches de transition « grises » + grille en surimpression après certains déplacements de blocs) → TSK15 : cause racine = z-value partagée -1 entre lignes de grille (`_draw_grid`) et `Connection`, l'ordre d'insertion faisant passer la grille (recréée au scroll/auto-scroll/resize) au-dessus des flèches. Correctif : grille à `setZValue(-2)` (4 lignes, `journeys_workspace.py`), conforme à `agents_workspace.py` de planoscript. Couleurs nominales conservées telles quelles (gel TSC jusqu'à la séance de tests utilisateur). py_compile OK, 44 tests passed. Fiche `tasks/TSK15_grid_zorder_fix.md` ; TSK15 passée en Review.
- TSK14 implémenté sur go TSC (ports conditionnels Début/Fin) : helpers Qt-free `type_allows_incoming/outgoing` dérivés de `ALLOWED_TARGET_TYPES` (matrice RG028, source unique) dans `transition_service.py` + test unitaire ; `has_input_port()`/`has_output_port()` dans `base_node.py` ; masquage des ports dans `BlockNode._apply_conditional_ports()` ; garde-fous « bord sans port = hors port » dans `_handle_port_selection` (`journeys_workspace.py`). py_compile OK, **45 tests passed** ; smoke offscreen TSK14 complété (à valider sur poste de dev). Fiche `tasks/TSK14_conditional_ports.md` ; TSK14 passée en Review.

- Implémentation TSK08–TSK13 (vue « Journeys ») lancée et menée à bien sur demande TSC :
  - TSK08 : services `transition_service` (matrice RG028 + unicité + cascade RG023), `journey_service` (RG039/RG040/RG042), `journey_sequence_service` (RG044), `journey_filter_service` (RG041/RG048, clé `journey_filter_opacity` ajoutée à config.json), `participation_badge_service`, 7 use cases `view_management` + tests → 33 tests passed.
  - TSK09 : 6 use cases `journey_management` (FN023–FN027, FN038) + tests → 40 tests passed.
  - TSK10 : nœuds `base_node.py` (type affiché, tooltip lb+note, couleurs par type via `theme.block_color`), `block_node.py` (fusion State/Event + badge participations conservé), `connection.py` (transition fléchée, **sans** écriture du modèle RG058) ; `view_model` : style ARROW par défaut ; `layout_service` : résidus plano corrigés (`create_empty_layout`, `create_connection_layout`).
  - TSK11 : `journeys_workspace.py` (grille, scène extensible, auto-scroll, sélection unique, tracé de transition, filtre RG048, menu contextuel via signaux), `tab_bar.py` (onglets Journeys/Agents/Relationships/Export), `main_window.py` (onglets, actions Project câblées sur les use cases, Display>Journey dynamique, menu contextuel construit depuis les QAction du menu général RG055, persistance layouts RG060 au save/load).
  - TSK12 : dialogues `block_dialog.py` (FN015/RG042/FN035), `transition_dialog.py`, `journey_dialog.py`, `journey_selection_dialog.py` + câblage `blocks_edit`/`transitions_edit`/`journeys_edit`/`journeys_set_default`.
  - TSK13 : matrice de traçabilité FR/EN mise à jour ; smoke offscreen jetable (`/tmp/offscreen_journeys_smoke.py`, non commité).
- **44 tests unitaires passed** (`pytest tests/ -q`) ; `py_compile` OK sur tout `src/` ; imports locaux résolus (vérif AST) ; aucun import Qt dans `core/`/`usecases/` (RG058).
- Corrections de specs en fin de séance (demande TSC) : SU004 et FN022 (FR + EN) alignées sur RG041 — la suppression d'une transition ne supprime **aucun** rattachement de parcours (l'appartenance est dérivée des blocs) ; résidu planoscript levé.

### État en fin de séance
- Commits + push sur `dev` effectués sur demande TSC (11-11-2026) : `0c2ad64` (séance n°03 complète, 72 fichiers, +5336/−282), `7df6c5c` (TSK14 acté dans `04_interface` FR/EN + correctif TSK15 z-order grille à -2 — 44 tests passed), `ba2e370` (implémentation TSK14 : helpers matrice + masquage des ports Début/Fin — 45 tests passed), puis quatrième commit (corrections SU004/FN022 FR/EN sur RG041 + kanban TSK15 en Done + SESSIONS.md).
- Kanban : **TSK15 en Done** (validée TSC) ; TSK08–TSK14 en Review ; TSK07 en Review ; To do vide. Tâches d'implémentation laissées en Review en attente des retours de test TSC.
- Point SU004/FN022 vs RG041 : **corrigé** (quatrième commit). Reste ouvert pour la prochaine séance : SU003 (FR ligne 50 / EN ligne 49) dit encore « chaque bloc dispose de deux ports » — à aligner sur TSK14 (Début sans port entrant, Fin sans port sortant, `04_interface` §4).
- Prochaine séance : retours de tests manuels TSC (`python src/main.py` sur poste de dev + smoke offscreen `/tmp/offscreen_journeys_smoke.py`, dont rendu QImage avant/après `_draw_grid()` pour TSK15 et visibilité des ports pour TSK14) → passage des tâches Review en Done, puis commit/push sur demande. **Séance clôturée le 11-11-2026.**

### Problèmes rencontrés
- Sandbox : `libGL.so.1` absent (pas de droits root) → PySide6 non importable ici : tests Qt offscreen **non exécutés** (script jetable prêt) ; `pytest` installé via pip (9.2.0).

### Problèmes rencontrés
- Aucun.

---

## Séance n°02 (2026-11-10)

### Travaux
- Revue des spécifications (3 points de vérification TSC) :
  1. Règle des points de suspension actée et appliquée à `05_menu-FR/EN.yaml` : « ... » = entrée ouvrant une fenêtre nécessitant une action complémentaire (saisie/choix/confirmation), fenêtre purement informative sans « ... » ; ajout sur « Exporter la carte... », « Importer une carte... », les 5 « Éditer... », les 5 « Supprimer... » ; retrait sur « Projets récents », « Blocs narratifs › Nouveau », « Transitions › Nouvelle », « Parcours › Nouveau » ; « Nouveau projet... » conservé par convention usuelle (exception documentée dans la légende des deux fichiers).
  2. Toutes les références aux entrées du menu dans `docs/specification/` alignées sur les noms anglais à jour de `05_menu-EN.yaml` (application unilingue anglais), y compris dans les documents FR (corrections : « Recents Projects... », « Fichier », « Blocks... », « Agents... », « Relations... », etc.).
  3. Parcours par défaut désigné par l'auteur : correction de SU005 (la création d'un parcours n'active rien — filtre possiblement désactivé), nouvelle fonctionnalité FN038 + entrée `Project › Journeys › Set as Default...`, nouvelle règle RG062 ; règle de rattachement des nouveaux blocs unifiée « parcours actif si le filtre de parcours est activé, parcours par défaut sinon » (FN014, FN019, FN026, SU003, SU005, RG040, FN038) ; notion « parcours courant » supprimée, unifiée sur « parcours actif ».
- `docs/conception/03_conception-FR.md` aligné (règles §4, points 13–15) ; version EN créée : `docs/conception/03_conception-EN.md`.
- Matrice de traçabilité initialisée : `docs/projet/implementation-FR.md` / `implementation-EN.md` (62 RG, 38 FN, entrées du menu, 12 SU ; statuts initiaux `not-started` / `greyed-MVP`).
- TSK07 — initialisation de la base de code (reprise du code planoscript figé `faa8fdd`) : classe A reprise telle quelle (loaders config/user_state, `ui_utils`, services+dialogues About/Change Log, `conftest.py`, `pyproject.toml` renommé) + `theme.py` adapté (couleurs par type de bloc) ; classe B adaptée (nouveau `core/models/data_model.py`, `view_model.py`, `layout_service.py`, `project_service.py` + `close_project()`, `create_project_usecase.py`, `main.py`, `main_window.py` shell : menu conforme à `05_menu-EN.yaml` avec stubs `menu_actions`, écran d'accueil, info bar, actions fichier FN002/005/006/008/009/010, dialogues FN003/004) ; scripts associés `usecases/file_management/` ; workspaces laissés en placeholder (tâche suivante). 8 tests unitaires passed (`pytest tests/ -q`). Commits `72b2461` (revue specs) et `455c823` (code) poussés sur `dev` ; kanban : TSK01–TSK06 en Done, TSK07 en Review.
- Vérifications : YAML des menus valide ; script de contrôle des références de chemins de menu contre `05_menu-EN.yaml` (OK) ; parité FR/EN des nouveaux documents (8 sections, tableau, points 1–15).

### Choix actés
- Règle des « ... » documentée dans la légende de `05_menu-FR/EN.yaml` ; exception « Nouveau projet... » conservée.
- Application unilingue anglais pour le moment : les documents de spécification référencent les noms anglais des entrées du menu, même en version FR.
- Une seule notion de parcours actif (`active_journey`, null = parcours par défaut) ; « parcours courant » abandonné.
- L'auteur peut désigner le parcours par défaut à tout moment (FN038, `Set as Default...`, RG062) ; la désignation ne modifie pas le parcours actif.
- Document de traçabilité placé dans `docs/projet/` (`implementation-FR.md` + `implementation-EN.md`), conventions de liens code/tests par commentaires d'ID (`# RGxxx:` / `# FNxxx:`) et noms de tests `test_rgXXX_*` / `test_fnXXX_*`.

### État en fin de séance
- Commits `72b2461` (revue des spécifications) et `455c823` (initialisation de la base de code, TSK07) poussés sur `dev`.
- Kanban : TSK01–TSK06 en Done (validées TSC 10-11-2026), TSK07 en Review.
- Matrice de traçabilité `docs/projet/implementation-FR/EN.md` mise à jour : 9 RG `implemented`, FN001–FN004/FN006/FN008–FN010 `partial`, FN005 `implemented`, 8 entrées de menu câblées (`partial`).
- Prochaine séance : espaces de travail (vues « Parcours »/Journeys, Agents, Relations, Export ; nœuds de blocs et transitions ; persistance des layouts RG060).
- Points ouverts : libellé du menu contextuel « Associate agents... » (FR dans les docs FR) ; noms de vues/onglets en FR dans les docs FR (« Parcours », « Agents », « Relations ») alors que l'app sera anglaise ; fiches historiques `docs/projet/tasks/TSK0*.md` non réécrites (journal de séance) ; périmètre MVP des vues, maquette vue « Relations », SU009/SU010/SU012 à finaliser, exports, zoom, annuler/rétablir, barres latérales.

### Problèmes rencontrés
- Lancement GUI non testable dans le sandbox (libGL.so.1 absent, pas de droits root) : tests offscreen Qt à valider sur poste de dev (noté dans la fiche TSK07).

---

## Séance n°01 (2026-11-09)

### Travaux
- Dépôt planoscript (action exceptionnelle) : `README.md` mis à jour pour refléter la clôture du projet le 06-11-2026 (badge, roadmap, note du créateur, dette TSK34 documentée) — commit `faa8fdd`, poussé sur `dev`.
- Dépôt hyperscript : initialisation de la note de conception `docs/conception/03_conception-FR.md`, à partir de la note de préconception de planoscript (`docs/conception/hyperscript_preconception-FR.md`) et des décisions TSC de la séance.
- Spécifications FR/EN rédigées via TSK01–TSK06 (kanban v1–v12, toutes en Review) : `07_data_model` (JSON), `01_user_stories` (SU001–SU012), `03_features` (FN001–FN037), `05_menu` (YAML), `04_interface`, `02_business_rules` (61 règles RG001–RG061, 5 thèmes) ; fiches dans `docs/projet/tasks/`.
- Vérifications effectuées : alignement FR/EN de `03_features` plano (OK) ; analyse doc ↔ code de `04_interface` plano (thème sombre réel, fichiers fantômes toolbars/zoom, onglet Export implémenté, textes UI en anglais).
- Commit `7593311` (conception initiale) + commit de fin de séance, poussés sur `dev`.

### Choix actés (séance TSC 09-11-2026)
- « Parcours » / « Journey » acté (« Version » conservée comme alternative future) ; « Branch » remplacé par le terme bilingue « Pivot ».
- Typage des relations : liste de valeurs en fichier de configuration pour le MVP ; enrichissement par l'auteur hors MVP.
- MVP aligné sur planoscript : une seule carte narrative par projet (le modèle prévoit N cartes dès le MVP), pas de contrôle de cohérence des parcours (hors MVP), pas de migration des projets planoscript existants.
- Cycles autorisés, exprimés par chaînage de blocs (ex. S1 → P1 → C1 → S1) : pas de clé « condition » sur la transition, la condition structurée est uniquement portée par le bloc Condition (formulation initiale « cycle direct S —C→ S » corrigée en séance).
- À définir en phase de conception : maquette de la vue « Relations », exports (technique dev, par événements, réimport), zoom, annuler/rétablir, barres latérales.
- Dette TSK34 de planoscript prise en compte dès le début (use cases, pas d'écriture directe du modèle depuis l'UI, bug export `_esc(rel.agent_id)` à traiter dès la conception).
- TSK01 du kanban = rédaction des documents de conception ; documents existants de `docs/conception/` à revoir si nécessaire (en-têtes « Planoscript »).
- Relations binaires (`agent_a_id`, `agent_b_id`), ancrées à un bloc ; pas de clé `clock_id` : l'ordonnancement = rang du bloc d'ancrage dans le parcours (dérivé de `journey_node.sequence_order`).
- En EN, l'entité se nomme « Relationship » (FR : « Relation »), la plupart des relations étant entre personnages ; clé JSON `relationship` (appliqué aux docs EN et aux deux JSON).
- Vue principale = « Parcours » / Journeys (ex-vue Events) ; export de lecture en HTML autonome ; aucun bloc orphelin (rattachement auto au parcours actif/par défaut, non-retrait du dernier parcours) ; filtre de parcours désactivé par défaut et appliqué à toutes les vues ; suppression d'un parcours → réaffectation des rattachements de ses blocs au parcours par défaut.
- Menu acté (`05_menu`) : Files avec séparateurs (Export Map, Import Map, Recent Projects... grisés en MVP), Edit grisé (History/Delete supprimés), Zoom grisé, Project›View (Parcours/Agents/Relations/Export nommés, min MVP = Parcours + Export), Agents (New/Edit/Copy/Delete/Associate with Block...), Narrative Blocks (New... sans Début), Transitions, Journeys (avec Copy), Relationships, About ; terme « Copy » pour la duplication ; menu contextuel aligné dynamiquement sur le menu applicatif.
- Export sur fichier hors MVP (seul l'aperçu in-app, vue « Export », est dans le MVP minimal) ; Import Map = importer une carte exportée dans le projet courant (grisée en MVP).
- `03_features` : pas de champ « État », pas de références RG ; FN001 complétée (single-instance + réf. écran d'accueil).
- `04_interface` : thème sombre charte 98 conservé, 100 % piloté par config.json ; vues « Agents » et « Relations » laissées vides (re-conception à venir) ; zoom hors MVP (pas de barre de zoom) ; pas de checklists, ni arborescence src, ni notes de conception dans le document.
- `02_business_rules` : nouvelle numérotation, sémantique pure sans termes techniques (réimplémentation possible dans un autre langage) ; degré d'opacité du filtre en configuration, pas dans les règles ; règles Pivot/Condition (RG030/RG031) marquées « sujettes à révision en cours de conception » ; suppressions RG033 (remplacée par chaînage libre + séquence DFS), RG058, RG062, RG065, RG066 ; RG024/RG052 remplacées par « aucun bloc orphelin ».

### État en fin de séance
- Kanban v12 : TSK01–TSK06 en Review (validation TSC à venir), Doing vide. Prochaine séance : `99_mvp_scope-FR/EN.md` (TSK07).
- Points ouverts : périmètre MVP des vues (min. Parcours + Export), maquette vue « Relations », contenu vue « Agents », SU009/SU010/SU012 à finaliser après conception, exports (technique / par événements / réimport), zoom, annuler/rétablir, barres latérales, langue de l'app (unilingue), fenêtre d'édition du projet, version EN de la note de conception, en-têtes « Planoscript » dans les docs `docs/conception/` copiées.

### Problèmes rencontrés
- Aucun.
