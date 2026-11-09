# TSK01 — Révision du modèle de données (point de départ de la reconception)

- **Épic** : reconception depuis planoscript — tâche de conception
- **Statut** : Review — en attente de validation TSC (09-11-2026)
- **Date de création** : 2026-11-09
- **Dépendances** : aucune

## Objectif

Cloner le document `docs/specification/07_data_model-FR.json` (et son équivalent EN
`07_data_model-EN.json`) du dossier `docs/specification/` du dépôt planoscript vers
`docs/specification/` du dépôt hyperscript, puis réviser les deux documents pour les
aligner sur les décisions actées (`docs/conception/03_conception-FR.md`, séance TSC
09-11-2026). Pas de migration des projets planoscript existants (hors périmètre) :
les clés JSON peuvent être renommées librement.

## Livrables

- [x] `docs/specification/07_data_model-FR.json` (généré).
- [x] `docs/specification/07_data_model-EN.json` (généré ; structure identique au FR, descriptions EN).

## Modifications appliquées (décisions actées 09-11-2026)

1. **Projet** : `narrative_map` → `narrative_maps[]` (MVP à une seule carte narrative,
   mais le modèle prévoit N cartes dès le MVP) ; agents au niveau projet (inchangé).
2. **Fusion State/Event** : `state[]` + `event[]` → `bloc[]` unique ; nouveau `$defs/Block`
   avec `typ` ∈ {Début, Scène, Pivot, Condition, Fin} (EN : {Start, Scene, Pivot,
   Condition, End}), choisi à la création et **immuable** ensuite ; le type « Relation »
   disparaît (remplace {Initial, Action, Relation, Final}).
3. **Arcs → Transitions** : `state_to_event[]` + `event_to_state[]` → `transition[]`
   { id, from_block_id, to_block_id, note, dates } ; chaînage libre bloc → bloc (fin de la
   contrainte bipartite) ; **cycles autorisés**, exprimés par chaînage de blocs (ex.
   S1 → P1 → C1 → S1) — **pas de clé `condition` sur `Transition`** (précision TSC
   09-11-2026 : la condition structurée est uniquement portée par le bloc Condition).
4. **Associations → Participations** : `state_agent_rel[]` → `participation[]`
   { id, block_id, agent_id, note, dates } (symétrique, vue matrice).
5. **Nouvelle entité Relation** (agent-agent) : `relation[]`
   { id, block_id (ancre), agent_a_id, agent_b_id, typ, note, content, dates } — dirigée,
   typée, **binaire** (`agent_a_id`, `agent_b_id` ; n-aire = évolution hors MVP), ancrée à
   un bloc ; `typ` lu dans une **liste de valeurs en fichier de configuration** (MVP) ;
   état courant d'une paire dérivé des ancres (jamais stocké) ; **pas de clé `clock_id`**
   (ordonnancement = rang du bloc d'ancrage dans le parcours, dérivé de
   `journey_node.sequence_order`).
6. **Nœuds de parcours sur les blocs** : `Journey_node` → `journey_node`
   { id, journey_id, block_id, sequence_order, dates } — suppression de
   `state_to_event_id` / `event_to_state_id` / `state_agent_rel_id` (rattachement sur les
   blocs, appartenance dérivée : une transition appartient à un parcours ssi ses deux
   extrémités y appartiennent ; participation/relation ssi leur bloc d'ancrage y
   appartient). `sequence_order` conservé (DFS depuis le Début, mémoïsation des cycles).
   `active_journey_id` conservé.
7. **Agent** : `typ` {Personnage, Artefact} (EN : {Character, Artefact}) en remplacement de
   {Subject, Object}.
8. **Condition structurée** : portée **uniquement** par le bloc `Condition` { kind (choix /
   artefact / compétence / flag), ref vers un agent Artefact, label } — pas de `condition`
   sur `Transition`.
9. **Cardinalités et notes** : mises à jour (participation Block 0..* ↔ Agent 0..* non
   directionnelle ; transition Block → Block directionnelle, une par paire ordonnée ;
   journey_node Block ↔ Journey via `block_id` ; relation ancrée à un bloc, typée ;
   unicité participation par (bloc, agent) ; cascades de suppression complètes — ne pas
   reproduire le bug planoscript `connection.py:811`).

## Journal

- 2026-11-09 : tâche créée et passée en Doing (décision TSC 09-11-2026, kanban v1).
  Analyse des écarts planoscript → hyperscript réalisée (liste ci-dessus, à valider en
  séance) ; clone et révision des deux documents à faire ensuite.
- 2026-11-09 (suite de séance, précisions TSC) : relations binaires documentées (n-aire
  hors MVP) ; pas de clé `clock_id` (ordonnancement dérivé du rang du bloc d'ancrage dans
  le parcours) ; clé `condition` retirée de `Transition` — le cycle S1 → P1 → C1 → S1
  s'exprime par chaînage de blocs. Reporté dans `docs/conception/03_conception-FR.md`
  (§3, §4, §8).

- 2026-11-09 : `docs/specification/07_data_model-FR.json` et `07_data_model-EN.json` générés (structure plano reprise et modifiée selon les décisions actées — voir liste ci-dessus). Validation : json.load OK sur les deux fichiers ; structures FR/EN identiques hors descriptions. Tâche passée en Review (kanban v2) — en attente de validation TSC.
