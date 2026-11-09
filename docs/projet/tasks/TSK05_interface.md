# TSK05 — Rédaction de l'interface (04_interface-FR/EN.md)

- **Épic** : reconception depuis planoscript — tâche de conception
- **Statut** : Review — en attente de validation TSC (09-11-2026)
- **Date de création** : 2026-11-09
- **Dépendances** : → #TSK04 (en Review)

## Objectif

Rédiger `docs/specification/04_interface-FR.md` et `04_interface-EN.md` pour hyperscript,
à partir de `04_interface` planoscript (v2.2) révisé selon les décisions actées et la
vérification doc ↔ code effectuée en séance (TSK 09-11-2026).

## Cadrage (décisions TSC 09-11-2026)

- **Esthétique conservée** : thème sombre « charte 98 » de planoscript, toutes les
  couleurs/dimensions/polices pilotées par `config.json` via un module de thème
  centralisé (aucune valeur en dur dans le code UI). Évolutions de style possibles en
  cours de conception.
- Vues « Agents » et « Relations » : **spécification laissée vide** (re-conception à
  venir ; maquette de « Relations » en phase de conception).
- **Barre de zoom oubliée** (zoom post-MVP ; entrées Display › Zoom grisées).
- Checklists de fonctionnalités implémentées supprimées ; références RG supprimées ;
  arborescence `src/`, notes de conception et prochaines étapes retirées du document
  (leur place est ailleurs).
- barre de menus = référence à `05_menu-FR/EN.yaml` ; barre d'info pleine largeur
  (30 px) ; onglets nommés sans numérotation (Parcours défaut, Agents, Relations,
  Export) ; minimum MVP = Parcours + Export.
- Doc volontairement incomplet : points marqués « À valider en phase de conception »
  (style des 5 types de blocs, badges, barres latérales, périmètre des vues, langue de
  l'app — unilingue pour l'instant).

## Vérification doc ↔ code planoscript (résumé, séance 09-11-2026)

- Périmé dans le doc : thème clair (code = sombre), fichiers fantômes
  `components_toolbar.py`/`journeys_toolbar.py`/`zoom_bar.py` (absents du code),
  onglet Export « non implémenté » (implémenté, TSK33), aimantation « non implémentée"
  (implémentée, `snap_to_grid`), textes UI français (code en anglais), zoom « contrôles
  existants non connectés » (aucun widget), arborescence src périmée.
- Conforme : structure des menus/stubs, onglets, grille 20/80 + zone visible, scrollbars
  toujours visibles, auto-scroll 50 px, scène 4000×4000 extensible, nœud 80×40, ports
  8 px, badge 16 px, connexion 2 px, matrice 120×80/case 20×20, dialogues 60/160 px,
  barre d'info 30 px, titre avec projet/chemin, accueil avec lien.

## Livrables

- [x] `docs/specification/04_interface-FR.md`
- [x] `docs/specification/04_interface-EN.md`

## Journal

- 2026-11-09 : tâche créée et passée en Doing (décision TSC 09-11-2026, kanban v9,
  TSK04 en Review). Analyse des écarts + vérification doc ↔ code réalisées en séance ;
  documents à rédiger.
- 2026-11-09 : documents rédigés (FR et EN). Validation : aucune référence RG, aucune checklist, pas d'arborescence src ; thème sombre charte 98 conservé et piloté par config.json ; vues Agents/Relations vides ; zoom hors MVP. TSK05 passée en Review (kanban v10) — en attente de validation TSC.
