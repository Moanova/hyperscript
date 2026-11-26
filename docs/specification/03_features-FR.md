# Hyperscript ::: Fonctionnalités

## Document Version
- **Version** : 1.0
- **Date** : 09-11-2026
- **Statut** : initial.


---

## Rappel du périmètre MVP
- Un projet ne contient qu'une seule carte narrative (le modèle de données prévoit plusieurs cartes).
- Seuls le renommage de la carte par défaut, la modification de son contenu et son export de lecture sont fonctionnels.
- Les barres d'outils ne sont pas implémentées : les actions correspondantes sont exclusivement accessibles par le menu.
- Le périmètre des vues n'est pas acté au-delà du minimum : vue « Parcours » et vue « Preview ».
- L'application n'analyse pas la cohérence des parcours (fonctionnalité hors MVP).
- L'application cible exclusivement les PC sous Windows.
- Le zoom et les fonctions d'édition (annuler/rétablir) sont à définir en phase de conception.
- Le périmètre exact de l'export de lecture sera précisé ultérieurement.
- Aucune migration des projets planoscript existants.


---

# Application

## FN001 : Lancer l'application
- **Description** : Lancer l'application.
- **Références** : SU001 (accueil) ; écran d'accueil décrit dans `04_interface` (§9).
- **Comportement attendu** :
    - Au lancement, l'application affiche un écran d'accueil permettant notamment de créer un nouveau projet.
    - Une seule instance de l'application peut tourner à la fois : si une instance est déjà en cours, un nouveau lancement se termine silencieusement (garde single-instance).

## FN002 : Quitter l'application
- **Description** : Quitter l'application.
- **Références** : SU001 ; menu « Files › Quit » (Ctrl+Q).
- **Comportement attendu** :
    - Si le projet courant est modifié, l'application propose « Enregistrer », « Ne pas enregistrer », « Annuler » avant de quitter.
    - L'annulation conserve le projet ouvert et l'application en cours d'exécution.

## FN003 : Afficher l'historique des changements
- **Description** : Afficher l'historique des changements de chaque version de l'application.
- **Références** : menu « About › Change Log ».
- **Comportement attendu** :
    - Une boîte de dialogue présente la liste des versions et les changements associés.

## FN004 : Afficher l'information « à propos »
- **Description** : Afficher le message d'information « à propos » de l'application.
- **Références** : menu « About › About Hyperscript ».
- **Comportement attendu** :
    - Une boîte de dialogue présente les informations générales de l'application.


---

# Projet

## FN005 : Créer un nouveau projet
- **Description** : Créer un nouveau projet narratif.
- **Références** : SU001 ; menu « Files › New Project... » (Ctrl+N) ; écran d'accueil.
- **Comportement attendu** :
    - Le projet peut être créé depuis le menu, le raccourci clavier ou l'écran d'accueil.
    - Le nouveau projet est un projet non enregistré : il réside en mémoire et n'est associé à aucun fichier tant que l'utilisateur ne l'enregistre pas.
    - Il est nommé « Nouveau projet » et contient une carte narrative nommée « Carte narrative principale ».
    - Un seul projet peut être ouvert à la fois ; la création d'un nouveau projet remplace le projet courant (avec confirmation de sauvegarde si modifié).
    - Le projet possède un identifiant stable, un nom, une date de création, une date de dernière modification ; le chemin du fichier est un état applicatif, non une donnée métier.

## FN006 : Ouvrir un projet
- **Description** : Ouvrir un projet depuis le système de fichiers.
- **Références** : SU001 ; menu « Files › Open... » (Ctrl+O).
- **Comportement attendu** :
    - L'utilisateur choisit un fichier de projet valide sur le système de fichiers.
    - En cas de fichier invalide, incompatible ou illisible, l'application affiche un message d'erreur clair et conserve le projet courant inchangé.
    - Si le projet courant est modifié, une confirmation de sauvegarde est proposée avant l'ouverture.

## FN007 : Ouvrir un projet récent
- **Description** : Ouvrir un projet depuis la liste des projets récents.
- **Références** : SU001 ; menu « Files › Recent Projects ».
- **Comportement attendu** :
    - Le menu présente une liste dynamique des projets précédemment enregistrés ou ouverts.
    - La liste respecte la limite configurée de projets récents.
    - Les fichiers n'existant plus sont retirés de la liste.
    - Le même traitement des fichiers invalides et des confirmations de sauvegarde que FN006 s'applique.
