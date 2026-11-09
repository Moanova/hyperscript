# TSK06 — Rédaction des règles de gestion (02_business_rules-FR/EN.md)

- **Épic** : reconception depuis planoscript — tâche de conception
- **Statut** : Review — en attente de validation TSC (09-11-2026)
- **Date de création** : 2026-11-09
- **Dépendances** : → #TSK05 (en Review)

## Objectif

Rédiger `docs/specification/02_business_rules-FR.md` et `-EN.md` pour hyperscript, à
partir de `02_business_rules` planoscript (v2.1) analysé **thème par thème** en séance TSC
09-11-2026 et des décisions actées. Nouvelle numérotation RG (libre) ; 5 thèmes conservés ;
**sémantique pure, aucun terme technique** (le projet pourrait être réimplémenté dans un
autre langage : pas de `shape()`, QPainterPathStroker, QLocalServer, clés JSON, etc.) ;
degrés d'opacité et valeurs d'affichage en configuration, pas dans les règles ; pas de
doublons d'en-têtes de section (bug plano : « ## 2 » en double, RG061 défini deux fois).

## Décisions actées par thème (séance 09-11-2026)

### Thème 1 — Gestion du projet et cycle de vie
- Conservées : RG001–004, RG006, RG011, RG012, RG014, RG047–049 (adaptées).
- Modifiées : RG005 (récents = post-MVP, entrée grisée) ; RG007/008 (menus grisés selon
  projet ouvert + entrées grisées en MVP même avec projet : Export Map, Import Map,
  Recent Projects..., Edit, Zoom) ; RG009/010 (ajout : aucune migration des fichiers
  planoscript) ; RG013 (nouveau projet = « Nouveau projet » + carte « Carte narrative
  principale » + bloc Début auto + parcours par défaut auto) ; RG046 (export fichier hors
  MVP, aperçu in-app seul en MVP).
- Ajoutées : instance unique de l'application ; non-migration des projets planoscript.

### Thème 2 — Structure de la carte narrative
- Conservées (adaptées) : RG015, RG018, RG019, RG020 (étendue), RG021 (étendue), RG035,
  RG037, RG038 (→ Fin degré sortant 0), RG060/061 (→ Début unique, auto-créé, immuable, non
  supprimable, non duplicable, non sélectionnable ailleurs), RG067 (focus, étendu vue Relations).
- Modifiées : RG017 (cascade du bloc : transitions, participations, relations ancrées,
  rattachements), RG031 (Début), RG032 (parcours peut ne pas atteindre de Fin — cohérence
  hors MVP), RG034 (rattachement sur les blocs), RG036 (réaffectation des rattachements au
  parcours par défaut), RG063 (participation unique par (bloc, agent)), RG064 (cascade agent
  → participations + relations), RG068 (matrice → à re-concevoir avec la vue Agents).
- Supprimées : RG033 (remplacée par « transitions libres, cycles autorisés, unicité paire
  ordonnée » + règle de séquence DFS du thème 3), RG058 (cycles autorisés), RG062 (doublon),
  RG065 (fondue dans RG017), RG066 (membership dérivée + pas d'orphelin).
- Ajoutées : typ de bloc immuable après création ; Pivot (degré sortant ≥ 2, promotion
  unidirectionnelle Scène→Pivot) **— règle sujette à révision en cours de conception** ;
  Condition (1 entrante depuis un Pivot, 1 sortante vers la scène gardée, condition
  structurée, ET/OU) **— règle sujette à révision** ; unicités (transition, relation,
  participation) ; aucun bloc orphelin ; relation binaire ancrée à un bloc, typ en
  configuration.

### Thème 3 — Logique des parcours et appartenance
- Conservées : RG022, RG023, RG029, RG055.
- Réécrites : RG025 (jamais d'orphelin), RG026 (appartenance dérivée : transition ssi 2
  blocs, participation/relation ssi bloc d'ancrage), RG027 (rattachement sur le bloc, liste
  jamais vidable), RG054 (transition = paire ordonnée), RG069 (séquence = DFS depuis le
  Début sur les transitions du parcours, branches par id de transition croissant,
  mémoïsation des cycles, repli déterministe, recalcul à chaque modification et au
  chargement, jamais modifiable manuellement).
- Supprimées : RG024, RG052 (remplacées par « aucun bloc orphelin »).
- Ajoutées : duplication d'un parcours copie les rattachements des blocs ; suppression d'un
  parcours réaffecte les rattachements de ses blocs au parcours par défaut.
- Précision : les nœuds de parcours ne référencent que des blocs → suppression d'une
  transition sans cascade sur les nœuds (élimine le bug plano connection.py:811).

### Thème 4 — Visualisation et interaction
- Conservées (adaptées) : RG039, RG040, RG041, RG043, RG044, RG045, RG059 (routage des
  transitions, purement graphique).
- Modifiée : RG042 → filtre appliqué à **toutes les vues**, désactivé par défaut à
  l'ouverture, non persisté ; sous filtre, éléments hors parcours **estompés et non
  interactifs** (degré d'opacité en configuration, pas dans la règle).
- Ajoutées (sémantique, sans termes techniques) : zone cliquable d'un élément graphique =
  sa forme géométrique élargie au-delà de l'épaisseur du trait ; infobulles immédiates au
  survol ; menu contextuel (clic droit sélectionne avant ouverture, aligné dynamiquement sur
  le menu applicatif selon vue active et sélection) ; état du filtre non persisté ; focus
  temporaire (RG067).

### Thème 5 — Architecture technique et modèle de données
- Supprimée : RG050 (remplacée par les règles Début + séquence DFS).
- Conservée : RG051 (métadonnées graphiques dans un fichier dédié, restaurées à la
  réouverture).
- Ajoutées : agents au niveau projet ; l'interface ne modifie jamais directement le modèle
  métier (passage par use cases/services) ; aucune valeur en dur dans l'interface (fichier
  de configuration) ; sauvegarde du projet et des métadonnées graphiques persistantes.

## Livrables

- [x] `docs/specification/02_business_rules-FR.md`
- [x] `docs/specification/02_business_rules-EN.md`

## Journal

- 2026-11-09 : tâche créée et passée en Doing (décision TSC 09-11-2026, kanban v11,
  TSK05 en Review). Analyse par thèmes réalisée et actée en séance (résumé ci-dessus) ;
  documents à rédiger.
- 2026-11-09 : documents rédigés (FR et EN générés depuis une structure commune : 61 règles RG001–RG061, 5 thèmes, alignés ligne à ligne). Validation : aucun terme technique (shape(), QLocalServer, clés JSON...), numérotation séquentielle, pas de section dupliquée, références RG internes valides, règles Pivot/Condition marquées « sujettes à révision », opacité du filtre renvoyée à la configuration. TSK06 passée en Review (kanban v12) — en attente de validation TSC.
