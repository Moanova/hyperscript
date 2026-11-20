# Hyperscript ::: Spécification de l'interface utilisateur

## Version du document
- **Version** : 1.0
- **Date** : 09-11-2026
- **Statut** : initial. L'application est unilingue pour l'instant (anglais).


---

## Architecture générale de l'interface

### Disposition
- **Type** : disposition verticale principale (QVBoxLayout) :
  - **Haut** : barre de menus (QMenuBar).
  - **Centre** : barre d'onglets, puis espace de travail (pages empilées : message d'accueil / vues du projet).
  - **Bas** : barre d'informations, pleine largeur, 30 px.
- **Barres latérales** : non prévues en MVP — à définir en phase de conception. *À valider.*
- **Barre de zoom** : aucune en MVP (zoom post-MVP ; entrées « Display › Zoom » grisées).

### Thème et style
- **Thème sombre conservé** (charte graphique 98 issue de planoscript) : toutes les couleurs, dimensions et polices sont lues dans `config.json` via un module de thème centralisé — **aucune valeur en dur dans le code UI**.
- Palette (valeurs par défaut de `config.json`) :
  - arrière-plans : `bg_primary` `#1E1E1E`, `bg_surface` `#2D2D2D` ; bordures `border_color` `#383838` ;
  - textes : `text_primary` `#FFFFFF`, `text_secondary` `#CCCCCC` ; survol de menu `menu_hover_bg` `#383838` ;
  - connexions : `connection_color` `#CCCCCC`, survol `connection_hover_color` `#E5C07B` (sable fixe) ; badges : `badge_bg_color` `#E5C07B`, `badge_border_color` `#F0F0F0`, `badge_text_color` `#1E1E1E` ; erreur `error_color` `#D19A66`.
  - accents (lien de la page d'accueil, survol des barres de défilement, soulignement de l'onglet actif) : `block_scene_color` `#E5C07B` (sable) ;
- Police : Segoe UI ; tailles en config (`menu_font_size_px` 12, `node_font_size_px` 13, `node_label_font_size_px` 9, `node_title_font_size_px` 14).
- Nœud (bloc) : 80×40 px (`node_default_width`/`node_default_height`), coins arrondis 6 px.
- Grille : pas mineur 20 px / majeur 80 px (`grid_minor_size`/`grid_major_size`), couleurs `#333333`/`#4A4A4A`, toujours visible, redessinée uniquement sur la zone visible.
- Vue « Agents » : points à la place de la grille, purement décoratifs — espacement `agents_view_dot_spacing_px`, rayon `agents_view_dot_radius_px`, couleur `agents_view_dot_color` ; **grille de cellules invisible** pour le positionnement des cartes à la libération du déplacement (`agents_view_cell_width`×`agents_view_cell_height`, ancrée sur l'origine de la scène) ; cartes agent `agents_view_card_width`×`agents_view_card_height` (plus grandes que les blocs 80×40, sans ports) — acté séance 04 (TSK19b), cellule invisible séance 05 (TSK21).
- **Couleurs par type de bloc narratif** (couleur de bordure du nœud) : Début `#D19A66` (or), Scène `#E5C07B` (sable), Pivot `#E06666` (rouge), Condition `#E06666` (rouge), Fin `#E5C07B` (sable) — acté séance 04 d'après les retours de tests visuels TSC (TSK16) ; Pivot et Condition partagent volontairement le même rouge, le type affiché dans le nœud les distingue.
- Vue « Relationships » (actée séance 06, révisée séance 09 TSK29) : largeur du panneau latéral droit `relationships_view_panel_width_px` ; **cellules carrées** de la matrice `relationships_view_cell_size_px` (100) ; couleur par type de relation `relationship_type_colors` (indexée sur la liste `relationship_types`) ; libellés « tous » des deux zones de filtres du panneau = `journey_list_all_label` / `agent_list_all_label`.


---

## Composants de l'interface

### 1. Barre de menus de la fenêtre d'application
- **Type** : QMenuBar native, en haut de la fenêtre, style sombre (thème).
- **Contenu et raccourcis** : spécifiés dans `docs/specification/05_menu-FR.yaml` (version EN : `05_menu-EN.yaml`). Les entrées non implémentées restent des stubs (grisées).
- **Comportement** : les menus sont désactivés lorsqu'aucun projet n'est ouvert (sauf « About ») ; « Save » est désactivé si le projet n'est pas modifié.

### 2. Barre de titre de la fenêtre
- Barre de titre native du système d'exploitation.
- Format dynamique : `Hyperscript : {libellé_projet} ({chemin_fichier})` si le projet est enregistré, `Hyperscript : {libellé_projet}` sinon ; message d'accueil (« start your new project ») quand aucun projet n'est ouvert.

### 3. Barre d'onglets (centre)
- Hauteur 40 px, style sombre. Onglets nommés en anglais, sans numérotation (application unilingue anglais, comme les entrées de menu) :
  - **Agents** — espace dédié aux agents, points d'ancrage + cartes (voir section 5, re-conçu séance 04), **actif par défaut** (ordre d'affichage inversé séance 09 TSK28 : Agents avant Journeys ; vue active par défaut passée à « Agents » séance 10, TSK30) ;
  - **Journeys** — vue principale, graphe des blocs et transitions ;
  - **Relationships** — vue matrice des relations agent-agent (voir section 6) ;
  - **Export** — aperçu de lecture in-app (voir section 7).
