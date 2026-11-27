# Hyperscript ::: Tableau kanban du projet

- **Dernière modification** : 27-11-2026 — restructuration du kanban (tableau en id+nom uniquement, résumés en section « Description des tâches », historique centralisé dans les fiches `tasks/`) — état : **To do 1 · Doing 1 · Review 12 · Done 39** (53 tâches).
- **Description** : suivi de l'avancement des tâches (TSKnn) du projet. Format et règles de mise à jour : section « Structure du kanban » ci-dessous.

---

## Structure du kanban

- **Tableau du kanban** (`To do` / `Doing` / `Review` / `Done`) : une ligne par tâche, uniquement `- [ ] TSKnn — Nom` (`- [x]` en `Done`). Ni description, ni dépendances, ni historique dans le tableau.
- **Description des tâches** : une ligne par tâche — identifiant, nom, **résumé**, dépendances (`→ #TSKnn`) et lien vers la fiche. Le détail (analyse, décisions) et **l'historique des actions** (création, passages en Doing/Review/Done avec dates, commits, résultats de tests) sont consignés **uniquement dans la fiche** `tasks/TSKnn_*.md`.
- **Jalons** : liste courte des dates clés ; le détail des séances est dans `SESSIONS.md`.

### Règles de mise à jour

- **Création** : tâche ajoutée en `To do` — ligne id+nom dans le tableau ; ligne id+nom+résumé+dépendances dans « Description des tâches » (fiche « à créer au passage en Doing »).
- **Doing** : uniquement si toutes les dépendances sont en `Review` ou `Done` ; la fiche `tasks/TSKnn_*.md` est créée à ce passage.
- **Review** : après implémentation + tests. **Done** : après validation utilisateur. Dans les deux cas, seule la ligne id+nom est déplacée dans le tableau ; la **date de passage en Done** est renseignée dans la fiche.
- L'historique (dates, commits, résultats de tests) est journalisé uniquement dans la fiche de la tâche — jamais dans le kanban.
- Convention de dépendances : `→ #TSKnn` notée uniquement sur la tâche dépendante (pas de lien inverse sur la tâche bloquante).
- Ce fichier est la source unique de vérité de l'état des tâches.

---

## Jalons

- **09-11-2026** : initialisation du dépôt — spécifications FR/EN (TSK01–TSK06 : modèle de données, scenarii SU, fonctionnalités FN, menu, interface, règles de gestion RG, périmètre MVP).
- **17-11-2026** : socle code + vue « Journeys » opérationnels (TSK07–TSK16 → Done).
- **18–20-11-2026** : agents, participations, relations agent-agent, filtres, panneau latéral, matrice « Relationships » triangle supérieur (TSK17–TSK34 → Done).
- **23-11-2026** : panneau latéral redimensionnable/repliable + ajustements vue « Relationships » (TSK35–TSK36 → Done).
- **26-11-2026** : vue « Preview » (TSK37–TSK38 → Done) ; retours de test séance 12 + export HTML « Export Project... » (TSK39–TSK42 → Review) ; revue de code / dette technique (TSK43 → Doing), refactorisations (TSK44–TSK51 → Review) ; TSK52 post-MVP → To do.

---

## Tableau du kanban

### To do

- [ ] TSK52 — Structure post-MVP (plan TSK43 pt 9)

### Doing

- [ ] TSK43 — Revue de code / dette technique (séance 12, demande TSC)

### Review

- [ ] TSK39 — Retours de test TSC (séance 12, 26-11-2026, 24 points)
- [ ] TSK40 — Correction TSC séance 12
- [ ] TSK41 — Libellés de la vue « Preview » (séance 12)
- [ ] TSK42 — Export HTML du projet « Files › Export Project... » (SU007/FN013, séance 12)
- [ ] TSK44 — Nettoyage du code mort (plan TSK43 pt 1)
- [ ] TSK45 — Factorisation des dialogues (plan TSK43 pt 2)
- [ ] TSK46 — `AgentCardItem` hérite de `BaseNode` (plan TSK43 pt 3)
- [ ] TSK47 — Classe de base des workspaces graphiques (plan TSK43 pt 4)
- [ ] TSK48 — Constantes visuelles centralisées dans `ui/utils/theme.py` (plan TSK43 pt 5)
- [ ] TSK49 — Tailles des dialogues/boutons en `config.json` (plan TSK43 pt 6)
- [ ] TSK50 — Corrections d'encapsulation (plan TSK43 pt 7)
- [ ] TSK51 — Complétion des docstrings en anglais (plan TSK43 pt 8)

### Done

