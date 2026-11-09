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

### Choix actés (séance TSC 09-11-2026)
- « Parcours » / « Journey » acté (« Version » conservée comme alternative future) ; « Branch » remplacé par le terme bilingue « Pivot ».
- Typage des relations : liste de valeurs en fichier de configuration pour le MVP ; enrichissement par l'auteur hors MVP.
- MVP aligné sur planoscript : une seule carte narrative par projet (le modèle prévoit N cartes dès le MVP), pas de contrôle de cohérence des parcours (hors MVP), pas de migration des projets planoscript existants.
- Cycles directs possibles moyennant une condition explicite sur la transition (ex. scène S —C→ S).
- À définir en phase de conception : maquette de la vue « Relations », exports (technique dev, par événements, réimport), zoom, annuler/rétablir, barres latérales.
- Dette TSK34 de planoscript prise en compte dès le début (use cases, pas d'écriture directe du modèle depuis l'UI, bug export `_esc(rel.agent_id)` à traiter dès la conception).
- TSK01 du kanban = rédaction des documents de conception ; documents existants de `docs/conception/` à revoir si nécessaire (en-têtes « Planoscript »).

### Problèmes rencontrés
- Aucun.
