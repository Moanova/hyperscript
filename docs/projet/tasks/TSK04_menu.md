# TSK04 — Rédaction du menu général (05_menu-EN.yaml / 05_menu-FR.yaml)

- **Épic** : reconception depuis planoscript — tâche de conception
- **Statut** : Review — en attente de validation TSC (09-11-2026)
- **Date de création** : 2026-11-09
- **Dépendances** : → #TSK03 (en Review)

## Objectif

Rédiger `docs/specification/05_menu-EN.yaml` et `05_menu-FR.yaml` pour hyperscript
(l'application est unilingue pour l'instant ; les deux versions documentaires sont
fournies pour harmoniser la documentation), à partir du menu planoscript
(`05_menu-EN.yaml` v2.2) révisé selon la structure actée en séance TSC 09-11-2026
(note `docs/conception/03_conception-FR.md` §8, point 15).

## Structure actée

- **Files** (ordre planoscript avec séparateurs) : New Project... (Ctrl+N), Open...
  (Ctrl+O), Close (Ctrl+W), Save (Ctrl+S), Save as... (Ctrl+Shift+S), sép.,
  **Export Map grisée en MVP** (export fichier hors MVP ; l'aperçu in-app vue
  « Export » est dans le MVP et n'est pas concerné par cette entrée), **Import Map
  grisée en MVP** (importer une carte exportée dans le projet courant ; distinct de la
  non-migration planoscript), sép., **Recent Projects... grisée en MVP** (dynamique),
  sép., Quit (Ctrl+Q).
- **Edit** : Undo (Ctrl+Z), Redo (Ctrl+Y), sép., Cut (Ctrl+X), Copy (Ctrl+C),
  Paste (Ctrl+V) — **toutes grisées en MVP** ; History et Delete supprimées (à
  réajouter après le MVP si besoin).
- **Display** : Journey (liste cochable dynamique : « All journeys » en tête, cochée =
  filtre désactivé, défaut à l'ouverture ; filtre appliqué à toutes les vues, non
  persisté) ; Zoom › In (Ctrl+=) / Out (Ctrl+-) / Reset (Ctrl+0), **grisé en MVP**.
- **Project** :
  - View › Journeys, Agents, Relationships, Export (vues nommées, sans numérotation ;
    entrées stubbées, vues activées par la barre d'onglets ; minimum MVP : Journeys +
    Export ; « Export » pourra être renommée ultérieurement).
  - Agents › New..., Edit, Copy, Delete, **Associate with Block...** (participation ;
    remplace « Link to Block »).
  - Narrative Blocks › New... › Scene / Pivot / Condition / Ending (**Start/Début
    volontairement absent** : auto-créé, unique, non duplicable — règle de gestion à
    venir), Edit, Copy, Delete.
  - Transitions › New..., Edit, Delete.
  - Journeys › New..., Edit, **Copy**, Delete (« Copy » = terme de duplication retenu
    sur tous les sous-menus).
  - Relationships › New..., Edit, Delete (relations agent-agent ; EN « Relationships »,
    FR « Relations »).
- **About** : Change Log, About Hyperscript.
- Raccourcis clavier conservés. **Menu contextuel** : aligné dynamiquement sur le menu
  applicatif selon la vue active et les objets graphiques sélectionnés.
- Pas de références aux règles de gestion (en cours de revue).

## Livrables

- [x] `docs/specification/05_menu-EN.yaml`
- [x] `docs/specification/05_menu-FR.yaml`

## Journal

- 2026-11-09 : tâche créée et passée en Doing (décision TSC 09-11-2026, kanban v7,
  TSK03 en Review). Substitution EN « Relationship » appliquées aux docs EN
  (07_data_model-EN.json, 01_user_stories-EN.md, 03_features-EN.md ; clés JSON
  `relation` → `relationship` dans les deux versions JSON). Alignements : SU002/SU007
  (export fichier hors MVP, aperçu in-app dans le MVP), FN007 (Recent grisé), FN013
  (Export Map grisé). Documents à rédiger.
- 2026-11-09 : `05_menu-EN.yaml` et `05_menu-FR.yaml` rédigés et validés (PyYAML). Structure conforme à la décision actée (point 15 de la note). TSK04 passée en Review (kanban v8) — en attente de validation TSC.
