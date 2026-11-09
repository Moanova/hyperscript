# TSK02 — Rédaction des scenarii d'utilisation (01_user_stories-FR/EN.md)

- **Épic** : reconception depuis planoscript — tâche de conception
- **Statut** : Review — en attente de validation TSC (09-11-2026)
- **Date de création** : 2026-11-09
- **Dépendances** : → #TSK01 (en Review)

## Objectif

Rédiger `docs/specification/01_user_stories-FR.md` et `01_user_stories-EN.md` pour
hyperscript, en reprenant la numérotation des scenarii planoscript (SU001–SU010,
révisés selon les décisions actées) et en ajoutant SU011 (relations agent-agent)
et SU012 (vue « Relations »).

## Décisions appliquées (séance TSC 09-11-2026)

- Vue principale (ex-« Events ») nommée **« Parcours » / Journeys** (évolution
  itérative de la conception).
- Export de lecture en **HTML autonome** (comme planoscript).
- **Aucun bloc orphelin** : les blocs sont directement rattachés aux parcours ;
  rattachement automatique au parcours actif/par défaut rétabli (règle d'une
  version antérieure de planoscript) ; un bloc ne peut être retiré de son
  dernier parcours.
- SU009 (vue agents), SU010 (aperçu d'export) et SU012 (vue « Relations »)
  **initialisés mais à finaliser après la phase de conception** ; périmètre MVP
  des vues non acté au-delà du minimum **vues « Parcours » et « Export »**
  (la vue « Export » pourra être renommée ultérieurement).
- Périmètre exact de l'export de lecture, zoom et fonctions d'édition
  (annuler/rétablir) : à définir durant la phase de conception.
- Pas de références aux règles de gestion (entièrement à revoir) ni aux clés
  techniques du modèle de données dans les scenarii : **sémantique uniquement**
  (blocs narratifs, pivots, transitions, participations, relations, parcours,
  agents).
- Numérotation libre : reprise de la numérotation planoscript (moins de
  modifications), SU011+ pour les nouveautés.
- MVP : une seule carte narrative par projet (modèle prévu pour N) ; pas de
  contrôle de cohérence des parcours (hors MVP) ; pas de migration des projets
  planoscript ; typage des relations par liste de valeurs en fichier de
  configuration (enrichissement par l'auteur hors MVP).

## Livrables

- [x] `docs/specification/01_user_stories-FR.md`
- [x] `docs/specification/01_user_stories-EN.md` (contenu identique, traduit)

## Journal

- 2026-11-09 : tâche créée et passée en Doing (décision TSC 09-11-2026, kanban v3,
  TSK01 en Review). Analyse des écarts planoscript → hyperscript réalisée en séance
  (SU001–SU010 revus, SU011/SU012 ajoutés, écarts sémantiques listés) ; documents
  rédigés.
- 2026-11-09 : documents rédigés (SU001–SU012, FR et EN). Validation : 12 scenarii par version ; aucune référence RG/FN ni clé technique (grep de contrôle vide). SU009/SU010/SU012 marqués « initialisé, à finaliser après la phase de conception ». Tâche passée en Review (kanban v4) — en attente de validation TSC.
