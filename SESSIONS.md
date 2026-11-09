# SESSIONS.md — Hyperscript

Journal de session :
- informations structurants échangées lors des séances de réalisation sous Vibe Code avec le concepteur produit (TSC), décisions prises et anomalies traitées.
Complément de `AGENTS.md` (règles de travail) et de `docs/project/kanban.md` (suivi des tâches).

Les entrées sont ajoutées dans l'ordre antechronologique.


--

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
