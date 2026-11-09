# Hyperscript ::: Tableau kanban du projet

- **Date de dernière modification** : 09-11-2026
- **Description** : Suivi de l'avancement des tâches du projet. v1 (09-11-2026) : TSK01 créée (révision du modèle de données — point de départ de la reconception depuis planoscript) et passée en Doing. v2 (09-11-2026) : TSK01 implémentée (docs/specification/07_data_model-FR.json + 07_data_model-EN.json générés, JSON valides, structures FR/EN identiques hors descriptions) et passée en Review — en attente de validation TSC. v3 (09-11-2026) : TSK02 créée (rédaction des scenarii d’utilisation) et passée en Doing (TSK01 en Review). v4 (09-11-2026) : TSK02 implémentée (01_user_stories-FR/EN.md rédigés, 12 scenarii, sans références RG ni clés techniques) et passée en Review — en attente de validation TSC. v5 (09-11-2026) : TSK03 créée (rédaction des fonctionnalités) et passée en Doing (TSK02 en Review). v6 (09-11-2026) : TSK03 implémentée (03_features-FR/EN.md rédigés, FN001–FN037, sans références RG ni champ « État ») et passée en Review — en attente de validation TSC. v7 (09-11-2026) : TSK04 créée (rédaction du menu) et passée en Doing (TSK03 en Review). v8 (09-11-2026) : TSK04 implémentée (05_menu-EN/FR.yaml rédigés, YAML valides) et passée en Review — en attente de validation TSC. v9 (09-11-2026) : TSK05 créée (rédaction de l’interface) et passée en Doing (TSK04 en Review). v10 (09-11-2026) : TSK05 implémentée (04_interface-FR/EN.md rédigés) et passée en Review — en attente de validation TSC.
  - Les chantiers majeurs sont des **épics** (EPCnn) découpés en **tâches** (TSKnn).
  - Le détail de chaque tâche (analyse, décisions, journal des travaux) est consigné dans un fichier markdown dédié du sous-dossier `tasks/`, nommé d'après le code de la tâche.
  - Le fichier de détail est créé au passage de la tâche en Doing.


---

## Convention de dépendances

- Une dépendance est notée `→ #TSKnn` (ou `→ #SUxxx` pour les scénarii d'utilisation) **uniquement sur la tâche dépendante** (source unique de vérité ; pas de lien inverse sur la tâche bloquante).
- Une tâche ne passe en Doing que si toutes ses dépendances sont en Done ; une tâche bloquée reste en To do.
- Les dépendances se déclarent entre tâches ; les mentions au niveau epic restent indicatives.

## Chaîne critique (déroulé de référence)

- TSK01 (modèle de données) → TSK02 (scenarii) → TSK03 (fonctionnalités) → TSK04 (menu) → TSK05 (interface), puis 02_règles de gestion et 99_périmètre MVP.


---

## Tableau du kanban

### To do

- A initialiser.


### Doing


### Review

- [ ] TSK01 — Modèle de données : cloner `07_data_model-FR.json` / `07_data_model-EN.json` depuis `docs/specification/` du dépôt planoscript vers `docs/specification/` de hyperscript, puis réviser les deux documents pour les aligner sur les décisions actées (`docs/conception/03_conception-FR.md`, séance TSC 09-11-2026 : fusion State/Event en Bloc typé, arcs → Transitions, associations → Participations, nouvelle entité Relation ancrée à un bloc, nœuds de parcours rattachés aux blocs, `narrative_maps[]`, Agent {Personnage, Artefact}) — fiche `tasks/TSK01_data_model_revision.md` — créée 09-11-2026 (décision TSC), passée en Doing 09-11-2026 (kanban v1), implémentée et passée en Review 09-11-2026 (kanban v2) — en attente de validation TSC

- [ ] TSK02 — Rédiger les scenarii d’utilisation `docs/specification/01_user_stories-FR.md` / `-EN.md` : reprise de la numérotation planoscript (SU001–SU010 révisés ; SU011 relations agent-agent et SU012 vue « Relations » ajoutés), sémantique hyperscript uniquement (pas de références RG ni de clés techniques), SU009/SU010/SU012 initialisés à finaliser après conception → #TSK01 — fiche `tasks/TSK02_user_stories.md` — créée 09-11-2026 (décision TSC), passée en Doing 09-11-2026 (kanban v3), implémentée et passée en Review 09-11-2026 (kanban v4) — en attente de validation TSC

- [ ] TSK03 — Rédiger les fonctionnalités `docs/specification/03_features-FR.md` / `-EN.md` : reprise FN001–FN033 (vocabulaire hyperscript, rattachement des blocs aux parcours, transitions libres avec cycles, FN027 réaffectation des rattachements au parcours par défaut, FN029 filtre désactivé par défaut et appliqué à toutes les vues, espaces de travail nommés sans numérotation), + FN034–FN037 nouvelles, sans références RG ni champ « État » → #TSK02 — fiche `tasks/TSK03_features.md` — créée 09-11-2026 (décision TSC), passée en Doing 09-11-2026 (kanban v5), implémentée et passée en Review 09-11-2026 (kanban v6) — en attente de validation TSC

- [ ] TSK04 — Rédiger le menu général `docs/specification/05_menu-EN.yaml` / `05_menu-FR.yaml` (structure actée séance TSC 09-11-2026 : Files avec séparateurs et entrées grisées MVP, Edit grisé, Display›Journey + Zoom grisé, Project›View/Agents/Narrative Blocks/Transitions/Journeys/Relationships, About ; Start absent de New..., « Associate with Block... », terme « Copy », menu contextuel dynamique aligné) → #TSK03 — fiche `tasks/TSK04_menu.md` — créée 09-11-2026 (décision TSC), passée en Doing 09-11-2026 (kanban v7), implémentée et passée en Review 09-11-2026 (kanban v8) — en attente de validation TSC

- [ ] TSK05 — Rédiger l'interface `docs/specification/04_interface-FR.md` / `-EN.md` (structure plano conservée, thème sombre charte 98 conservé et piloté par config.json, vues « Agents »/« Relations » laissées vides, zoom hors MVP, sans checklists ni références RG ni arborescence src) → #TSK04 — fiche `tasks/TSK05_interface.md` — créée 09-11-2026 (décision TSC), passée en Doing 09-11-2026 (kanban v9), implémentée et passée en Review 09-11-2026 (kanban v10) — en attente de validation TSC


### Done

- A initialiser.


---

## Description des tâches

- [ ] TSK01 — Révision du modèle de données `docs/specification/07_data_model-FR.json` / `07_data_model-EN.json` (clone depuis planoscript, aligné sur `docs/conception/03_conception-FR.md`) — fiche `tasks/TSK01_data_model_revision.md`
- [ ] TSK02 — Scenarii d’utilisation `docs/specification/01_user_stories-FR.md` / `-EN.md` (SU001–SU012, reprise de la numérotation plano) → #TSK01 — fiche `tasks/TSK02_user_stories.md`
- [ ] TSK03 — Fonctionnalités `docs/specification/03_features-FR.md` / `-EN.md` (FN001–FN037) → #TSK02 — fiche `tasks/TSK03_features.md`
- [ ] TSK04 — Menu général `docs/specification/05_menu-EN.yaml` / `-FR.yaml` → #TSK03 — fiche `tasks/TSK04_menu.md`
- [ ] TSK05 — Interface `docs/specification/04_interface-FR.md` / `-EN.md` → #TSK04 — fiche `tasks/TSK05_interface.md`
