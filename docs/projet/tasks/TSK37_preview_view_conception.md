# TSK37 — Conception de la vue « Preview » (ex-« Export ») — SU010 / FN033

- **Statut** : Review (23-11-2026, séance 11 — conception rédigée, à valider TSC) ; dépend de #TSK33 (Done).
- **Origine** : séance 11 — étude de la vue Export côté Hyperscript (spécifiée mais non implémentée : onglet « Export » prévu en `04_interface` §3/§7, `view_export` stub, `export_map` grisé) comparée à la PoC planoscript (TSK31/TSK33 plano : aperçu in-app livré dans un 3ᵉ onglet `ExportWorkspace(QTextBrowser)` + `ExportService.build_reading_text`, export fichier FN013 non implémenté des deux côtés).
- **Périmètre de la tâche** : conception uniquement — mise à jour de **SU010**, **FN033**, `04_interface` §3 (onglet) et §7 (vue), `05_menu` (View › Export → Preview), RG048 (mention « aperçu Export » → « Preview »), matrice d'implémentation `docs/projet/implementation-FR/EN.md`, checklist de renommage côté code (prévue pour l'implémentation : `menu_actions['view_export']` → `view_preview`, docstring `tab_bar.py`, futurs scripts `preview_workspace.py` / service `preview_service.py`, etc.). **SU007 / FN013 (export sur fichier HTML, « Files › Export Map... » grisé) sont HORS périmètre** — restent post-MVP inchangés.

## Décisions actées TSC (séance 11, 23-11-2026)

1. **Renommage Export → Preview** : la vue elle-même et tous les éléments qui la référencent (menu View, objets créés dans le code, nommage des scripts s'il y a lieu).
2. **Aperçu en lecture seule**, liens hypertexte internes au document ; **régénéré à chaque bascule** sur la vue Preview.
3. **Rendu dynamique selon les filtres activés** (Journey et/ou Agent) ; le **panneau latéral de filtres fait partie de la vue** (même version que la vue Journeys — `FiltersSidePanel(show_block_list=False)`).
4. La visualisation de l'aperçu et l'application des filtres **ne marquent ni la carte ni le projet comme modifiés**.
5. **Organisation des sections** :
   a) Projet : nom du projet (`lb`)
   b) Liste des agents : liens hypertexte vers la liste des agents du projet
   c) Carte : nom de la carte narrative (`lb`)
   d) Liste des parcours : liens hypertexte vers la liste des parcours de la carte
   e) Parcours : séquence des blocs narratifs depuis Start jusqu'à End pour le parcours courant (`lb`, `typ`, `content`, note en infobulle) ; relations entre agents ancrées sur leurs blocs respectifs (`lb` agents 1 et 2, `typ`, `content`, note en infobulle)
   f) Orphelins : liste des blocs orphelins pour le parcours courant (`lb`, `typ`, `content`, note en infobulle)
   g) Agents : tous les agents du projet (`lb`, `typ`, `content`, note en infobulle)

## Évaluation de cohérence (faite en séance 11)

- **Modèle de données** : tous les champs cités existent (`Project.lb`, `NarrativeMap.lb`, `Agent.lb/typ/content/note`, `Journey.lb`, `Block.lb/typ/content/note`, `Relationship.agent_1_id/agent_2_id/block_id/typ/content/note`) → point 5 cohérent tel quel.
- **Point 3 (filtres + panneau)** : cohérent — RG048/RG063/RG064 incluent déjà l'aperçu dans le périmètre des filtres (hors vue « Agents ») ; `FiltersSidePanel` existe (TSK33) et ne touche jamais au modèle (RG058) ; état des filtres session-only (RG047), possédé par MainWindow et partagé entre vues.
- **Point 4** : cohérent — RG058 (l'UI n'écrit jamais le modèle) + règle « l'export/l'aperçu ne marque pas modifié » ; le panneau de filtres émet seulement des signaux.
- **Point 2 — VALIDÉ TSC 23-11-2026** : les **deux déclencheurs sont conservés** — régénération à chaque bascule sur la vue Preview **et** après chaque modification du modèle quand la vue est déjà active (cohérent avec `04_interface` §7 actuelle et la décision plano TSK31).
- **Point 1 — VALIDÉ TSC 23-11-2026** : l'export fichier garde le nom « Export Map » (FN013, hors périmètre, grisé) ; la **coexistence Preview (vue in-app) / Export Map (fichier, post-MVP) est assumée dans les spécifications**.
- **Point 5 — définition actée TSC 23-11-2026 pour les orphelins** : un bloc orphelin est un bloc **sans aucune transition entrante ni sortante** (non encore rattaché à un autre bloc) — et non « non rattaché au parcours ». Section f) = orphelins du parcours courant (blocs orphelins rattachés au parcours actif ; avec « Tous les parcours » → tous les blocs orphelins). Restent à finaliser en conception : « parcours courant » avec filtre « Tous les parcours » → restituer tous les parcours (chaque section e) ancrée, liens de d) ; ancres internes b)→g) et d)→e).