- [x] TSK01 — Révision du modèle de données `docs/specification/07_data_model-FR.json` / `07_data_model-EN.json` (clone depuis planoscript, aligné sur `docs/conception/03_conception-FR.md`)
- [x] TSK02 — Scenarii d’utilisation `docs/specification/01_user_stories-FR.md` / `-EN.md` (SU001–SU012, reprise de la numérotation plano)
- [x] TSK03 — Fonctionnalités `docs/specification/03_features-FR.md` / `-EN.md` (FN001–FN037)
- [x] TSK04 — Menu général `docs/specification/05_menu-EN.yaml` / `-FR.yaml`
- [x] TSK05 — Interface `docs/specification/04_interface-FR.md` / `-EN.md`
- [x] TSK06 — Règles de gestion `docs/specification/02_business_rules-FR.md` / `-EN.md`
- [x] TSK07 — Initialisation de l'arborescence du code source `src/` + `tests/`
- [x] TSK08 — Services et use cases de la carte narrative (`transition_service`, `journey_service`, `journey_sequence_service`, `journey_filter_service`, `participation_badge_service`, use cases `view_management` + tests unitaires)
- [x] TSK09 — Use cases de gestion des parcours (FN023–FN027, FN038) + tests unitaires
- [x] TSK10 — Nœuds graphiques de la vue « Journeys » (`base_node`, `block_node`, `connection`)
- [x] TSK11 — Workspace « Journeys » + barre d'onglets + intégration `main_window` + persistance des layouts (RG060)
- [x] TSK12 — Dialogues (édition bloc, transition, parcours, Set as Default) + câblage des menus `Project` restants
- [x] TSK13 — Tests offscreen vue « Journeys » + matrice de traçabilité
- [x] TSK14 — Ports conditionnels Début/Fin dans la vue « Journeys » (masquage des ports + garde-fous de création de transition)
- [x] TSK15 — Correctif z-order grille (z=-2) sous les transitions (z=-1) dans `_draw_grid()`
- [x] TSK16 — Retours de tests visuels TSC (séance n°04)
- [x] TSK17 — Services et use cases agents & participations (FN030/FN031, RG032/RG033) + tests unitaires
- [x] TSK18 — Dialogues agents + menu `Project › Agents`
- [x] TSK19a — Filtre agent dans la vue « Journeys » (FN039, RG063/RG064) + menu Display › Agent
- [x] TSK19b — Vue « Agents » re-conçue
- [x] TSK20 — Relations agent-agent (FN034/RG035)
- [x] TSK21 — Snap des cartes agent sur cellule invisible à la libération (évolution RG065)
- [x] TSK22 — Placement d'une nouvelle carte agent sur la première cellule libre à droite de la boîte englobante des cartes existantes
- [x] TSK23 — Dépôt d'une carte contraint à l'anneau (1 cellule) de la boîte englobante des autres cartes
- [x] TSK24 — Snap des blocs sur la grille à la libération uniquement (position libre pendant le drag)
- [x] TSK25 — Relation agent-agent non dirigée (révision RG035, paire non ordonnée stockée triée)
- [x] TSK26 — RG068
- [x] TSK27 — Vue « Relationships » (SU012/FN036, RG069/RG070)
- [x] TSK28 — Évolutions mineures (demande TSC séance 09)
- [x] TSK29 — Matrice « Relationships » façon planoscript (révision RG070 séance 09)
- [x] TSK30 — Retours de test TSC (séance 10)
- [x] TSK31 — Retours de test TSC (séance 10, 2ᵉ salve, 8 points)
- [x] TSK32 — Re-conception de la vue « Relationships » en 3 colonnes (agents+ports / liens non directionnels / agents+ports, panneau latéral conservé, création façon transition, extension vers le bas uniquement)
- [x] TSK33 — Panneau latéral des filtres (Journey + Agent) reporté dans la vue « Journeys »
- [x] TSK34 — Retours de test TSC (séance 10, 3ᵉ salve, points 2–4)
- [x] TSK35 — Panneau latéral redimensionnable + repliable par icône
- [x] TSK36 — Vue « Relationships » (retours TSC séance 11)
- [x] TSK37 — Conception de la vue « Preview » (ex-« Export », SU010/FN033)
- [x] TSK38 — Implémentation de la vue « Preview » (SU010/FN033, conception actée TSK37)

---

## Description des tâches

- TSK01 — Révision du modèle de données `docs/specification/07_data_model-FR.json` / `07_data_model-EN.json` (clone depuis planoscript, aligné sur `docs/conception/03_conception-FR.md`) — fiche `tasks/TSK01_data_model_revision.md`