- **Périmètre MVP** :
    - Entrée « Files › Recent Projects » grisée en MVP (fonctionnalité hors MVP).

## FN008 : Enregistrer le projet
- **Description** : Enregistrer le projet.
- **Références** : SU001 ; menu « Files › Save » (Ctrl+S).
- **Comportement attendu** :
    - Si le projet est déjà associé à un fichier, l'enregistrement s'effectue sans nouvelle boîte de dialogue.
    - Si le projet n'a jamais été enregistré, l'application demande un nom et un emplacement (comportement équivalent à FN009).
    - L'action est désactivée tant que le projet n'est pas modifié.
    - L'enregistrement ajoute le projet à la liste des projets récents.

## FN009 : Enregistrer le projet sous...
- **Description** : Enregistrer le projet sous un autre nom ou dans un autre emplacement.
- **Références** : SU001 ; menu « Files › Save as... » (Ctrl+Shift+S).
- **Comportement attendu** :
    - L'utilisateur choisit un nom et un emplacement.
    - La copie enregistrée devient le projet courant.
    - L'action ajoute le projet à la liste des projets récents.

## FN010 : Fermer le projet
- **Description** : Fermer le projet courant.
- **Références** : SU001 ; menu « Files › Close » (Ctrl+W).
- **Comportement attendu** :
    - Si le projet est modifié, l'application propose « Enregistrer », « Ne pas enregistrer », « Annuler ».
    - Après fermeture, aucun projet n'est ouvert (retour à l'écran d'accueil).

## FN011 : Modifier le libellé du projet
- **Description** : Modifier le libellé (nom) du projet courant.
- **Références** : SU001. **Hors menu** : aucune option de menu dédiée.
- **Comportement attendu** :
    - Le libellé du projet est un attribut métier modifiable via une fenêtre d'édition du projet (spécification de cette fenêtre à venir).
    - Toute modification du libellé met à jour la date de dernière modification et marque le projet comme modifié.
    - Le libellé n'est pas contraint à l'unicité.


---

# Carte narrative

## FN012 : Renommer la carte narrative
- **Description** : Renommer la carte narrative du projet.
- **Références** : SU002 (périmètre MVP : seul le renommage de la carte par défaut est disponible).
- **Comportement attendu** :
    - Le renommage s'effectue par édition directe du libellé ou via une boîte de dialogue d'édition.
    - Tout renommage marque la carte, et donc le projet, comme modifié, et met à jour les dates de dernière modification.

## FN013 : Exporter la carte narrative en document de lecture
- **Description** : Exporter la carte narrative courante en document autonome de lecture (HTML), consultable dans un navigateur standard.
- **Références** : SU002 (échange de carte, post-MVP), SU007 ; menu « Files › Export Project... » (TSK42, séance 12) ; « Files › Export Map... » reste grisée.
- **Comportement attendu** :
    - L'export est lancé depuis le menu « Files » (pas de barre d'outils en MVP).
    - L'export génère un dossier nommé d'après le projet, dans le dossier parent choisi par l'utilisateur, contenant `index.html` (liens vers chaque page de parcours et vers la page des agents) et toutes les pages nécessaires à la navigation hypertexte : une page par parcours (`journey-<id>.html`), une page des agents (`agents.html`), une feuille de style partagée (`style.css`, référencée en relatif) (TSK42, séance 12).
    - Le document est autonome : aucun serveur, aucune connexion Internet, aucune dépendance externe ; il s'affiche correctement dans Chrome, Firefox et Edge.
    - La page d'accueil propose le choix du mode de lecture ; seul le mode « par parcours » est disponible en MVP.
    - En mode « par parcours » : une page intermédiaire liste les parcours de la carte ; le choix d'un parcours affiche la séquence linéaire complète de ses blocs.
    - Chaque bloc est rendu par son libellé (titre de paragraphe) et son contenu (corps du texte) ; si le contenu est vide, seul le libellé est affiché. Les transitions sont rendues en ligne ; **les agents participants sous le contenu, ligne préfixée « Participations: »** ; **les relations entre agents listées sous leur bloc d'ancrage, chaque ligne préfixée « Relationships: »** (TSK39 4.1/4.2, libellés TSK41).
    - L'ordre de lecture est la séquence de lecture du parcours (calculée depuis le bloc Début), indépendamment des positions graphiques.
    - Chaque page de lecture offre un lien de retour vers le sommaire.
    - L'export ne marque ni la carte ni le projet comme modifiés.