## Comportement de la vue avec les filtres (VALIDÉ TSC 23-11-2026)

Validé : périmètre de restitution = filtre Agent (RG063) ; le reste (filtres off à l'ouverture, non persistés, ne marquent rien modifié) inchangé par rapport à l'existant (RG047). Comportement de l'aperçu selon les filtres du panneau latéral (ou du menu Display) : oui. Selon le filtre de parcours actif : oui. Rendu selon les filtres (omission des blocs filtrés) : oui. Navigation selon les ancres internes : oui.

Points détaillés à spécifier :

- **Périmètre** : RG048 (filtre de parcours s'applique aux vues de la carte, y compris l'aperçu Preview ; pas à la vue « Agents »), RG063 (filtre agent : blocs auxquels l'agent participe, transitions dont les deux blocs sont visibles, relations/participations dont le bloc d'ancrage est visible), RG064 (intersection si les deux filtres sont actifs), RG047 (filtres off par défaut à l'ouverture, session-only, non persistés, ne marquent rien comme modifié).
- **Panneau latéral dans la vue** : même `FiltersSidePanel(show_block_list=False)` que Journeys ; combos = miroirs du menu Display et des autres vues (état possédé par MainWindow, partagé) ; changer un filtre depuis le panneau régénère l'aperçu (2ᵉ déclencheur) sans marquer modifié.
- **Filtre de parcours actif** : sections d)/e)/f) restreintes au parcours actif (d) n'affiche que le lien du parcours actif, comme la PoC) ; relations affichées sous leur bloc d'ancrage seulement si ce bloc est visible sous les filtres.
- **« Tous les parcours »** : tous les parcours restitués (une section e) par parcours, ancres d) → e)) ; f) = tous les blocs orphelins.
- **Filtre agent actif** : blocs visibles = blocs auxquels l'agent participe ; transitions dont les deux blocs sont visibles ; relations dont le bloc d'ancrage est visible (RG063), intersection avec le parcours si filtre actif (RG064). Dans l'aperçu **en lecture seule**, décider : les éléments hors filtre sont **omis du flux rendu** (proposé, car un document de lecture n'a pas d'état estompé/interactif comme les vues graphiques ; alternative : les restituer estompés) ; les blocs orphelins (sans transition ni relation) ne sont pas concernés par le filtre agent.
- Liens internes (ancres b)→g), d)→e)) : scroll passif uniquement, jamais d'effet sur l'état de l'application (lecture seule).

## Parcours incomplets (proposition VALIDÉE TSC 23-11-2026)

Contexte : `JourneySequenceService.recompute_journey` (RG044) calcule déjà la séquence en DFS depuis le bloc Start, puis **les blocs rattachés mais injoignables sont ajoutés en fin de séquence, triés par id** — aucun bloc du parcours n'est jamais perdu. Proposition pour l'aperçu :
- flux principal = séquence DFS depuis Start (ordre RG044) ;
- les blocs du parcours restants (injoignables depuis Start, ex. votre cas d'une chaîne ultimement rattachée à un bloc End sans lien avec la chaîne du Start) sont restitués **après le flux principal, regroupés par chaîne** (racine = bloc sans transition entrante dans le parcours), chaque sous-section portant un marqueur visible « branche non jointe au bloc Start » — l'incomplétude est visible sans rien cacher ;
- les blocs totalement isolés (aucune transition) vont dans la section f) orphelins (définition actée ci-dessus) ;
- le **contrôle de cohérence** des parcours (dead ends, branches non terminées, etc.) reste **post-MVP** (inchangé) : l'aperçu affiche, ne bloque pas.

## Éléments restants à compléter en conception

