# Conception — Vue « Preview » (aperçu de lecture in-app) — TSK37, SU010 / FN033

- **Date** : 23-11-2026 (séance 11)
- **Statut** : conception actée (décisions TSC séance 11) — implémentation à venir (tâche dédiée après TSK37)
- **Contexte** : SU010/FN033 prévoyaient une vue « Export » (aperçu in-app, MVP minimal) ; la PoC planoscript a livré un aperçu équivalent (TSK31/TSK33 plano : onglet « Export », `ExportWorkspace(QTextBrowser)` + `ExportService.build_reading_text`, export fichier FN013 non implémenté des deux côtés). La vue est **renommée « Preview »**.
- **Hors périmètre** : SU007 / FN013 (export sur fichier HTML, « Files › Export Map... » grisé, post-MVP) — inchangé ; la coexistence « Preview » (vue in-app) / « Export Map » (fichier, post-MVP) est assumée dans les spécifications.

## 1. Décisions actées (TSC, séance 11)

1. **Renommage Export → Preview** : la vue et tous les éléments qui la référencent — onglet de la barre d'onglets, entrée « View › Preview » du menu (stub renommé depuis `view_export`), objets du code et nommage des scripts à venir (`preview_workspace.py`, `preview_service.py`, etc.). Voir checklist §6.
2. **Lecture seule, liens internes** : aperçu en lecture seule ; liens hypertexte internes au document = ancres à scroll passif uniquement (aucun effet sur l'état de l'application). **Régénéré à chaque bascule sur la vue ET après chaque modification du modèle si la vue est déjà active** (deux déclencheurs conservés, validé TSC) ; jamais en arrière-plan.
3. **Rendu dynamique selon les filtres actifs** (Journey et/ou Agent) ; le **panneau latéral de filtres fait partie de la vue** (même version que la vue « Journeys » : `FiltersSidePanel(show_block_list=False)` dans un `SidePanelSplitter` au niveau page, TSK33).
4. La visualisation de l'aperçu et l'application des filtres **ne marquent ni la carte ni le projet comme modifiés** (RG058 + point acté).
5. **Sections restituées** (dans l'ordre) :
   a) Projet : nom du projet (`lb`)
   b) Liste des agents : liens hypertexte vers la liste des agents du projet (ancres vers g)
   c) Carte : nom de la carte narrative (`lb`)
   d) Liste des parcours : liens hypertexte vers les parcours de la carte (ancres vers e)
   e) Parcours : séquence des blocs narratifs depuis Start jusqu'à End pour le parcours courant, dans l'ordre de la séquence de lecture (RG044) — chaque bloc avec `lb`, `typ`, `content`, note en infobulle au survol ; **les agents participants sous le contenu du bloc, ligne préfixée « Participations: »** (TSK39 4.1, libellé TSK41 séance 12) ; transitions rendues en ligne ; puis **les relations ancrées sous la liste des agents, chaque ligne préfixée « Relationships: »** (TSK39 4.2, libellé TSK41 séance 12) ; plus de champs de condition (retirés du modèle, TSK39 3.2/4.3) (lb agents 1 et 2, `typ`, `content`, note en infobulle) — l'« état des relations » est ainsi restitué sous chaque bloc d'ancrage (point e), **sans section finale séparée** (validé TSC)
   f) Orphelins : blocs **sans aucune transition entrante ni sortante** (définition actée TSC), pour le parcours courant
   g) Agents : tous les agents du projet (`lb`, `typ`, `content`, note en infobulle)

## 2. Comportement avec les filtres (validé TSC séance 11)

