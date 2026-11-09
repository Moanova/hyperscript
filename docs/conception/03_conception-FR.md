# Note de conception du projet « hyperscript »

- **Date** : 2026-11-09
- **Statut** : acté en séance TSC — point de départ de la phase de conception
- **Contexte** : clôture de planoscript le 06-11-2026 (kanban v36), initialisation du
  dépôt hyperscript le 09-11-2026. Cette note part de la note de préconception
  `docs/conception/hyperscript_preconception-FR.md` (dépôt planoscript, actée le
  06-11-2026) et intègre les décisions de la séance du 09-11-2026 (§8).
- **Version EN** : à produire (contenu identique).

---

## 1. Décisions de portée

1. **planoscript est clôturé** ; hyperscript est son successeur, avec cette note
   comme point de départ de la conception.
2. Le périmètre MVP d'hyperscript est aligné sur celui de planoscript partout où
   la séance du 09-11-2026 ne décide pas le contraire (§7) ; le modèle de données
   anticipe néanmoins les évolutions actées (cartes multiples, §3).
3. La **première tâche du kanban (TSK01)** sera précisément la rédaction des
   documents de conception (spécifications FR/EN, kanban) à partir de cette note ;
   les documents existants de `docs/conception/` seront revus si nécessaire.

## 2. Sémantique actée (FR / EN)

| FR | EN | Remplace (planoscript) |
|---|---|---|
| **Bloc narratif** { Début ; Scène ; Pivot ; Condition ; Fin } | **Narrative block** { Start ; Scene ; Pivot ; Condition ; End } | State / Event (deux composants séparés) |
| **Transition** | **Transition** | arc State_to_event / Event_to_state |
| **Participation** | **Participation** | association State_agent_rel (agent ↔ état, non directionnelle) |
| **Relation** (typée) | **Relation** (typed) | — (hors MVP planoscript ; texte libre dans les faits) |
| **Agent** { Personnage ; Artefact } | **Agent** { Character ; Artefact } | Agent { Subject ; Object } |
| **Parcours** | **Journey** | Journey |

- « **Parcours** » (« Journey ») est le terme **acté** (décision TSC 09-11-2026) ;
  « Version » est conservée comme **alternative future**, au cas où un besoin de
  reconception serait détecté.
- « **Pivot** » remplace « Branch » (décision TSC 09-11-2026) ; le terme est
  bilingue (identique en FR et en EN).
- Un seul objet **Bloc narratif** pour tous les types ; le `typ` est choisi à la
  création et **immuable** ensuite (pattern déjà éprouvé pour `Initial`,
  RG061/RG062 de planoscript), avec un rendu visuel différent par type.
- « Relation » désigne exclusivement les relations agent-agent ; les menus ne
  l'utilisent plus comme terme chapeau. Le type d'état « Relation » de planoscript
  disparaît : la scène concernée redevient une **Scène**.
- Le typage des **Relations** est une **liste de valeurs définie pour le MVP dans
  un fichier de configuration** ; son enrichissement par l'auteur est une
  fonctionnalité **hors MVP** (décision TSC 09-11-2026).

## 3. Modèle de données acté

- **Projet** { id, lb, dates, agents[], narrative_maps[] } — agents au niveau
  projet ; la liste de cartes prévoit **dès le MVP** la possibilité de cartes
  multiples (axe épisodes/saisons), même si le périmètre MVP reste d'une seule
  carte par projet (§7).
- **Carte narrative** { id, lb, active_journey_id, blocs[], transitions[],
  participations[], relations[], journeys[] }
- **Bloc narratif** { id, lb, typ ∈ {Début, Scène, Pivot, Condition, Fin},
  note, content, dates }
- **Transition** { id, from_block_id, to_block_id, condition, note, dates } —
  dirigée bloc → bloc ; tout chaînage autorisé (plus de contrainte bipartite) ;
  `condition` est une condition structurée **optionnelle** portée par la
  transition (§4, cycles).
- **Participation** { id, block_id, agent_id, note, dates } — présence d'un
  agent dans un bloc (symétrique, vue matrice).
- **Relation** { id, block_id (ancre), agent_a_id, agent_b_id, typ, note,
  content, dates } — dirigée et typée, **ancrée à un bloc** : « à ce moment du
  récit, la relation A —typ→ B est vraie ». L'historique d'une paire = ses ancres
  ordonnées par rang du bloc ; l'état courant à un bloc = dernière ancre de rang
  ≤ rang du bloc (**dérivé, jamais stocké**).
- **Parcours** { id, lb, default, note } + **nœud de parcours**
  { journey_id, block_id, sequence_order } — le rattachement se fait **sur les
  blocs**, pas sur les transitions.
- **Agent** { id, lb, typ ∈ {Personnage, Artefact}, note, content, dates }.

## 4. Règles actées (invariants, appliqués par l'application)

- **Début** : unique, créé automatiquement, immuable ; peut porter la
  bifurcation (plusieurs transitions sortantes).
- **Fin** : degré sortant 0 ; on interdit d'y ajouter une transition sortante
  (pour prolonger : dupliquer le bloc en Scène).