- **Widget et format de rendu** : `QTextBrowser` read-only + sous-ensemble HTML 4 (comme la PoC) ; échappement du contenu utilisateur ; thème sombre (fond explicite `bg_primary`, car le stylesheet global éclaire le texte) ; couleur des liens (`link_color`) ; police.
- **Notes en infobulle** : mécanisme (PoC : ancres `#note-<kind>-<id>` + index des notes + `anchorAt` + `QToolTip.showText`, car `QTextBrowser` ignore les titres d'ancre).
- **Rendu des transitions** « en ligne » (§7 actuel) : préciser le rendu entre blocs prédécesseur/successeur (flèche/ligne + note de la transition en infobulle si présente).
- **Rendu des conditions** « sur leur branche » (§7 actuel) : affichage du `condition` du bloc Condition sur la branche concernée.
- **Schéma d'ancres internes** : nommage (`#journey-<id>`, `#agent-<id>`, éventuellement `#block-<id>`) ; liens de b) vers g) et de d) vers e) ; scroll passif uniquement.
- **Section finale « état des relations »** : **résolu TSC 23-11-2026** — l'état des relations est restitué **dans le point e)** : chaque bloc narratif affiche son contenu (avec ses autres attributs), puis les relations ancrées sur ce bloc s'il y en a ; il n'y a **pas de section finale séparée**.
- **États vides** : aucun projet ouvert (placeholder), parcours sans bloc, parcours sans Start rattaché (repli RG044 : blocs injoignables seuls), carte sans parcours.
- **Câblage des déclencheurs** : régénération à la bascule sur l'onglet + sur signal de modification du modèle si la vue est active (mécanisme de signal existant, ex. `workspace_modified` côté MainWindow).
- **Architecture de la page** : `SidePanelSplitter(browser_preview, FiltersSidePanel(show_block_list=False))` au niveau page (comme Journeys, TSK33) ; état des filtres possédé/partagé par MainWindow, miroirs du menu Display et des autres vues.
- **Non-modification** : service de preview purement read-only (Qt-free), aucun signal de modification émis (RG058 + point 4 acté).
- **Plan de tests** : tests unitaires du service (ordre RG044, filtres RG063/RG064, orphelins, branches non jointes au Start, échappement HTML, non-modification) + test de rendu offscreen + tests de renommage.
- **Checklist de renommage code** (implémentation) : `menu_actions['view_export']` → `view_preview`, onglet `Preview`, docstring `tab_bar.py`, futurs scripts `preview_workspace.py` / `preview_service.py`, etc.

## Plan (conception) — exécuté le 23-11-2026 (séance 11)

1. `01_user_stories` FR/EN : SU010 réécrit (vue « Preview », lecture seule, liens internes, régénération, filtres, non-modification, sections a–g).
2. `03_features` FR/EN : FN033 mis à jour (idem) ; FN013/SU007 inchangés (post-MVP).
3. `04_interface` FR/EN : §3 onglet « Preview » (remplace « Export ») ; §7 réécrit « Vue Preview » avec les sections a–g, le panneau latéral de filtres, la régénération, RG047/RG048 ; périmètre MVP.
4. `05_menu` FR/EN : View › Export → View › Preview (stub renommé) ; Files › Export Map... inchangé (grisé).
5. `02_business_rules` FR/EN : RG048 « aperçu Export » → « aperçu Preview ».
6. Matrice `docs/projet/implementation-FR/EN.md` : statuts SU010/FN033 → `not-started` (conception faite, code à venir) avec références.
7. Checklist de renommage code pour la future implémentation (objets `view_export`, docstring `tab_bar.py`, etc.).

## Journal

- 2026-11-23 (compléments TSC séance 11) : **validé** — les deux déclencheurs de régénération conservés (bascule sur la vue + modification du modèle si vue active) ; nom « Export Map » conservé pour l'export fichier, coexistence Preview/Export Map assumée dans les specs. **Définition actée des orphelins** : bloc sans aucune transition entrante ni sortante. **Comportement avec les filtres** : points à spécifier consignés (RG047/RG048/RG063/RG064, panneau latéral miroir, parcours actif vs Tous, omission des éléments hors filtre proposée, ancres passives). **Parcours incomplets** : proposition consignée (flux DFS depuis Start puis sous-sections marquées des blocs injoignables, regroupés par chaîne ; orphelins isolés en section f) ; contrôle de cohérence reste post-MVP. À valider en conception.
- 2026-11-23 (validations TSC séance 11) : filtres (périmètre RG063, comportement panneau/menu et parcours actif, omission des blocs filtrés, ancres internes) et gestion des parcours incomplets **validés** ; liste des éléments restants à compléter en conception ajoutée (widget/format, infobulles de notes, transitions/conditions, ancres, états vides, section « état des relations » à trancher, câblage, tests, renommage).
- 2026-11-23 (conception rédigée) : SU010 et FN033 réécrits (FR/EN), `04_interface` §3/§7 (onglet et vue « Preview »), `05_menu` FR/EN (View › Preview, coexistence « Export Map » notée), `02_business_rules` FR/EN (RG048 + règle export fichier), matrice `implementation-FR/EN.md`, note de conception `docs/conception/05_preview-FR/EN.md`. Point ouvert résolu : état des relations = dans le point e) (relations sous chaque bloc d'ancrage, pas de section finale). YAML des menus revalidé. Passée en **Review** (à valider TSC). Pas de commit/push (non demandé).
- 2026-11-23 : TSK37 créée et passée en Doing (séance 11) ; fiche initialisée avec les 7 points actés TSC, le périmètre (SU010/FN033 uniquement) et l'évaluation de cohérence (2 remarques : régénération après modification si vue active à confirmer ; coexistence Preview / « Export Map »). Étude comparative planoscript consignée (aperçu seul livré dans la PoC ; export fichier non fait des deux côtés). AGENTS.md corrigé (paragraphe d'aperçu hérité plano). Travail de rédaction des specs à lancer sur feu vert.