- La barre n'est visible que si un projet est ouvert. Les vues sont activées par la barre d'onglets ; les entrées « Project › View » du menu sont des stubs.
- **Périmètre MVP** : au minimum les onglets « Journeys » et « Export » ; « Agents » et « Relationships » selon le périmètre des vues à acter. *À valider.*
- Style des onglets : survol `#e0e0e0`-sombre équivalent (thème), onglet sélectionné en gras avec bordure inférieure visible de 2 px en `block_scene_color` (sable `#E5C07B`).

### 4. Espace de travail — vue « Journeys »
- **Type** : QGraphicsView. Graphe des blocs narratifs et de leurs transitions.
- **Panneau latéral droit** (TSK33, séance 10) : même widget partagé que la vue « Relationships » (`FiltersSidePanel`, largeur `side_panel_width_px`) — zones de filtres **Journey** et **Agent**, miroirs du menu « Display » (choisir un parcours dans le panneau **l'active** FN026 et active le filtre FN029, comme « Display > Journey », TSK30 4.1) ; **pas de liste des blocs** dans cette vue, la zone sous les filtres reste vide (la liste sert à suivre les relations, propre à « Relationships »). Les panneaux des deux vues sont synchronisés entre eux et avec le menu Display à chaque changement de filtre et à chaque CRUD de parcours/agent.
- **Grille** : toujours visible (20/80 px) ; les blocs s'alignent sur la grille à la création et à la libération des déplacements (position libre pendant le déplacement, TSK24).
- **Position par défaut à la création de la carte** : le bloc Début est placé au bord gauche de la scène plus un pas majeur de grille (80 px), centré verticalement dans un pas majeur de grille (acté séance 04, TSK16) ; sans layout sauvegardé, les autres blocs sont placés en colonne sous le bloc Début. **Création d'un bloc par l'utilisateur** (menu ou menu contextuel) : au premier emplacement libre à droite du bloc Début (une largeur de nœud + un pas majeur, puis balayage latéral RG050), ancré sur la position courante du bloc Début et aligné sur la grille (RG046) — acté séance 04 (TSK16, option B).
- **Défilement** : barres horizontale et verticale toujours visibles ; survol/actif du curseur en `block_scene_color` (sable) ; défilement automatique lorsque la souris est à moins de 50 px d'un bord ; scène initiale 4000×4000 px, étendue dynamiquement lorsque les blocs la dépassent.
- **Sélection et édition** : sélection unique (pas de sélection multiple) ; contour de sélection en tirets dans la couleur du type du bloc (`node_selection_dash_pattern`, ex. `[4.0, 4.0]` — tirets raccourcis, acté séance 04, TSK16) ; déplacement des blocs par glisser-déposer ; hit-testing des éléments graphiques par zone élargie (`shape()`) ; infobulles immédiates au survol (libellé + note des blocs, note des transitions).
- **Bloc narratif** : rectangle 80×40 px ; bordure colorée selon le type (code couleur ci-dessus) ; ports actifs entrant à gauche et sortant à droite (8 px), **sauf bloc Début (pas de port entrant) et bloc Fin (pas de port sortant), dont le port est masqué** (acté 11-11-2026, TSK14 ; la contrainte métier est déjà couverte par RG025/RG028) ; **type affiché** dans le nœud, **libellé et note en infobulle au survol** ; badge avec le nombre de participations (agents présents dans le bloc) : coin inférieur droit du nœud (2/3 du badge à l'intérieur du contour, 1/3 dehors), diamètre 16 px (`journeys_view_badge_diameter_px`), remplissage fixe `badge_bg_color`, bordure `badge_border_color`, texte `badge_text_color` ; masqué si 0 participation, « 9+ » au-delà de 9 ; ligne « Agents: … » ajoutée à l'infobulle.
- **Transition** : flèche dirigée, 2 px (couleur `connection_color`), suit les déplacements des blocs, non déplaçable en tant que telle ; survol en trait plein `connection_hover_color` (sable fixe, acté séance 04, TSK16) ; note affichée en infobulle au survol ; création par tracé temporaire du port sortant du bloc source jusqu'au port entrant du bloc cible ; la création part obligatoirement du port sortant de la source et se termine sur le port entrant de la cible (un clic à proximité du bord d'un bloc dépourvu du port requis est traité comme hors port, TSK14).
- **Filtre de parcours** : s'applique aux **vues portant sur la carte narrative** (pas à la vue « Agents ») ; désactivé par défaut à l'ouverture d'un projet ; non persisté entre les sessions. Sous filtre actif, seuls les blocs du parcours actif, les transitions dont les deux blocs y appartiennent, et les participations/relations dont le bloc d'ancrage y appartient restent à pleine opacité ; les autres éléments sont estompés (opacité 0.25) et non interactifs.
- **Filtre agent** (FN039/RG063) : « Display › Agent » (liste cochable, « All agents » en tête, cochée = filtre désactivé par défaut à l'ouverture) filtre les vues de la carte sur les blocs auxquels l'agent participe (transitions dont les deux blocs sont visibles, participations/relations dont le bloc d'ancrage est visible) ; avec le filtre de parcours actif, **intersection** (RG064) ; non persisté ; ne s'applique pas à la vue « Agents » (RG048).
- **Menus contextuels** : alignés **dynamiquement** sur le menu applicatif (mêmes actions et gestionnaires) selon la vue active et les objets graphiques sélectionnés ; le clic droit sélectionne l'élément sous le curseur avant d'ouvrir le menu, de sorte que les actions s'appliquent à l'élément cliqué ; sur la grille vide, les entrées de création portent les libellés « New Block » (sous-menu des types) et « New Transition » (acté séance 04, TSK16).

### 5. Vue « Agents » — re-conçue séance 04 (SU009, TSK19b)
- Espace de travail dédié aux agents (niveau projet), distinct du graphe des blocs : fond `bg_primary` **identique à la vue « Journeys »**, mais habillé de **points d'ancrage à la place d'une grille** (espacement/rayon/couleur en config, dessinés sur la zone visible uniquement) (RG065).
- Chaque agent du projet est représenté par une **carte** (`agents_view_card_width`×`agents_view_card_height`, plus grande qu'un bloc 80×40, **sans ports**) affichant libellé et type ; contour de la carte en `block_scene_color` (sable, retour TSC séance 04) ; note en infobulle au survol (RG054) ; **aucun badge de comptage** sur la carte — les participations et relations sont traitées dans d'autres vues (RG066).
- Les cartes sont déplaçables librement **en 2D** pendant le déplacement (aucun couloir, aucun snap en cours de drag) ; **à la libération**, la carte se positionne sur la cellule la plus proche de la grille de cellules invisible (`agents_view_cell_width`×`agents_view_cell_height`, ancrée sur l'origine de la scène ; si la cellule cible est occupée, cellule libre la plus proche) ; la cellule de dépôt doit appartenir à la boîte englobante des autres cartes élargie d'une cellule (sinon cellule libre la plus proche dans cette zone ; carte unique = libre) (RG065, TSK23). À la **création** d'un agent, la carte est placée sur la **première cellule libre en balayage ligne par ligne depuis le coin haut gauche** de la grille invisible, **décalée d'une marge égale à l'écart entre deux cartes** (cellule − carte = 40 px en x et y, calculée depuis la config — révision séance 10 TSK30, remplacée séance 10 TSK31 pour la marge, remplace TSK22) ; l'espace de travail n'est **extensible que vers la droite et vers le bas** (la scène est ancrée sur (0, 0), ses bords gauche/haut ne descendent jamais sous 0 — idem pour les déplacements de cartes, bornés par la scène). Sélection unique (RG049) ; hit-testing par `shape()` élargie (RG053) ; infobulles immédiates (RG054).
- Menu contextuel aligné sur le menu applicatif (RG055) : Edit.../Copy/Delete.../Associate with Block... pour une carte agent.
- Les filtres (parcours, agent) ne s'appliquent pas à cette vue (RG048/RG063).
- Positions des cartes persistées **au niveau projet** dans les métadonnées graphiques (fichier layout projet, distinct des layouts par carte — structure conforme au modèle métier : les agents appartiennent au projet, RG067), restaurées à la réouverture ; aucune valeur métier.

### 6. Vue « Relationships » — maquette actée séance 06 (SU012 / FN036)
- **Type** : espace de travail dédié composé d'une **matrice agent × agent** (zone centrale, scène graphique) et d'un **panneau latéral à droite** (widget partagé `FiltersSidePanel`, largeur `side_panel_width_px`, RG059 — TSK33, séance 10 ; la vue « Journeys » héberge le même panneau sans la liste des blocs, voir section 4).
- **Matrice** : une ligne et une colonne par agent du projet — **tous les agents sont affichés, même ceux qui n'ont (pas encore) aucune relation** ; matrice symétrique (relations non dirigées, RG035). **Lignes et colonnes ont chacune leur propre ordre, indépendant** (RG070 révisée séance 09) : ordre initial alphabétique sur le libellé (ex æquo par identifiant) ; déplacement d'une ligne/colonne par glisser la **carte d'en-tête** (déplacement contraint à l'axe de la ligne/colonne) ; ordres persistés au niveau projet (`relationships_view_row_order` / `relationships_view_column_order`, comme RG067) et restaurés à la réouverture. **Scène** (révision séance 09 TSK29, puis séance 10 TSK30 — rapprochement de la matrice Agent × State de planoscript, `docs/conception/04_relationships_matrix-FR.md`) : cellules **carrées** de `relationships_view_cell_size_px` (100) ; matrice **ancrée au coin haut gauche** (alignement `AlignLeft|AlignTop`, scène d'au moins 4000×4000 à l'origine, croissant uniquement vers la droite et le bas ; **barres de défilement horizontale et verticale toujours visibles et stylées comme celles de la vue « Journeys »** (`theme.WORKSPACE_STYLESHEET`) — révision séance 10 TSK31) ; **grille en fond sur toute la zone visible** (couleurs `grid_minor_color`/`grid_major_color`, lignes non interactives maintenues hors hit-testing, redessinées au défilement et au redimensionnement) ; **cellules transparentes** (pas de fond ni de bordure propre : les lignes de la matrice sont celles de la grille, TSK31) ; **point au centre de chaque cellule de tout l'espace de travail visible** (peint dans `drawBackground`, même rendu que les points d'ancrage de la vue « Agents » : `agents_view_dot_radius_px`/`agents_view_dot_color` — révision séance 10 TSK31, remplace le point limité aux cellules de la matrice) ; cartes d'en-tête au **rendu des blocs narratifs** (80×40 `node_default_width/height`, coins `node_corner_radius_px`, bordure `block_scene_color`, libellé tronqué + infobulle RG054, hit-testing `shape()` RG053), centrées dans leur cellule ; **point au centre de chaque cellule** (même rendu que les points d'ancrage de la vue « Agents » : `agents_view_dot_radius_px`/`agents_view_dot_color`).
- **Cellule (A, B)** : matérialise l'état de la paire A-B au bloc sélectionné — la relation ancrée au dernier bloc de rang inférieur ou égal au rang du bloc sélectionné (donnée dérivée, jamais stockée, SU011) ; une seule relation par (bloc, paire), donc un seul état par cellule (RG035) ; cellule vide quand la paire n'a aucun ancrage à rang inférieur ou égal. La matrice est **dynamique** : recalculée à chaque changement de bloc sélectionné. La cellule est un **objet cliquable** façon **case à cocher** (révision séance 10, TSK30, d'après la matrice Agent × State de planoscript) : contour de case centré (`relationships_view_checkbox_size`/`relationships_view_checkbox_color`), **cercle de fond plein or** (`relationships_view_check_color`) quand la paire a une relation ; le **type de la relation apparaît en infobulle au survol** (avec la note, RG054). **Clic gauche** : si aucune relation → **création directe d'une relation de type « Undefined »** (paire A-B + bloc courant, sans dialogue) ; sinon → dialogue d'**édition** de la relation existante. **Clic droit** → menu contextuel (RG055) ; cellule hors filtre estompée et non cliquable (RG048/RG063).
- **Panneau latéral (droite)** : trois zones de haut en bas — (1) filtre de parcours, (2) filtre agent, (3) **liste des blocs** ordonnés du haut vers le bas par rang minimal sur tous les parcours (ex æquo par identifiant de bloc), restreints aux blocs visibles sous les filtres actifs (intersection RG064) ; **séparateur horizontal** entre la zone des filtres et la liste des blocs — barre pleine de `relationships_view_separator_height_px` (2 px) en `grid_major_color`, bien visible (séance 10 TSK30, épaissi TSK31) ; la liste des blocs a son **ascenseur vertical toujours visible**, stylé comme ceux de la vue « Journeys » — il n'occupe que la zone liste, jamais la zone filtres ; **aucune marge résiduelle à droite du panneau** (fente du splitter calée sur la largeur du panneau, séance 10 TSK31). Les deux zones de filtres sont des miroirs du menu « Display » : mêmes actions, état toujours synchronisé (deux voies pour la même action, RG047/RG048/RG063) — choisir un parcours dans le panneau **l'active** (FN026) et active le filtre (FN029), comme « Display > Journey » (séance 10, TSK30).
- **Sélection du bloc courant** : par défaut le bloc **Start** (qui appartient à tous les parcours — règle métier actée séance 06, à implémenter en tâche dédiée avant TSK20) ; si l'utilisateur bascule sur « Relationships » depuis un bloc sélectionné dans « Journeys », ce bloc est sélectionné s'il appartient au filtre actif, sinon le Start (un élément hors filtre n'est pas sélectionnable, RG048). Cet état est visuel, de session, non persisté (RG047/RG056).
- **Filtres appliqués à la vue** : filtre de parcours (RG048) — les relations dont le bloc d'ancrage est hors filtre sont estompées (opacité de configuration) et non interactives ; filtre agent (RG063) — tous les agents restent affichés, les agents non concernés sont estompés (même opacité) et la création d'une relation les concernant est interdite.
- **Sélection et menus** : sélection unique (RG049) ; le clic sur une cellule ouvre le menu contextuel aligné sur le menu applicatif (`Project › Relationships` : New.../Edit.../Delete..., RG055) ; « Voir dans la vue Journeys » bascule vers « Journeys » avec le focus sur le bloc d'ancrage (FN032, état visuel temporaire RG056) ; note de la relation en infobulle au survol (RG054).
- **Périmètre MVP** : la vue « Relationships » (matrice + panneau latéral) fait partie du MVP.

### 7. Vue « Export » (aperçu in-app)
- Espace de travail « Export » : aperçu de lecture de la carte narrative courante, **en lecture seule** (liens inertes, aucune interaction sur le contenu).
- Régénéré à chaque bascule sur l'onglet « Export », et après chaque modification du modèle lorsque l'onglet est déjà actif ; jamais en arrière-plan.
- Dynamique selon le filtre de parcours (filtre actif → parcours actif seul ; « Tous les parcours » → tous les parcours).
- Contenu restitué : blocs depuis le bloc Début dans l'ordre de la séquence de lecture, transitions rendues en ligne, conditions rendues sur leur branche, relations entre agents listées sous leur bloc d'ancrage, section finale « état des relations » ; libellé en titre, contenu en corps de texte (libellé seul si vide), note en infobulle au survol.
- Fait partie du **MVP minimal** ; pourra être renommée ultérieurement. *Détail à finaliser après la phase de conception* (SU010).
- La visualisation de l'aperçu ne marque ni la carte ni le projet comme modifiés.

### 8. Barre d'informations (bas)
- Pleine largeur, hauteur 30 px, style sombre (arrière-plan de surface, bordure supérieure).
- Affiche un message contextuel selon l'objet sélectionné (bloc, transition, participation, relation, agent) ; vide si rien n'est sélectionné. Les messages de la barre d'info ne marquent pas le projet comme modifié.

### 9. Message d'accueil
- Affiché dans le centre tant qu'aucun projet n'est ouvert (la barre d'onglets est masquée).
- Texte centré, padding 40 px, thème sombre : titre + paragraphe avec un lien « créer un nouveau projet » en `block_scene_color` (sable) déclenchant la création d'un projet.


---

## Zoom
- Hors MVP : les entrées « Display › Zoom » (In/Out/Reset, Ctrl+= / Ctrl+- / Ctrl+0) restent grisées ; aucune barre de zoom. Le zoom sera ajouté après le MVP (à définir en phase de conception).


---

## Points ouverts à valider en phase de conception
1. Formes/icônes des 5 types de blocs narratifs et des transitions — code couleur acté séance 04 d'après les retours de tests visuels (TSK16, voir « Thème et style »).
2. Badges : nombre de participations en vue « Journeys » — acté séance 03 (voir section 4) ; compteurs de transitions entrantes/sortantes en vue « Agents » (à re-concevoir).
3. Maquette de la vue « Relationships » — **actée séance 06** (voir section 6).
4. Contenu de la vue « Agents » (re-conception).
5. Barres latérales (intégration ou non).
6. Zoom (post-MVP).
7. Périmètre MVP des vues au-delà du minimum « Journeys » + « Export ».