- **Note** : export réalisé via l'entrée « Files › Export Project... » (TSK42, séance 12) ; « Files › Export Map... » et « Files › Import Map... » restent grisées jusqu'à nouvel ordre (échange de carte/agents entre projets en JSON = post-MVP).


---

# Blocs narratifs

## FN014 : Créer un bloc narratif
- **Description** : Créer un bloc narratif dans la carte narrative. Le type — Début, Scène, Pivot, Condition ou Fin — est choisi à la création et immuable ensuite.
- **Références** : SU003 ; menu « Project › Blocks › New » (choix du type).
- **Comportement attendu** :
    - En MVP, la création s'effectue exclusivement depuis le menu (pas de barre d'outils).
    - Le bloc est créé avec un identifiant unique dans la carte, le libellé par défaut de son type, et le rendu visuel correspondant à son type.
    - En MVP (création depuis le menu), il est positionné automatiquement au premier emplacement libre de la **zone visible courante** (suit les barres de défilement), aligné sur la grille d'alignement (toujours visible et active) — révisé séance 12 (TSK39 3.3) ; repli au premier emplacement libre à droite du bloc Début (ancré sur sa position courante, TSK16 option B) si la zone visible est pleine. La création depuis une autre vue bascule d'abord vers la vue « Journeys » (TSK39 1.4).
    - Il présente deux ports d'attachement actifs : entrant (gauche) et sortant (droite).
    - Il n'est pas redimensionnable.
    - Aucun bloc orphelin : le bloc nouvellement créé est rattaché au parcours actif si le filtre de parcours est activé, au parcours par défaut sinon.
    - Le bloc Début est unique : il est créé automatiquement à la création de la carte narrative et ne peut pas être créé manuellement ni dupliqué.
    - Toute création marque la carte, et donc le projet, comme modifié.

## FN015 : Modifier les attributs d'un bloc
- **Description** : Modifier les attributs éditables d'un bloc via un dialogue d'édition.
- **Références** : SU003 ; menu « Project › Blocks › Edit... ».
- **Comportement attendu** :
    - Le dialogue d'édition présente les attributs éditables : libellé, note (annotation) et contenu narratif. Le type n'est pas modifiable.
    - Le dialogue présente en outre la liste « Agents » du projet avec les participants actuels cochés — même principe que le rattachement aux parcours (TSK39 séance 12, 3.1).
    - Les champs de condition structurée (nature / référence Artefact / libellé, ex-FN035) ont été **retirés du modèle** séance 12 (TSK39 3.2) : un bloc Condition ne porte plus que libellé, note et contenu.
    - Le libellé n'est pas contraint à l'unicité au sein de la carte.
    - Toute modification d'attribut marque la carte, et donc le projet, comme modifié.

## FN016 : Dupliquer un bloc
- **Description** : Dupliquer un bloc existant.
- **Références** : SU003.
- **Comportement attendu** :
    - La copie porte un nom distinct (« {libellé} (copie) ») et un nouvel identifiant.
    - La copie est rattachée au parcours actif.
    - Le bloc Début n'est pas duplicable.
    - Toute duplication marque la carte, et donc le projet, comme modifié.

## FN017 : Déplacer un bloc
- **Description** : Positionner ou repositionner un bloc dans l'espace de travail (visualisation).
- **Références** : SU003, SU006.
- **Comportement attendu** :
    - Le déplacement s'effectue par glisser-déposer à la souris (PC), au stylet ou en mode tactile (tablette).
    - Pendant le déplacement, la position du bloc est libre ; à la libération, il s'aligne sur la grille (RG046).
    - La position (x, y) est conservée entre les sessions via le fichier de métadonnées graphiques associé au projet.
    - Le bloc n'est pas redimensionnable.
    - Tout déplacement marque la carte, et donc le projet, comme modifié.

## FN018 : Supprimer un bloc
- **Description** : Supprimer un bloc de la carte narrative.
- **Références** : SU003 ; menu « Project › Blocks › Delete... ».
- **Comportement attendu** :
    - Si des données sont associées au bloc, une confirmation est demandée.
    - La suppression entraîne la suppression en cascade de ses transitions, de ses participations, de ses relations ancrées et de ses rattachements aux parcours.
    - Toute suppression marque la carte, et donc le projet, comme modifié.

