# SESSIONS.md — Hyperscript

Journal de session :
- informations structurants échangées lors des séances de réalisation sous Vibe Code avec le concepteur produit (TSC), décisions prises et anomalies traitées.
Complément de `AGENTS.md` (règles de travail) et de `docs/project/kanban.md` (suivi des tâches).

Les entrées sont ajoutées dans l'ordre antechronologique.


--

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