- TSK02 — Scenarii d’utilisation `docs/specification/01_user_stories-FR.md` / `-EN.md` (SU001–SU012, reprise de la numérotation plano) → #TSK01 — fiche `tasks/TSK02_user_stories.md`

- TSK03 — Fonctionnalités `docs/specification/03_features-FR.md` / `-EN.md` (FN001–FN037) → #TSK02 — fiche `tasks/TSK03_features.md`

- TSK04 — Menu général `docs/specification/05_menu-EN.yaml` / `-FR.yaml` → #TSK03 — fiche `tasks/TSK04_menu.md`

- TSK05 — Interface `docs/specification/04_interface-FR.md` / `-EN.md` → #TSK04 — fiche `tasks/TSK05_interface.md`

- TSK06 — Règles de gestion `docs/specification/02_business_rules-FR.md` / `-EN.md` → #TSK05 — fiche `tasks/TSK06_business_rules.md`

- TSK07 — Initialisation de l'arborescence du code source `src/` + `tests/` → #TSK06 — fiche `tasks/TSK07_code_init.md`

- TSK08 — Services et use cases de la carte narrative (`transition_service`, `journey_service`, `journey_sequence_service`, `journey_filter_service`, `participation_badge_service`, use cases `view_management` + tests unitaires) → #TSK07 — fiche `tasks/TSK08_map_services_usecases.md`

- TSK09 — Use cases de gestion des parcours (FN023–FN027, FN038) + tests unitaires → #TSK08 — fiche `tasks/TSK09_journey_usecases.md`

- TSK10 — Nœuds graphiques de la vue « Journeys » (`base_node`, `block_node`, `connection`) → #TSK08 — fiche `tasks/TSK10_graph_nodes.md`

- TSK11 — Workspace « Journeys » + barre d'onglets + intégration `main_window` + persistance des layouts (RG060) → #TSK08, #TSK10 — fiche `tasks/TSK11_journeys_workspace.md`

- TSK12 — Dialogues (édition bloc, transition, parcours, Set as Default) + câblage des menus `Project` restants → #TSK09, #TSK11 — fiche `tasks/TSK12_dialogs_menus.md`

- TSK13 — Tests offscreen vue « Journeys » + matrice de traçabilité → #TSK11, #TSK12 — fiche `tasks/TSK13_offscreen_tests.md`

- TSK14 — Ports conditionnels Début/Fin dans la vue « Journeys » (masquage des ports + garde-fous de création de transition) → #TSK10, #TSK11 — fiche `tasks/TSK14_conditional_ports.md`

- TSK15 — Correctif z-order grille (z=-2) sous les transitions (z=-1) dans `_draw_grid()` → #TSK11 — fiche `tasks/TSK15_grid_zorder_fix.md`

- TSK16 — Retours de tests visuels TSC (séance n°04) : couleurs (config.json + theme.py), position du bloc Start à la création, tirets de sélection, survol des transitions, libellés des menus Project et contextuel, ligne « Type » du dialogue d'édition → #TSK10, #TSK11, #TSK12 — fiche `tasks/TSK16_visual_feedback.md`

- TSK17 — Services et use cases agents & participations (FN030/FN031, RG032/RG033) + tests unitaires → #TSK08 — fiche `tasks/TSK17_agent_participation_usecases.md`

- TSK18 — Dialogues agents + menu `Project › Agents` → #TSK17 — fiche `tasks/TSK18_agent_dialogs_menus.md`

- TSK19a — Filtre agent dans la vue « Journeys » (FN039, RG063/RG064) + menu Display › Agent → #TSK11, #TSK17 — fiche `tasks/TSK19a_agent_filter.md`

- TSK19b — Vue « Agents » re-conçue : points d'ancrage + cartes agent + persistance niveau projet + menu contextuel bloc « Associate agents... » (RG065–RG067, FN030) → #TSK11, #TSK17, #TSK18 — fiche `tasks/TSK19b_agents_view.md`

- TSK20 — Relations agent-agent (FN034/RG035) : use cases + dialogue + menu `Project › Relationships` → #TSK17, #TSK25, #TSK26 — fiche `tasks/TSK20_relationships.md`

- TSK21 — Snap des cartes agent sur cellule invisible à la libération (évolution RG065) → #TSK19b — fiche `tasks/TSK21_agent_card_cell_snap.md`

- TSK22 — Placement d'une nouvelle carte agent sur la première cellule libre à droite de la boîte englobante des cartes existantes → #TSK21 — fiche `tasks/TSK22_agent_card_placement.md`

- TSK23 — Dépôt d'une carte contraint à l'anneau (1 cellule) de la boîte englobante des autres cartes → #TSK22 — fiche `tasks/TSK23_agent_card_release_ring.md`