## FN019 : Gérer le rattachement d'un bloc aux parcours
- **Description** : Modifier la liste des parcours auxquels un bloc est rattaché.
- **Références** : SU003, SU005.
- **Comportement attendu** :
    - Le rattachement est géré via une liste à choix multiples des parcours, présentée dans le dialogue d'édition du bloc, parmi les parcours existants de la carte.
    - La liste ne peut pas être vidée : aucun bloc orphelin (un bloc ne peut pas être retiré de son dernier parcours).
    - L'option est désactivée si la carte ne comporte qu'un seul parcours.
    - Toute modification de rattachement marque la carte, et donc le projet, comme modifié.


---

# Transitions

## FN020 : Créer une transition
- **Description** : Créer une transition orientée entre deux blocs de la carte narrative.
- **Références** : SU004 ; menu « Project › Transitions › New ».
- **Comportement attendu** :
    - En MVP, la création est initiée depuis le menu (pas de barre d'outils).
    - L'utilisateur sélectionne un bloc source ; si aucun bloc n'est actif, il devient actif. Une connexion (tracé temporaire) suit alors le curseur jusqu'au clic sur le port du bloc cible.
    - La transition est orientée : le port sortant du bloc source est relié au port entrant du bloc cible.
    - Le chaînage est contraint par la matrice des types de blocs : Début → Scène ou Pivot ; Scène → Scène, Pivot ou Fin ; Pivot → Condition ; Condition → Scène ou Fin ; Fin → aucune. Les cycles restent autorisés (par ex. Scène → Pivot → Condition → la même Scène).
    - L'application refuse la création si une transition existe déjà pour la paire ordonnée de blocs (source, cible), ou si l'enchaînement des deux types de blocs n'est pas autorisé par la matrice.
    - La transition est représentée par une ligne ; elle suit les déplacements des blocs qu'elle relie et n'est pas déplaçable en tant que telle.
    - L'appartenance aux parcours est dérivée : une transition appartient à un parcours si et seulement si ses deux blocs y appartiennent (aucun rattachement direct).
    - Toute création marque la carte, et donc le projet, comme modifié.

## FN021 : Annoter et modifier une transition
- **Description** : Annoter une transition d'un texte libre et modifier ses attributs éditables.
- **Références** : SU004 ; menu « Project › Transitions › Edit... ».
- **Comportement attendu** :
    - L'annotation s'effectue via le dialogue d'édition de la transition (champ « Note »).
    - La note de la transition est affichée dans une infobulle au survol de la ligne représentative.
    - Une transition ne porte pas de condition (la condition structurée a été retirée du modèle, TSK39 séance 12).
    - Toute modification marque la carte, et donc le projet, comme modifié.

## FN022 : Supprimer une transition
- **Description** : Supprimer une transition entre deux blocs.
- **Références** : SU004 ; menu « Project › Transitions › Delete... ».
- **Comportement attendu** :
    - Une confirmation est demandée avant la suppression.
    - La suppression d'une transition ne supprime aucun rattachement de parcours (l'appartenance est dérivée des blocs, RG041) ; elle est indépendante de la suppression des blocs (hors cascade de FN018).
    - Toute suppression marque la carte, et donc le projet, comme modifié.


---

# Parcours

## FN023 : Créer un parcours
- **Description** : Créer un parcours dans la carte.
- **Références** : SU005 ; menu « Project › Journeys › New » ; liste des parcours dans « Display › Journey ».
- **Comportement attendu** :
    - La création s'effectue via un dialogue d'édition ouvert par « Project › Journeys › New » (libellé et note saisis, libellé proposé par défaut) — TSK39 séance 12 (1.8).
    - Le nouveau parcours reçoit un identifiant unique, le libellé saisi et la note saisie.
    - Le nouveau parcours n'est pas activé : le parcours actif reste inchangé (si le filtre de parcours est désactivé, tous les parcours sont actifs).
    - Toute création marque la carte, et donc le projet, comme modifié.

## FN024 : Renommer et décrire un parcours
- **Description** : Modifier le libellé et la note d'un parcours.
- **Références** : SU005.
- **Comportement attendu** :
    - La modification s'effectue via un dialogue d'édition.
    - Toute modification marque la carte, et donc le projet, comme modifié.

## FN025 : Dupliquer un parcours — **supprimée séance 12 (TSK39 1.9)**
- **Description** : la duplication d'un parcours a été retirée (entrée « Project › Journeys › Copy », use case et règle RG043 supprimés). Le numéro est conservé pour la traçabilité.

