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
  - connexions : `connection_color` `#CCCCCC` ; badges : `badge_bg_color` `#E5C07B`, `badge_border_color` `#F0F0F0`, `badge_text_color` `#1E1E1E` ; erreur `error_color` `#D19A66`.
- Police : Segoe UI ; tailles en config (`menu_font_size_px` 12, `node_font_size_px` 13, `node_label_font_size_px` 9, `node_title_font_size_px` 14).
- Nœud (bloc) : 80×40 px (`node_default_width`/`node_default_height`), coins arrondis 6 px.
- Grille : pas mineur 20 px / majeur 80 px (`grid_minor_size`/`grid_major_size`), couleurs `#333333`/`#4A4A4A`, toujours visible, redessinée uniquement sur la zone visible.
- **Couleurs par type de bloc narratif** (Début, Scène, Pivot, Condition, Fin) : *À valider en phase de conception* (plano : état `#E5C07B`, événement `#D19A66`).


---

## Composants de l'interface

### 1. Barre de menus de la fenêtre d'application
- **Type** : QMenuBar native, en haut de la fenêtre, style sombre (thème).
- **Contenu et raccourcis** : spécifiés dans `docs/specification/05_menu-FR.yaml` (version EN : `05_menu-EN.yaml`). Les entrées non implémentées restent des stubs (grisées).
- **Comportement** : les menus sont désactivés lorsqu'aucun projet n'est ouvert (sauf « À propos ») ; « Enregistrer » est désactivé si le projet n'est pas modifié.

### 2. Barre de titre de la fenêtre
- Barre de titre native du système d'exploitation.
- Format dynamique : `Hyperscript : {libellé_projet} ({chemin_fichier})` si le projet est enregistré, `Hyperscript : {libellé_projet}` sinon ; message d'accueil (« start your new project ») quand aucun projet n'est ouvert.

### 3. Barre d'onglets (centre)
- Hauteur 40 px, style sombre. Onglets nommés, sans numérotation :
  - **Parcours** — actif par défaut (vue principale, graphe des blocs et transitions) ;
  - **Agents** — vue matrice (voir section 5) ;
  - **Relations** — vue graphe des relations agent-agent (voir section 6) ;
  - **Export** — aperçu de lecture in-app (voir section 7).
- La barre n'est visible que si un projet est ouvert. Les vues sont activées par la barre d'onglets ; les entrées « Project › View » du menu sont des stubs.
- **Périmètre MVP** : au minimum les onglets « Parcours » et « Export » ; « Agents » et « Relations » selon le périmètre des vues à acter. *À valider.*
- Style des onglets : survol `#e0e0e0`-sombre équivalent (thème), onglet sélectionné en gras avec bordure inférieure visible.

### 4. Espace de travail — vue « Parcours »
- **Type** : QGraphicsView. Graphe des blocs narratifs et de leurs transitions.
- **Grille** : toujours visible (20/80 px) ; les blocs s'aimantent sur la grille à la création et lors des déplacements.
- **Défilement** : barres horizontale et verticale toujours visibles ; défilement automatique lorsque la souris est à moins de 50 px d'un bord ; scène initiale 4000×4000 px, étendue dynamiquement lorsque les blocs la dépassent.
- **Sélection et édition** : sélection unique (pas de sélection multiple) ; déplacement des blocs par glisser-déposer ; hit-testing des éléments graphiques par zone élargie (`shape()`) ; infobulles immédiates au survol (note des blocs et des transitions).
- **Bloc narratif** : rectangle 80×40 px ; rendu visuel distinct par type — *À valider en conception* ; deux ports actifs (entrant à gauche, sortant à droite, 8 px) ; badge avec le nombre de participations (agents présents dans le bloc) — *position/détail à valider* ; libellé affiché, note en infobulle au survol.
- **Transition** : flèche dirigée, 2 px (couleur `connection_color`), suit les déplacements des blocs, non déplaçable en tant que telle ; note affichée en infobulle au survol ; création par tracé temporaire du port sortant du bloc source jusqu'au port entrant du bloc cible.
- **Filtre de parcours** : s'applique à **toutes les vues** ; désactivé par défaut à l'ouverture d'un projet ; non persisté entre les sessions. Sous filtre actif, seuls les blocs du parcours actif, les transitions dont les deux blocs y appartiennent, et les participations/relations dont le bloc d'ancrage y appartient restent à pleine opacité ; les autres éléments sont estompés (opacité 0.25) et non interactifs.
- **Menus contextuels** : alignés **dynamiquement** sur le menu applicatif selon la vue active et les objets graphiques sélectionnés ; le clic droit sélectionne l'élément sous le curseur avant d'ouvrir le menu, de sorte que les actions s'appliquent à l'élément cliqué.

### 5. Vue « Agents »
- *Spécification laissée vide pour le moment — travail de re-conception à venir* (SU009 initialisé, à finaliser après la phase de conception).

### 6. Vue « Relations »
- *Spécification laissée vide pour le moment — la maquette sera définie durant la phase de conception* (SU012 / FN036). Rappel du besoin : graphe des agents, arcs étiquetés par type, annotés des blocs d'ancrage, navigation croisée vers le bloc d'ancrage dans la vue « Parcours ».

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
- Texte centré, padding 40 px, thème sombre : titre + paragraphe avec un lien « créer un nouveau projet » déclenchant la création d'un projet.


---

## Zoom
- Hors MVP : les entrées « Display › Zoom » (avant/arrière/réinitialiser, Ctrl+= / Ctrl+- / Ctrl+0) restent grisées ; aucune barre de zoom. Le zoom sera ajouté après le MVP (à définir en phase de conception).


---

## Points ouverts à valider en phase de conception
1. Style visuel des 5 types de blocs narratifs (formes/couleurs/icônes) et des transitions.
2. Badges : nombre de participations en vue « Parcours » ; compteurs de transitions entrantes/sortantes en vue « Agents » (à re-concevoir).
3. Maquette de la vue « Relations ».
4. Contenu de la vue « Agents » (re-conception).
5. Barres latérales (intégration ou non).
6. Zoom (post-MVP).
7. Périmètre MVP des vues au-delà du minimum « Parcours » + « Export ».