- TSK24 — Snap des blocs sur la grille à la libération uniquement (position libre pendant le drag) → #TSK11 — fiche `tasks/TSK24_block_snap_on_release.md`

- TSK25 — Relation agent-agent non dirigée (révision RG035, paire non ordonnée stockée triée) → #TSK01 — fiche `tasks/TSK25_relationship_non_directed.md`

- TSK26 — RG068 : bloc Start rattaché à tous les parcours, non modifiable → #TSK09 — fiche `tasks/TSK26_start_all_journeys.md`

- TSK27 — Vue « Relationships » (SU012/FN036, RG069/RG070) → #TSK20, #TSK26 — fiche `tasks/TSK27_relationships_view.md`

- TSK28 — Évolutions mineures (demande TSC séance 09) : ordre des onglets « Agents » avant « Journeys » (vue active par défaut inchangée) + type « Undefined » en tête de `relationship_types` avec sa couleur dans `config.json` → #TSK27 — fiche `tasks/TSK28_minor_evolutions.md`

- TSK29 — Matrice « Relationships » façon planoscript (révision RG070 séance 09) : scène custom, cellules carrées 100×100, ordres lignes/colonnes indépendants persistés au niveau projet, cellule cliquable → dialogue création/édition pré-rempli → #TSK27 — fiche `tasks/TSK29_relationships_matrix.md`

- TSK30 — Retours de test TSC (séance 10) : vue par défaut « Agents », placement cartes agent coin haut gauche + extension droite/bas, matrice « Relationships » ancrée haut gauche façon planoscript (grille pleine zone visible, point central, case à cocher cercle or, création « Undefined » au clic gauche, menu contextuel au clic droit, ascenseurs), correctifs infobulle et drag, séparateur panneau latéral, filtre Journey du panneau → #TSK27, #TSK28, #TSK29 — fiche `tasks/TSK30_tsc_feedback_session10.md`

- TSK31 — Retours de test TSC (séance 10, 2ᵉ salve, 8 points) : marge de la 1ʳᵉ carte = écart entre cartes, `contextMenuEvent` `event.pos()`, diagonale estompée par identité d'agent, cellules transparentes, points sur tout l'espace visible, ascenseurs matrice stylés, séparateur épaissi, panneau latéral → #TSK30 — fiche `tasks/TSK31_tsc_feedback_session10b.md`

- TSK32 — Re-conception de la vue « Relationships » en 3 colonnes (agents+ports / liens non directionnels / agents+ports, panneau latéral conservé, création façon transition, extension vers le bas uniquement) → #TSK31 — fiche à créer au passage en Doing

- TSK33 — Panneau latéral des filtres (Journey + Agent) reporté dans la vue « Journeys » : extraction en widget partagé `FiltersSidePanel`, signaux câblés vers les mêmes handlers que le menu Display, resync des panneaux après chaque CRUD parcours/agent → #TSK31 (TSK32 en dépend aussi) — fiche `tasks/TSK33_filters_panel_journeys.md`

- TSK34 — Retours de test TSC (séance 10, 3ᵉ salve, points 2–4) : `showEvent` → `_draw_grid()` (grille pleine dès le 1ᵉʳ affichage), `scene().removeItem(card)` au lieu de `deleteLater()` sur `QGraphicsItem`, fenêtre réductible (`setGeometry`, `setMinimumSize` supprimé) → #TSK32, #TSK33 — fiche `tasks/TSK34_tsc_feedback_session10c.md`

- TSK35 — Panneau latéral redimensionnable + repliable par icône : handle personnalisé `SidePanelHandle` (chevron ◀/▶), `setFixedWidth` → `setMinimumWidth` (`side_panel_min_width_px` = 180), plancher dur au drag, largeur standard par projet, synchro Journeys/Relationships, repli de session (RG047) → #TSK33, #TSK34 — fiche `tasks/TSK35_side_panel_resize_collapse.md`

- TSK36 — Vue « Relationships » (retours TSC séance 11) : plus de point central en fond, carte Relationship à la taille des cartes Agent de la matrice (80×40, centrée) → #TSK32, #TSK35 — fiche `tasks/TSK36_relationships_dots_card_size.md`

- TSK37 — Conception de la vue « Preview » (ex-« Export », SU010/FN033) : renommage Export → Preview, aperçu lecture seule à liens hypertexte internes régénéré à chaque bascule, rendu selon filtres actifs, jamais de marquage « modifiés », sections a)–g) (projet, agents, carte, parcours, parcours courant, orphelins, agents du projet) ; export fichier SU007/FN013 hors périmètre MVP → #TSK33 — fiche `tasks/TSK37_preview_view_conception.md`