## FN026 : Activer un parcours
- **Description** : Activer un parcours comme parcours actif.
- **Références** : SU005 ; liste des parcours dans « Display › Journey ».
- **Comportement attendu** :
    - L'activation s'effectue depuis la liste des parcours.
    - L'activation rend le parcours actif : le filtre d'affichage s'y applique (FN029) et les nouveaux blocs y sont rattachés (FN014).
    - L'activation marque la carte, et donc le projet, comme modifié.

## FN027 : Supprimer un parcours
- **Description** : Supprimer un parcours de la carte narrative.
- **Références** : SU005.
- **Comportement attendu** :
    - La suppression du dernier parcours de la carte est impossible : l'application affiche un message explicatif.
    - La suppression s'effectue via un dialogue de sélection du parcours à supprimer, puis une confirmation — TSK39 séance 12 (1.8).
    - **Les rattachements des blocs du parcours supprimé sont réaffectés au parcours par défaut**.
    - Si le parcours supprimé était le parcours par défaut, le plus ancien parcours restant devient le parcours par défaut ; si c'était le parcours activé, le parcours par défaut devient le parcours activé.
    - Toute suppression marque la carte, et donc le projet, comme modifié.

## FN038 : Définir le parcours par défaut
- **Description** : Désigner l'un des parcours de la carte comme parcours par défaut.
- **Références** : SU005 ; menu « Project › Journeys › Set as Default... ».
- **Comportement attendu** :
    - La désignation s'effectue via un dialogue de sélection du parcours à définir par défaut.
    - Il n'existe toujours qu'un seul parcours par défaut : la désignation remplace le parcours par défaut courant.
    - Le parcours par défaut est le parcours de rattachement des nouveaux blocs lorsque le filtre de parcours est désactivé (sinon, c'est le parcours actif, FN014), et celui de réaffectation des rattachements en cas de suppression d'un parcours.
    - La désignation ne modifie pas le parcours actif.
    - Toute désignation marque la carte, et donc le projet, comme modifié.


## FN039 : Filtrer l'affichage par agent
- **Description** : Afficher soit tous les blocs et transitions de la carte, soit seulement ceux auxquels un agent participe — dans les vues portant sur la carte narrative, pas dans la vue « Agents ».
- **Références** : SU006, SU008 ; règles RG063 (filtre agent), RG064 (intersection avec le filtre de parcours).
- **Comportement attendu** :
    - Point d'entrée : case cochable « All agents » en tête de « Display › Agent » (cochée = filtre désactivé, état par défaut à l'ouverture d'un projet) ; cocher un agent active le filtre agent.
    - Sous filtre agent actif, ne restent pleinement visibles que les blocs auxquels l'agent participe, les transitions dont les deux blocs sont visibles, et les participations/relations dont le bloc d'ancrage est visible ; les autres éléments sont estompés (opacité réduite) et non interactifs.
    - Filtre agent et filtre de parcours actifs simultanément : intersection des deux filtres (RG064).
    - Le filtre agent n'est pas persisté entre les sessions et ne marque pas la carte comme modifiée.

---

# Visualisation

## FN028 : Naviguer dans l'espace de travail
- **Description** : Naviguer dans l'espace graphique de représentation de la carte narrative.
- **Références** : SU006.
- **Comportement attendu** :
    - La navigation s'effectue par les ascenseurs horizontal et vertical.
    - L'espace de travail (visualisation) est virtuellement illimité (dans les limites du système d'exploitation).
    - La grille d'alignement des blocs est toujours visible et active.
    - Les positions des ascenseurs et le niveau de zoom ne constituent pas des données métier : ils ne sont pas conservés entre les sessions et ne marquent pas la carte comme modifiée.
    - La fenêtre démarre en 1280×720 (`window_width`/`window_height`, géométrie initiale `setGeometry(100, 100, …)` façon planoscript) et est **librement redimensionnable en réduction** — aucune taille minimale fixe (TSK34, séance 10) ; le minimum effectif est piloté par les vues (ex. `setMinimumSize(0, 0)` sur la vue matrice, TSK30) ; l'interface reste pleinement fonctionnelle à 1280×720.
    - Le zoom est à définir en phase de conception.