- **Pivot** : degré sortant ≥ 2 ; **promotion automatique unidirectionnelle**
  Scène → Pivot quand une 2e transition sortante est créée (jamais l'inverse).
  Ses transitions mènent soit à des blocs **Condition** (branche gardée), soit
  directement à des Scènes (choix libre, libellé en note de transition).
- **Condition** : exactement 1 transition entrante (depuis un Pivot) et 1
  sortante (vers la scène gardée). Porte la condition structurée : kind (choix /
  artefact / compétence / flag), ref vers un agent Artefact, label. Chaîner des
  blocs Condition = ET ; deux Condition issus d'un même Pivot = OU.
- **Cycles** : autorisés. Les **cycles directs** deviennent possibles dès lors
  que la transition porte une **condition explicite** (décision TSC 09-11-2026) :
  moyennant la condition C, la transition du port sortant de la scène S peut
  ramener directement au port entrant de la même scène S.
- **Appartenance à un parcours dérivée** (règle uniforme) : une Transition
  appartient à un parcours ssi **ses deux extrémités** y appartiennent ; une
  Participation ou une Relation y appartient ssi son **bloc d'ancrage** y
  appartient. (Résout par construction la pollution croisée des associations
  constatée sur testCase01.)
- **Séquence** : DFS depuis le Début sur les transitions du parcours, branches
  explorées par id de transition croissant, mémoïsation des cycles, repli
  déterministe pour les blocs inatteignables (analogue RG069 de planoscript).
- **Unicité** : une transition par paire ordonnée de blocs ; (bloc, paire, typ)
  unique pour les relations ; une participation unique par (bloc, agent).
- **Cascades** : suppression d'un agent → ses participations et relations ;
  suppression d'un bloc → ses transitions, participations, relations ancrées,
  nœuds de parcours ; suppression d'une transition → nœuds de parcours
  référençant. **Ne pas reproduire le bug planoscript** `connection.py:811` :
  toute modification du modèle passe par les use cases/services (dette TSK34
  prise en compte dès le début, §7).

## 5. Vues (espaces de travail)

1. **Vue Blocs** (ex-vue Events) : graphe des blocs, rendu par type ; filtre
   par parcours (non persisté) ; badges de participations.
2. **Vue Agents** : matrice agents × blocs des Participations.
3. **3e espace de travail « Relations »** (anticipé par `99_mvp_scope-FR.md` §5
   de planoscript) : graphe des agents, arcs étiquetés par typ, annotés des blocs
   d'ancrage ; navigation croisée vers le bloc dans la vue Blocs (analogue
   RG067). **Maquette à définir durant la phase de conception** (décision TSC
   09-11-2026).
4. **Vue Export** : aperçu de lecture par parcours.

## 6. Export

- **Acté** : texte de lecture par parcours — blocs dans l'ordre de séquence ;
  transitions rendues en ligne ; conditions rendues sur leur branche
  (« → si artefact « clé USB » : … ») ; relations listées sous leur bloc
  d'ancrage ; section finale « état des relations » (dernier typ par paire).
- **À définir durant la phase de conception** (décision TSC 09-11-2026) : export
  technique formaté pour l'équipe de développement (frustration n°3 de la
  persona Jen Yen), export « par événements », export technique pour réimport,
  zoom de la visualisation, annuler/rétablir.

## 7. Périmètre MVP acté

- **Une seule carte narrative par projet** (aligné sur planoscript) ; le modèle
  de données prévoit néanmoins les cartes multiples dès le MVP (§3).
- **Pas de contrôle de cohérence des parcours** dans le MVP (impasses, branches
  non terminées, Pivot à une seule branche, Fin non atteinte) — développé comme
  fonctionnalité **hors MVP** (décision TSC 09-11-2026).
- **Pas de migration** des projets planoscript existants (il n'existe à date que
  deux projets de test) — hors périmètre (décision TSC 09-11-2026).
- **Typage des relations** : liste de valeurs en fichier de configuration pour
  le MVP ; enrichissement par l'auteur hors MVP.
- **Dette technique de planoscript (TSK34) prise en compte dès le début** :
  hyperscript est développé selon les meilleures pratiques — architecture
  UI → use cases → services → models, aucune écriture directe du modèle depuis
  l'UI, pas de code mort, et le bug latent export `_esc(rel.agent_id)` traité
  dès la conception (décision TSC 09-11-2026).
- **Barres latérales** (TSK14/TSK30 de planoscript) : à définir durant la phase de
  conception.

## 8. Récapitulatif des décisions de la séance TSC du 09-11-2026

1. « Parcours » / « Journey » acté ; « Version » conservée comme alternative future.
2. « Branch » remplacé par le terme bilingue « Pivot ».
3. Typage des relations : liste de valeurs en fichier de configuration pour le MVP ; enrichissement par l'auteur hors MVP.
4. MVP aligné sur planoscript (une seule carte narrative par projet) ; le modèle prévoit les cartes multiples dès le MVP.
5. Cycles directs possibles moyennant une condition explicite sur la transition (ex. S —C→ S).
6. Maquette de la vue « Relations » à définir durant la phase de conception.
7. Pas de migration des projets planoscript existants (deux projets de test seulement).
8. Pas de contrôle de cohérence des parcours dans le MVP (fonctionnalité hors MVP).
9. Exports, zoom et fonctions d'édition (annuler/rétablir) à définir durant la phase de conception.
10. Dette technique de planoscript prise en compte dès le début (meilleures pratiques) ; barres latérales, export par événements et export technique pour réimport à définir en phase de conception.
11. TSK01 du kanban = rédaction des documents de conception ; documents existants à revoir si nécessaire.

## 9. Prochaines étapes

1. **TSK01 (kanban)** : rédiger les documents de conception à partir de cette note
   — spécifications FR/EN (user stories, règles de gestion, features, interface,
   menu, modèle de données, périmètre MVP) et initialisation du kanban ; revue
   des documents existants de `docs/conception/` si nécessaire (en-têtes
   « Planoscript » à corriger dans `01_persona_*` et `02_*_test_case`).
2. Produire la **version EN** de cette note (contenu identique).
