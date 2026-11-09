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
| **Relation** (typée) | **Relationship** (typed) | — (hors MVP planoscript ; texte libre dans les faits) |
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
- « Relation » (EN : « Relationship » ; clé JSON : `relationship`) désigne exclusivement les relations agent-agent ; les menus ne
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
- **Transition** { id, from_block_id, to_block_id, note, dates } — dirigée
  bloc → bloc ; tout chaînage autorisé (plus de contrainte bipartite, cycles
  compris — §4). **Pas de clé `condition` sur la transition** : la condition
  structurée est uniquement portée par le bloc Condition (décision TSC
  09-11-2026, précisée en séance).
- **Participation** { id, block_id, agent_id, note, dates } — présence d'un
  agent dans un bloc (symétrique, vue matrice).
- **Relation** { id, block_id (ancre), agent_a_id, agent_b_id, typ, note,
  content, dates } — dirigée et typée, **binaire** (`agent_a_id`, `agent_b_id`) :
  une relation à plus de deux agents est une évolution **hors MVP**. **Ancrée à
  un bloc** : « à ce moment du récit, la relation A —typ→ B est vraie ».
  L'historique d'une paire = ses ancres ordonnées par rang du bloc ; l'état
  courant à un bloc = dernière ancre de rang ≤ rang du bloc (**dérivé, jamais
  stocké**). Pas de clé d'horloge (`clock_id`) : le rang est celui du bloc
  d'ancrage dans le parcours (`journey_node.sequence_order`).
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
  sortante (vers la scène gardée). Porte la condition structurée — **unique
  support** de celle-ci (pas de `condition` sur Transition) : kind (choix /
  artefact / compétence / flag), ref vers un agent Artefact, label. Chaîner des
  blocs Condition = ET ; deux Condition issus d'un même Pivot = OU.
- **Cycles** : autorisés, exprimés par chaînage de blocs — ex. **S1 (Scène) →
  P1 (Pivot) → C1 (Condition) → S1** (décision TSC 09-11-2026 précisée en séance :
  le « cycle direct » S —C→ S se réalise en fait via un Pivot et un bloc
  Condition). L'invariant du Pivot (degré sortant ≥ 2) s'applique : la branche
  revenant à S1 est l'une d'au moins deux branches. La séquence DFS mémoïse les
  cycles.
- **Appartenance à un parcours dérivée** (règle uniforme) : une Transition
  appartient à un parcours ssi **ses deux extrémités** y appartiennent ; une
  Participation ou une Relation y appartient ssi son **bloc d'ancrage** y
  appartient. (Résout par construction la pollution croisée des associations
  constatée sur testCase01.)