## FN029 : Filtrer l'affichage par parcours
- **Description** : Afficher soit tous les blocs et transitions de la carte, soit seulement ceux du parcours actif — dans les vues portant sur la carte narrative (vues « Journeys », « Relationships », aperçu « Preview »), pas dans la vue « Agents ».
- **Références** : SU006.
- **Comportement attendu** :
    - Le filtre permet de basculer entre « tout afficher » et « parcours actif ».
    - Point d'entrée : case cochable « All journeys » en tête de « Display › Journey » (cochée = filtre désactivé) ; cocher un parcours active ce parcours et le filtre.
    - **Le filtre est désactivé par défaut à l'ouverture d'un projet** et son état n'est pas persisté entre les sessions.
    - **Le filtre s'applique aux vues portant sur la carte narrative** (vue « Journeys », vue « Relationships », aperçu « Preview » — **pas à la vue « Agents »**, les agents étant de niveau projet) : ne restent pleinement visibles que les blocs du parcours actif, les transitions dont les deux blocs y appartiennent, et les participations et relations dont le bloc d'ancrage y appartient ; les autres éléments sont estompés (opacité réduite) et non interactifs tant que le filtre est activé.
    - La bascule d'un parcours à l'autre met à jour instantanément l'affichage des vues concernées.
    - Le filtrage ne marque pas la carte comme modifiée.


---

# Agents et participations

## FN030 : Associer des agents à un bloc
- **Description** : Associer ou dissocier un ou plusieurs agents à un bloc de la carte narrative.
- **Références** : SU008 ; menu contextuel d'un bloc « Add Participation » (vue « Journeys ») ; menu « Project › Agents › Add Participation » (libellé normalisé séance 12, TSK39 1.3) ; liste « Agents » du dialogue d'édition du bloc (FN015).
- **Comportement attendu** :
    - Depuis la vue « Parcours », le menu contextuel d'un bloc (« Add Participation ») ouvre un dialogue listant tous les agents du projet avec leur statut de participation courant pour ce bloc (coché/décoché). Cocher associe, décocher dissocie. Idem depuis la liste « Agents » du dialogue d'édition du bloc (FN015, TSK39 séance 12 3.1).
    - L'entrée est grisée hors vue « Journeys » active + bloc sélectionné (TSK39 séance 12 1.3).
    - Le dialogue permet de créer un nouvel agent et de l'associer en une seule opération (règles de FN031).
    - L'application empêche la création d'une participation en double (agent, bloc).
    - Les agents participants d'un bloc sont représentés par des badges sur le bloc dans la vue « Parcours ».
    - L'appartenance aux parcours est dérivée : une participation appartient à un parcours si et seulement si son bloc y appartient.
    - Toute association ou dissociation marque la carte, et donc le projet, comme modifiés.

## FN031 : Gérer les agents du projet
- **Description** : Créer, renommer, modifier ou supprimer un agent du projet.
- **Références** : SU008, SU009 ; sous-menu « Project › Agents » (New.../Edit.../Delete...) ; vues « Parcours » et « Agents ».
- **Comportement attendu** :
    - Un agent appartient au projet ; il est caractérisé par un identifiant unique au sein du projet, un libellé, un type (Personnage ou Artefact), une note et un contenu narratif.
    - La suppression d'un agent supprime en cascade toutes ses participations et toutes ses relations, avec confirmation préalable indiquant le nombre d'éléments supprimés.
    - Toute création, modification ou suppression d'agent marque le projet comme modifié.

## FN032 : Naviguer entre les vues (navigation croisée)
- **Description** : Basculer d'une vue à l'autre en ciblant une entité afin d'examiner ses relations dans l'autre représentation.
- **Références** : SU009, SU012.
- **Comportement attendu** :
    - Depuis la vue « Parcours », « Voir dans la vue Agents » bascule vers la vue « Agents » et met en évidence la colonne du bloc ciblé.
    - Depuis la vue « Agents », « Voir dans la vue Parcours » bascule vers la vue « Parcours » et met le focus sur le bloc (ou sur l'ensemble des blocs d'un agent).
    - Depuis la vue « Relations », « Voir dans la vue Parcours » bascule vers la vue « Parcours » et met le focus sur le bloc d'ancrage d'une relation.
    - Depuis la vue « Journeys », basculer sur la vue « Relationships » sélectionne dans le panneau latéral le bloc actuellement sélectionné dans « Journeys » s'il appartient au filtre actif, sinon le bloc Début (RG069) — acté séance 06.
    - Le focus est un état visuel temporaire : un clic dans le vide ou la touche Échap le relâche.
    - La navigation ne marque ni la carte ni le projet comme modifiés.

