# TSK03 — Rédaction des fonctionnalités (03_features-FR/EN.md)

- **Épic** : reconception depuis planoscript — tâche de conception
- **Statut** : Review — en attente de validation TSC (09-11-2026)
- **Date de création** : 2026-11-09
- **Dépendances** : → #TSK02 (en Review)

## Objectif

Rédiger `docs/specification/03_features-FR.md` et `03_features-EN.md` pour hyperscript,
en reprenant la numérotation des fonctionnalités planoscript (FN001–FN033, révisées selon
les décisions actées) et en ajoutant FN034–FN037.

## Décisions appliquées (séance TSC 09-11-2026)

- FN027 : la suppression d'un parcours **réaffecte les rattachements de ses blocs au
  parcours par défaut** (aucun bloc orphelin).
- FN029 : le filtre de parcours est **désactivé par défaut** à l'ouverture d'un projet
  et **s'applique à toutes les vues**.
- Les espaces de travail sont référencés **par leur nom**, sans numérotation
  (« Parcours », « Agents », « Relations », « Export ») — y compris pour l'aperçu
  d'export (FN033).
- Nouvelles fonctionnalités actées : **FN034** relations agent-agent, **FN035**
  condition structurée + promotion Scène → Pivot, **FN036** vue « Relations »,
  **FN037** liste des types de relations en fichier de configuration.
- Changement de vocabulaire : bloc narratif, transition, participation, relation
  agent-agent, parcours, Personnage/Artefact, vue « Parcours » (ex-Events).
- **Pas de références aux règles de gestion** dans les fonctionnalités tant qu'elles
  ne sont pas révisées ; **champ « État » supprimé** (nouveau projet).
- FN019 déplacée dans la section « Blocs narratifs » : le rattachement aux parcours se
  gère sur le bloc (liste jamais vidable), plus sur la relation.
- FN020–FN022 réécrites en « Transitions » : chaînage libre, cycles autorisés, seule
  interdiction = doublon sur la paire ordonnée de blocs ; rattachement dérivé.
- Hors périmètre / à définir en phase de conception : multi-cartes (MVP 1 carte),
  import de carte, pas de migration plano, export technique/réimport et « par
  événements », zoom, annuler/rétablir, barres latérales, contrôle de cohérence
  (hors MVP), enrichissement de la liste des types de relations (hors MVP),
  relations à plus de deux agents (hors MVP).

## Livrables

- [x] `docs/specification/03_features-FR.md`
- [x] `docs/specification/03_features-EN.md` (contenu identique, traduit)

## Journal

- 2026-11-09 : tâche créée et passée en Doing (décision TSC 09-11-2026, kanban v5,
  TSK02 en Review). Analyse des écarts plano → hyperscript réalisée en séance
  (FN001–FN033 revus, FN034–FN037 ajoutés) ; documents à rédiger.
- 2026-11-09 : documents rédigés (FN001–FN037, FR et EN). Validation : 37 fonctionnalités par version ; aucune référence RG, aucun champ « État », aucune numérotation des espaces de travail (grep de contrôle). TSK03 passée en Review (kanban v6) — en attente de validation TSC.