- **Rattachement des blocs aux parcours** : aucun bloc orphelin — tout bloc
  appartient à au moins un parcours ; un bloc nouvellement créé est
  automatiquement rattaché au parcours actif (ou au parcours par défaut) ;
  un bloc ne peut pas être retiré de son dernier parcours (décision TSC
  09-11-2026, règle rétablie d'une version antérieure de planoscript).
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

1. **Vue « Parcours » / Journeys** (ex-vue Events) : graphe des blocs, rendu
   par type ; filtre par parcours (non persisté) ; badges de participations
   (dénomination actée en séance TSC 09-11-2026).
2. **Vue Agents** : matrice agents × blocs des Participations.
3. **Espace de travail « Relations »** (EN : « Relationships ») (anticipé par `99_mvp_scope-FR.md` §5
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
5. Cycles possibles, exprimés par chaînage de blocs (ex. S1 → P1 → C1 → S1) ; **pas de clé `condition` sur la Transition** (la condition structurée est portée par le bloc Condition).
6. Maquette de la vue « Relations » à définir durant la phase de conception.
7. Pas de migration des projets planoscript existants (deux projets de test seulement).
8. Pas de contrôle de cohérence des parcours dans le MVP (fonctionnalité hors MVP).
9. Exports, zoom et fonctions d'édition (annuler/rétablir) à définir durant la phase de conception.
10. Dette technique de planoscript prise en compte dès le début (meilleures pratiques) ; barres latérales, export par événements et export technique pour réimport à définir en phase de conception.
11. TSK01 du kanban = rédaction des documents de conception ; documents existants à revoir si nécessaire.
12. Précisions de la même séance : relations **binaires** (`agent_a_id`, `agent_b_id`) jusqu'à éventuelle évolution hors MVP ; pas de clé `clock_id` (l'ordonnancement des relations est le rang du bloc d'ancrage dans le parcours, dérivé de `journey_node.sequence_order`) ; clé `condition` retirée de l'entité Transition.

13. Précisions de la même séance (scenarii d’utilisation) : la vue principale (ex-Events)
s’appelle **« Parcours » / Journeys** ; l’export de lecture reste en **HTML autonome** ;
**aucun bloc orphelin** (rattachement automatique au parcours actif/par défaut, rétabli) ;
périmètre MVP des vues non acté au-delà du minimum **vues « Parcours » et « Export »** ;
les scenarii « vue agents », « aperçu d’export » et « vue Relations » sont initialisés mais à finaliser
après la phase de conception ; pas de références aux règles de gestion ni aux clés techniques dans les
scenarii (sémantique uniquement) ; numérotation des scenarii libre (reprise de la numérotation
planoscript, SU011+ ajoutés).

14. Précisions de la même séance (fonctionnalités) : suppression d'un parcours →
**réaffectation des rattachements de ses blocs au parcours par défaut** (aucun bloc orphelin) ;
**filtre de parcours désactivé par défaut** et **appliqué à toutes les vues** ; les espaces de
travail sont référencés **par leur nom**, sans numérotation (« Parcours », « Agents », « Relations »,
« Export ») ; pas de références aux règles de gestion dans les fonctionnalités tant qu'elles ne sont
pas révisées ; champ « État » supprimé des fonctionnalités ; nouvelles fonctionnalités **FN034–FN037**
actées (relations agent-agent, condition structurée/promotion Scène→Pivot, vue « Relations », liste des
types de relations en fichier de configuration).

15. Arbitrages de la même séance (menu et divers) : menu général acté (voir `docs/specification/05_menu-EN.yaml` /
`05_menu-FR.yaml`) —
**Files** dans l'ordre planoscript avec séparateurs (New Project, Open, Close, Save, Save as, sép., Export Map,
Import Map, sép., Recent Projects..., sép., Quit) ; **Export Map** et **Import Map** grisées en MVP, **Recent Projects...**
grisée en MVP ; Import Map = importer une carte exportée dans le projet courant (distinct de la non-migration
planoscript) ;
**Edit** réduit à Undo/Redo/Cut/Copy/Paste, toujours grisé en MVP (History et Delete supprimés, à réajouter
après MVP si besoin) ;
**Display** › Journey (liste cochable, « All journeys » en tête, filtre désactivé par défaut, appliqué à toutes les vues,
non persisté) et Zoom grisé en MVP ;
**Project** › View (Journeys, Agents, Relationships, Export — vues nommées, sans numérotation ; minimum MVP :
Journeys + Export ; entrées stubbées, vues activées par la barre d'onglets) ; Agents (New/Edit/Copy/Delete/
**Associate with Block...** — en remplacement de « Link to Block », terme jugé ambigu avec les transitions) ;
Narrative Blocks (New... › Scene/Pivot/Condition/Ending — **Start/Début volontairement absent : auto-créé,
unique, non duplicable**, fera l'objet d'une règle de gestion ; Edit/Copy/Delete) ; Transitions (New/Edit/Delete) ;
Journeys (New/Edit/**Copy**/Delete — « Copy » retenu comme terme de duplication sur tous les sous-menus) ;
Relationships (New/Edit/Delete) ;
**Export sur fichier (Files › Export Map) hors MVP** : seul l'aperçu in-app (vue « Export ») est dans le MVP et n'est pas
concerné par cette entrée de menu ;
en EN, l'entité se nomme **« Relationship »** (FR : « Relation »), la plupart des relations étant entre personnages ;
le menu contextuel doit rester **aligné dynamiquement sur le menu applicatif** selon la vue active et les objets
sélectionnés ; la remarque « Display dynamique selon la vue active » est ignorée pour le moment ; raccourcis clavier
conservés.

## 9. Prochaines étapes

1. **TSK01 (kanban)** : rédiger les documents de conception à partir de cette note
   — spécifications FR/EN (user stories, règles de gestion, features, interface,
   menu, modèle de données, périmètre MVP) et initialisation du kanban ; revue
   des documents existants de `docs/conception/` si nécessaire (en-têtes
   « Planoscript » à corriger dans `01_persona_*` et `02_*_test_case`).
2. Produire la **version EN** de cette note (contenu identique).