## FN033 : Aperçu de lecture (vue « Preview »)
- **Description** : Afficher dans la vue « Preview » un aperçu de lecture de la carte narrative courante, en lecture seule.
- **Références** : SU010, SU007 (export de lecture HTML via « Files › Export Project... », TSK42 séance 12) ; onglet « Preview » de la barre d'onglets ; filtres Journey/Agent (FN029, FN039, RG048/RG063/RG064) ; conception `docs/conception/05_preview-FR.md` (TSK37).
- **Comportement attendu** :
    - L'onglet « Preview » est présent dans la barre d'onglets à côté des vues « Agents », « Journeys », « Relationships » ; entrée « View › Preview » active (bascule vers la vue, TSK39 séance 12 1.1 ; renommée depuis « Export », TSK37).
    - La vue héberge le panneau latéral de filtres (même `FiltersSidePanel` que la vue « Journeys », sans liste de blocs), miroirs du menu « Display » et des autres vues.
    - L'aperçu est en lecture seule : aucune interaction sur le contenu ; les liens hypertexte internes sont des ancres à scroll passif uniquement.
    - L'aperçu est régénéré à chaque bascule sur l'onglet « Preview », **et** après chaque modification du modèle lorsque la vue est déjà active ; jamais en arrière-plan.
    - Rendu dynamique selon les filtres actifs (RG048/RG063/RG064) : filtre de parcours actif → parcours actif seul (« Tous les parcours » → tous les parcours) ; filtre agent → blocs auxquels l'agent participe, transitions dont les deux blocs sont visibles, relations dont le bloc d'ancrage est visible ; les éléments hors filtre sont **omis du rendu**.
    - Sections restituées : a) projet (`lb`) ; b) liste des agents `lb (typ)` (liens vers g) ; c) carte (`lb`) ; d) liste des parcours (liens vers e) ; e) parcours : séquence des blocs depuis Start dans l'ordre de la séquence de lecture (RG044), chaque bloc avec `lb`, `typ`, `content` (note en infobulle au survol), **les agents participants sous le contenu, ligne préfixée « Participations: »** (TSK39 4.1, libellé TSK41 séance 12), transitions rendues en ligne, puis **les relations ancrées sous la liste des agents, chaque ligne préfixée « Relationships: »** (lb agents 1 et 2, `typ`, `content`, note en infobulle — TSK39 4.2, libellé TSK41 séance 12) — l'« état des relations » est restitué sous chaque bloc d'ancrage, sans section finale séparée ; les branches non jointes au Start sont restituées marquées après le flux ; f) orphelins : blocs sans aucune transition entrante ni sortante ; g) agents du projet `lb (typ)` (TSK39 4.4), `content`, note en infobulle. Plus de champs de condition (retirés du modèle, TSK39 3.2/4.3). Libellé en titre, contenu en corps de texte (libellé seul si vide).
    - La visualisation de l'aperçu et l'application des filtres ne marquent ni la carte ni le projet comme modifiés.
- **Note** : vue renommée « Preview » (TSK37, séance 11) ; l'export de lecture se fait via « Files › Export Project... » (FN013/SU007, TSK42 séance 12) ; « Export Map... » reste grisée (échange entre projets, post-MVP) — coexistence « Preview » (vue in-app) / « Export Project... » (fichier) assumée.


---

# Relations entre agents