- TSK38 — Implémentation de la vue « Preview » (SU010/FN033, conception actée TSK37) : service Qt-free `core/services/preview_service.py`, `PreviewWorkspace(QTextBrowser)` read-only, onglet + panneau latéral de filtres partagé, filtres MainWindow (RG047/RG048), tests unitaires + offscreen → #TSK37, #TSK33 — fiche `tasks/TSK38_preview_view_implementation.md`

- TSK39 — Retours de test TSC (séance 12, 26-11-2026, 24 points) : menus/bascules de vue/grisement selon vue active et sélection, dialogues (parcours, relation, bloc + participations), matrice « Relationships », panneau latéral (règle 2.4), position des nouveaux blocs dans la zone visible, vue « Preview » → #TSK37, #TSK38 — fiche `tasks/TSK39_tsc_feedback_session12.md`

- TSK40 — Correction TSC séance 12 : règle 2.4 inversée dans le panneau latéral (« All journeys » → `lb (parcours…)`, parcours filtré → `lb (typ)`) + renommages « Journey Filter » / « Agent Filter » / « Block Sequence » → #TSK39 — fiche `tasks/TSK40_side_panel_labels_2_4_inversion.md`

- TSK41 — Libellés de la vue « Preview » (séance 12) : « Participations: » pour les agents participants d'un bloc, « Relationships: » devant chaque relation ancrée → #TSK39 — fiche `tasks/TSK41_preview_labels.md`

- TSK42 — Export HTML du projet « Files › Export Project... » (SU007/FN013, séance 12) : dossier `<lb projet>/` dans le dossier parent choisi (`index.html` + `journey-<id>.html` + `agents.html` + `style.css`), rendu non filtré via `PreviewService`, use case Qt-free lecture seule (RG058) ; « Export/Import Map... » restent grisés (post-MVP) → #TSK38 — fiche `tasks/TSK42_export_project_html.md`

- TSK43 — Revue de code / dette technique (séance 12, demande TSC) : analyse de `src/` — code mort, duplication, principes d'implémentation (`core/` Qt-free, RG058, pas de valeurs UI en dur), nommages, docstrings manquants — livrable = constats chiffrés file:line + plan de refactorisation, sans modification de code — fiche `tasks/TSK43_code_review_technical_debt.md`

- TSK44 — Nettoyage du code mort (plan TSK43 pt 1) : définitions non référencées, constantes et imports morts, ajustement des tests — fiche `tasks/TSK44_dead_code_cleanup.md`

- TSK45 — Factorisation des dialogues (plan TSK43 pt 2) : base commune `ui/dialogs/base_dialog.py` (`FormDialog`/`SelectionDialog`) héritée par les 8 dialogues → #TSK44 — fiche `tasks/TSK45_dialog_base_class.md`

- TSK46 — `AgentCardItem` hérite de `BaseNode` (plan TSK43 pt 3) : suppression des méthodes dupliquées avec `base_node.py` → #TSK44 — fiche `tasks/TSK46_agent_card_inherit_base_node.md`

- TSK47 — Classe de base des workspaces graphiques (plan TSK43 pt 4) : `BaseGraphicsWorkspace(QGraphicsView, QObject)` partagée par `AgentsWorkspace` et `JourneysWorkspace` → #TSK44 — fiche `tasks/TSK47_workspace_base_class.md`

- TSK48 — Constantes visuelles centralisées dans `ui/utils/theme.py` (plan TSK43 pt 5) → #TSK44 — fiche `tasks/TSK48_theme_constants_centralization.md`

- TSK49 — Tailles des dialogues/boutons en `config.json` (plan TSK43 pt 6) : ~26 nombres magiques remplacés par des clés `dialog_*_px` lues via `_get_config` → #TSK44 — fiche `tasks/TSK49_dialog_sizes_config.md`

- TSK50 — Corrections d'encapsulation (plan TSK43 pt 7) : méthodes privées appelées hors classe rendues publiques → #TSK44 — fiche `tasks/TSK50_encapsulation_fixes.md`

- TSK51 — Complétion des docstrings en anglais (plan TSK43 pt 8) : classes + méthodes publiques de `src/` → #TSK44–TSK50 — fiche `tasks/TSK51_docstrings_completion.md`

- TSK52 — Structure post-MVP (plan TSK43 pt 9) : éclater `main_window.py` (1 616 lignes) en modules, décider du placement de `core/models/view_model.py` — conception préalable requise → #TSK51 — fiche `tasks/TSK52_main_window_split_post_mvp.md`