- Périmètre de restitution : filtre Agent (RG063) ; le reste inchangé (RG047 : filtres désactivés à l'ouverture d'un projet, non persistés entre les sessions, ne marquent ni la carte ni le projet comme modifiés).
- Comportement de l'aperçu selon les filtres du panneau latéral (ou du menu Display) : oui — état des filtres possédé et partagé par MainWindow, miroirs entre toutes les vues ; changer un filtre régénère l'aperçu (2ᵉ déclencheur).
- Selon le filtre de parcours actif : filtre actif → parcours actif seul (section d : un seul lien) ; « Tous les parcours » → tous les parcours restitués (une section e par parcours, ancres d→e) ; section f restreinte aux orphelins du parcours actif.
- Filtre agent actif : blocs visibles = blocs auxquels l'agent participe ; transitions dont les deux blocs sont visibles ; relations dont le bloc d'ancrage est visible (RG063), intersection avec le parcours si les deux filtres sont actifs (RG064).
- **Rendu selon les filtres** : les éléments hors filtre sont **omis du rendu** (un document de lecture n'a pas d'état estompé/interactif comme les vues graphiques).
- **Navigation selon les ancres internes** : oui — scroll passif uniquement.
- RG048 : le filtre de parcours s'applique aux vues de la carte, y compris l'aperçu « Preview » ; jamais à la vue « Agents ».

## 3. Parcours incomplets (validé TSC séance 11)

- `JourneySequenceService.recompute_journey` (RG044) calcule la séquence en DFS depuis le bloc Start, puis ajoute les blocs rattachés mais injoignables en fin de séquence (triés par id) : aucun bloc du parcours n'est perdu.
- Rendu : flux principal = séquence DFS depuis Start ; ensuite les blocs restants du parcours (ex. une chaîne ultimement rattachée à un bloc End sans lien avec la chaîne du Start) sont restitués **regroupés par chaîne** (racine = bloc sans transition entrante dans le parcours), chaque sous-section portant un marqueur visible « branche non jointe au bloc Start ».
- Les blocs totalement isolés (aucune transition) vont dans la section f) orphelins.
- Le contrôle de cohérence des parcours (dead ends, branches non terminées, etc.) reste **post-MVP** : l'aperçu affiche, ne bloque pas.

## 4. Architecture prévue (à affiner à l'implémentation)

- Service de preview dédié, **Qt-free et read-only** (`core/services/preview_service.py` à venir) : `build_preview_html(project, narrative_map, journey=None, agent_id=None)` → sous-ensemble HTML 4 échappé, à partir de `JourneySequenceService` (ordre RG044), des attachements (`journey_node`), des transitions et de `RelationshipService` (relations par bloc d'ancrage) ; aucun appel à `set_modified`.
- UI : `PreviewWorkspace(QTextBrowser)` read-only dans `src/ui/views/preview_workspace.py` (comme la PoC : `setOpenLinks(False)`, ancres internes = scroll passif, notes en infobulle via ancres `#note-<kind>-<id>` + index + `anchorAt` + `QToolTip.showText`, thème sombre explicite), page = `SidePanelSplitter(browser, FiltersSidePanel(show_block_list=False))` au niveau page (comme Journeys).
- Intégration MainWindow : onglet « Preview » + page dans le `QStackedWidget` ; régénération à la bascule (`_on_tab_changed`) et sur signal de modification si la vue est active ; panneau latéral câblé sur les mêmes signaux que les autres vues (`journey_filter_requested`/`agent_filter_requested`).
- États vides : aucun projet ouvert (placeholder), parcours sans bloc, parcours sans Start rattaché (repli RG044), carte sans parcours.

## 5. Plan de tests (à l'implémentation)

- Tests unitaires du service : ordre RG044, filtres RG063/RG064, orphelins, branches non jointes au Start, échappement HTML, non-modification.
- Test de rendu offscreen (QTextBrowser) + tests de renommage (menu, onglet).

## 6. Checklist de renommage code (à l'implémentation)

- `menu_actions['view_export']` → `view_preview` (`main_window.py`) ; entrée menu « View › Preview » ; onglet « Preview » (`tab_bar.py`, docstring) ; futurs scripts `preview_workspace.py` / `preview_service.py`.
- « Files › Export Map... » (`export_map`, FN013) **inchangé** (grisé, post-MVP) — coexistence assumée.
- Specs mises à jour (TSK37) : SU010, FN033, `04_interface` §3/§7, `05_menu` FR/EN, RG048 + règle export fichier (`02_business_rules` FR/EN), matrice `implementation-FR/EN.md`.