## FN034 : Gérer une relation entre agents
- **Description** : Créer, annoter, modifier ou supprimer une relation typée entre deux agents, ancrée à un bloc.
- **Références** : SU011 ; menu « Project › Relationships ».
- **Comportement attendu** :
    - La relation est binaire : elle relie exactement deux agents (une évolution à plus de deux agents est hors MVP).
    - Elle est non dirigée (paire d'agents non ordonnée) et typée ; le type est choisi dans la liste de valeurs du fichier de configuration (FN037).
    - Elle est ancrée à un bloc : « à ce moment du récit, une relation de ce type entre A et B est vraie ».
    - Les deux agents sont distincts (aucune relation d'un agent à lui-même, RG035).
    - Il ne peut exister qu'une seule relation par couple (bloc, paire d'agents) (RG035).
    - Dans le dialogue de création/édition, la liste des blocs d'ancrage est ordonnée par rang minimal sur tous les parcours (ex æquo par identifiant) — même règle que la liste du panneau de la vue « Relationships » (RG069) ; la paire d'agents n'est pas modifiable à l'édition (type, bloc d'ancrage, note, contenu le sont).
    - L'historique d'une paire d'agents est l'ensemble de ses relations ancrées, ordonnées selon la position de leur bloc dans le parcours ; l'état courant de la paire à un bloc est dérivé (jamais stocké).
    - L'appartenance aux parcours est dérivée du bloc d'ancrage.
    - La note est affichée en infobulle au survol.
    - La suppression d'un agent ou d'un bloc entraîne la suppression en cascade de ses relations.
    - Toute création, modification ou suppression marque la carte, et donc le projet, comme modifié.


---

# Conditions

## FN035 : Gérer la condition d'un bloc Condition — **supprimée séance 12 (TSK39 3.2)**
- **Description** : la condition structurée a été **retirée du modèle** pour le simplifier (champs nature / référence Artefact / libellé supprimés du dialogue d'édition, du modèle et de l'aperçu). Le numéro est conservé pour la traçabilité. La matrice des types de blocs (Pivot/Condition/Fin, RG028/RG030/RG031) est inchangée.


---

# Vue « Relations »

## FN036 : Vue « Relationships »
- **Description** : Visualiser dans l'espace de travail « Relationships » la matrice agent × agent des relations entre agents — chaque cellule affiche le type de l'état de la paire au bloc sélectionné (dernier bloc d'ancrage de rang inférieur ou égal, donnée dérivée) — avec un panneau latéral droit (filtres de parcours et d'agent, puis liste des blocs ordonnée par rang minimal sur tous les parcours), et navigation croisée vers le bloc d'ancrage dans la vue « Journeys » (FN032).
- **Références** : SU012 ; filtre de parcours FN029 ; filtre agent FN039.
- **Comportement attendu** :
    - La matrice affiche **tous les agents du projet**, même sans relation ; matrice symétrique (relations non dirigées, RG035).
    - Ordre initial des axes : alphabétique sur le libellé (ex æquo par identifiant) ; lignes et colonnes déplaçables manuellement par l'utilisateur, ordre persisté au niveau projet (fichier layout projet, comme RG067) et restauré à la réouverture.
    - La matrice est **dynamique** selon le bloc sélectionné dans le panneau : la cellule (A, B) affiche le type de l'unique relation possible par (bloc, paire) (RG035) ancrée au dernier bloc de rang inférieur ou égal ; cellule vide sinon.
    - Panneau latéral droit, trois zones de haut en bas : filtre de parcours, filtre agent (miroirs synchronisés du menu « Display » — mêmes actions, un seul état ; RG047), liste des blocs ordonnée par rang minimal sur tous les parcours (ex æquo par identifiant de bloc), restreinte aux blocs visibles sous les filtres actifs (intersection RG064).
    - Bloc sélectionné par défaut : le Start ; à l'arrivée depuis un bloc sélectionné dans « Journeys », ce bloc s'il appartient au filtre actif, sinon le Start (un élément hors filtre n'est pas sélectionnable, RG048).
    - Filtre de parcours actif (RG048) : les relations dont le bloc d'ancrage est hors filtre sont estompées (opacité de configuration) et non interactives.
    - Filtre agent actif (RG063) : tous les agents restent affichés ; les agents non concernés sont estompés (même opacité que le filtre de parcours) et la création d'une relation les concernant est interdite.
    - La vue « Relationships » fait partie du périmètre MVP.


---

# Configuration

## FN037 : Liste des types de relations
- **Description** : Lire le type des relations entre agents dans une liste de valeurs définie dans un fichier de configuration.
- **Références** : SU011.
- **Comportement attendu** :
    - En MVP, les types de relations proposés à la création (FN034) sont lus dans le fichier de configuration.
    - L'enrichissement de cette liste par l'auteur est une fonctionnalité hors MVP.


---

# Hors périmètre MVP / à définir en phase de conception

- Opérations multi-cartes : création, duplication, suppression et navigation entre plusieurs cartes narratives d'un même projet (MVP : une seule carte par projet ; le modèle prévoit plusieurs cartes).
- Import de carte narrative depuis un fichier autonome ; aucune migration des projets planoscript existants.
- Export technique de carte destiné à la réimportation ; export de lecture « par événements » — à définir en phase de conception.
- Zoom de l'espace de travail ; fonctions d'édition (annuler/rétablir, historique, couper/copier/coller) — à définir en phase de conception.
- Barres d'outils et barres latérales — actions par menu uniquement en MVP ; barres latérales à définir en phase de conception.
- Contrôle de cohérence des parcours (impasses, branches non terminées, Pivot à une seule branche, Fin non atteinte) — fonctionnalité hors MVP.
- Enrichissement par l'auteur de la liste des types de relations (FN037) — hors MVP.
- Relations à plus de deux agents — hors MVP.
- Finalisation des scenarii et fonctionnalités des vues « Agents », « Relations » et de l'aperçu « Preview » — après la phase de conception.
