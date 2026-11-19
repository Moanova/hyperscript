# Règles de gestion - Hyperscript

## Document Version
- **Version** : 1.0
- **Date** : 2026-11-09
- **Statut** : initial.


---

## 1. Gestion du projet et cycle de vie

## RG001
- **Description** : Un projet est un document local (format JSON) contenant ses métadonnées, ses agents et ses cartes narratives. Le modèle prévoit plusieurs cartes par projet ; le MVP en contient une seule.
- **Classification** : 1. Gestion du projet et cycle de vie

## RG002
- **Description** : Un seul projet peut être ouvert dans l'application à tout moment.
- **Classification** : 1. Gestion du projet et cycle de vie

## RG003
- **Description** : Un projet nouvellement créé est un projet non enregistré : il existe en mémoire mais n'est associé à aucun fichier tant que l'utilisateur ne l'a pas sauvegardé.
- **Classification** : 1. Gestion du projet et cycle de vie

## RG004
- **Description** : Chaque projet possède un identifiant stable, un nom, une date de création, une date de dernière modification et une version de format.
- **Classification** : 1. Gestion du projet et cycle de vie

## RG005
- **Description** : Les projets enregistrés ou ouverts avec succès sont ajoutés à la liste des projets récents, ordonnée du plus au moins récemment ouvert, avec une seule occurrence par fichier et une limite définie par la configuration ; les entrées dont le fichier est inexistant, inaccessible ou invalide sont retirées. [Post-MVP : l'entrée de menu correspondante est grisée en MVP.]
- **Classification** : 1. Gestion du projet et cycle de vie

## RG006
- **Description** : La commande « Save » n'est active que si le projet ouvert est modifié ; « Save as... » est active dès qu'un projet est ouvert ; sans projet ouvert, les deux sont désactivées.
- **Classification** : 1. Gestion du projet et cycle de vie

## RG007
- **Description** : Lorsqu'aucun projet n'est ouvert, les entrées des menus Files (Close, Save, Save as...), Edit, Display et Project sont grisées. En MVP, « Export Map... », « Import Map... », « Recent Projects », tout le menu Edit et le sous-menu Zoom restent grisés même avec un projet ouvert.
- **Classification** : 1. Gestion du projet et cycle de vie

## RG008
- **Description** : À l'ouverture ou à la création d'un projet, les entrées des menus Files (Close, Save, Save as...), Display et Project sont activées (hors entrées grisées en MVP, RG007).
- **Classification** : 1. Gestion du projet et cycle de vie

## RG009
- **Description** : L'ouverture d'un projet ne remplace le projet courant qu'après lecture et validation réussies du fichier sélectionné ; sinon, une erreur est affichée et le projet courant reste inchangé. Aucun projet planoscript n'est migré : un tel fichier est traité comme incompatible.
- **Classification** : 1. Gestion du projet et cycle de vie

## RG010
- **Description** : L'application n'ouvre un projet que si sa version de format est supportée ; elle ne migre aucun fichier provenant d'une autre application et ne remplace jamais un fichier d'origine sans action explicite de l'utilisateur.
- **Classification** : 1. Gestion du projet et cycle de vie

## RG011
- **Description** : Une sauvegarde ne remplace le fichier existant qu'après écriture complète et réussie de la nouvelle version ; en cas d'échec, le fichier précédemment enregistré reste exploitable et le projet conserve son état modifié ; après une sauvegarde réussie, la date de dernière modification du projet est mise à jour.
- **Classification** : 1. Gestion du projet et cycle de vie

## RG012
- **Description** : « Save as... » crée ou remplace un fichier à l'emplacement choisi (avec confirmation si le fichier existe déjà) ; après une sauvegarde réussie, ce fichier devient le fichier associé au projet ouvert, et l'ancien fichier n'est ni renommé ni supprimé.
- **Classification** : 1. Gestion du projet et cycle de vie

## RG013
- **Description** : Un nouveau projet est nommé « Nouveau projet » et contient une carte narrative nommée « Carte narrative principale », créée avec un bloc Début (créé automatiquement) et un parcours par défaut (créé et activé).
- **Classification** : 1. Gestion du projet et cycle de vie

## RG014
- **Description** : Un projet contient toujours au moins une carte narrative (en MVP : exactement une).
- **Classification** : 1. Gestion du projet et cycle de vie

## RG015
- **Description** : Une seule instance de l'application peut tourner à la fois ; si une instance est déjà en cours, un nouveau lancement se termine silencieusement.
- **Classification** : 1. Gestion du projet et cycle de vie

## RG016
- **Description** : Aucun projet planoscript existant n'est migré : les fichiers planoscript sont considérés comme incompatibles (RG009).
- **Classification** : 1. Gestion du projet et cycle de vie

## RG017
- **Description** : L'export sur fichier est hors périmètre MVP (seul l'aperçu in-app, vue « Export », est disponible en MVP). Lorsqu'il sera disponible, l'export de lecture génère un dossier autonome nommé d'après la carte (fichier d'index + pages liées), dans l'ordre de la séquence du parcours indépendamment des positions graphiques, et ne marque ni la carte ni le projet comme modifiés ; l'export technique reste à définir en phase de conception.
- **Classification** : 1. Gestion du projet et cycle de vie

## 2. Structure de la carte narrative

## RG018
- **Description** : Chaque carte narrative possède un identifiant stable.
- **Classification** : 2. Structure de la carte narrative

## RG019
- **Description** : Chaque bloc, transition, participation, relation, parcours et rattachement d'un bloc à un parcours possède un identifiant entier unique au sein de sa carte narrative.
- **Classification** : 2. Structure de la carte narrative

## RG020
- **Description** : Les libellés des blocs, transitions, participations, relations, parcours et agents ne sont pas contraints à l'unicité.
- **Classification** : 2. Structure de la carte narrative

## RG021
- **Description** : Une carte narrative contient toujours au moins un parcours.
- **Classification** : 2. Structure de la carte narrative

## RG022
- **Description** : La suppression d'une carte narrative est irréversible et entraîne la suppression de tout son contenu (blocs, transitions, participations, relations, parcours, rattachements). [Hors MVP : une seule carte par projet.]
- **Classification** : 2. Structure de la carte narrative

## RG023
- **Description** : La suppression d'un bloc entraîne la suppression en cascade de ses transitions, de ses participations, de ses relations ancrées et de ses rattachements aux parcours ; un message d'information est affiché si le bloc était référencé par d'autres éléments.
- **Classification** : 2. Structure de la carte narrative

## RG024
- **Description** : La suppression du dernier parcours d'une carte est impossible.
- **Classification** : 2. Structure de la carte narrative

## RG025
- **Description** : Chaque carte narrative possède un et un seul bloc Début, créé automatiquement à la création de la carte, jamais supprimable ni duplicable ; le type « Début » n'est proposé nulle part ailleurs (création ou édition d'un autre bloc) ; le bloc Début ne reçoit jamais de transition entrante.
- **Classification** : 2. Structure de la carte narrative

## RG026
- **Description** : Un bloc Fin ne peut recevoir aucune transition sortante (degré sortant 0). En cours d'édition, un parcours peut temporairement ne pas comporter de bloc Fin (le contrôle de cohérence est hors MVP).
- **Classification** : 2. Structure de la carte narrative

## RG027
- **Description** : Un bloc peut avoir 0 ou n transitions entrantes et 0 ou n transitions sortantes, dans les limites des types autorisés par la matrice d'enchaînement (RG028).
- **Classification** : 2. Structure de la carte narrative

## RG028
- **Description** : Le chaînage par transition est contraint par la matrice des types de blocs autorisés :

  | Type du bloc source | Types des blocs cibles autorisés |
  | --- | --- |
  | Début | Scène, Pivot |
  | Scène | Scène, Pivot, Fin |
  | Pivot | Condition |
  | Condition | Scène, Fin |
  | Fin | — (aucune transition sortante) |

  Les cycles sont autorisés (ex. Scène → Pivot → Condition → la même Scène). En construction, un bloc peut avoir 0 ou n transitions entrantes et sortantes ; en carte finalisée et cohérente, 1 ou n (hors Début : 0 entrante ; Fin : 0 sortante) — ce contrôle de cohérence est hors MVP. Il ne peut exister qu'une seule transition par paire ordonnée de blocs.
- **Classification** : 2. Structure de la carte narrative

## RG029
- **Description** : Le type d'un bloc est choisi à sa création et immuable ensuite.
- **Classification** : 2. Structure de la carte narrative

## RG030
- **Description** : Un bloc Pivot ne peut recevoir de transitions entrantes que de blocs Début ou Scène, et n'émettre de transitions sortantes que vers des blocs Condition (matrice RG028) ; plusieurs blocs Condition issus d'un même Pivot valent OU.
- **Classification** : 2. Structure de la carte narrative

## RG031
- **Description** : Un bloc Condition ne peut recevoir de transitions entrantes que de blocs Pivot, et n'émettre de transitions sortantes que vers des blocs Scène ou Fin (matrice RG028) ; il porte une condition structurée (nature : choix / artefact / compétence / flag ; référence éventuelle vers un agent Artefact ; libellé) — unique support de celle-ci. Chaîner des blocs Condition (Condition → Condition) n'est pas autorisé : le ET n'est pas exprimable ; deux blocs Condition issus d'un même Pivot valent OU (RG030).
- **Classification** : 2. Structure de la carte narrative

## RG032
- **Description** : Il ne peut exister qu'une seule participation par couple (bloc, agent).
- **Classification** : 2. Structure de la carte narrative

## RG033
- **Description** : La suppression d'un agent entraîne la suppression en cascade de toutes ses participations et de toutes ses relations, avec un message d'information si l'agent était référencé.
- **Classification** : 2. Structure de la carte narrative

## RG034
- **Description** : La suppression d'un parcours réaffecte au parcours par défaut les rattachements des blocs qui n'appartenaient qu'à lui (aucun bloc orphelin).
- **Classification** : 2. Structure de la carte narrative

## RG035
- **Description** : Une relation est binaire (exactement deux agents — paire non ordonnée, TSK25), non dirigée et typée, et ancrée à exactement un bloc ; son type est lu dans la liste de valeurs du fichier de configuration ; il ne peut exister qu'une seule relation par couple (bloc, paire d'agents) : le lien entre un bloc et une relation est unique (décision TSC séance 06, pour le MVP) ; les entités Bloc et Relation restent distinctes dans le modèle de données, afin de permettre en post-MVP plusieurs relations — donc plusieurs types — par paire et par bloc.
- **Classification** : 2. Structure de la carte narrative

## 3. Logique des parcours et appartenance

## RG037
- **Description** : À la création d'une carte narrative, un parcours par défaut est automatiquement créé.
- **Classification** : 3. Logique des parcours et appartenance

## RG038
- **Description** : La copie d'un parcours ne modifie pas le parcours activé quanf le filtre de parcours est actif.
- **Classification** : 3. Logique des parcours et appartenance

## RG039
- **Description** : Il existe toujours un parcours par défaut, et un seul ; si le parcours par défaut est supprimé, le plus ancien parcours restant le devient ; si le parcours activé est supprimé, le parcours par défaut devient l'actif.
- **Classification** : 3. Logique des parcours et appartenance

## RG040
- **Description** : Aucun bloc orphelin : tout bloc appartient à au moins un parcours ; à sa création, un bloc est rattaché au parcours actif si le filtre de parcours est activé, au parcours par défaut sinon ; un bloc ne peut pas être retiré de son dernier parcours.
- **Classification** : 3. Logique des parcours et appartenance

## RG041
- **Description** : L'appartenance à un parcours est dérivée et jamais stockée : une transition appartient à un parcours si et seulement si ses deux blocs y appartiennent ; une participation ou une relation y appartient si et seulement si son bloc d'ancrage y appartient.
- **Classification** : 3. Logique des parcours et appartenance

## RG042
- **Description** : Les parcours auxquels un bloc est rattaché se modifient via la liste des parcours présentée dans le dialogue d'édition du bloc ; cette liste ne peut pas être vidée ; l'option est désactivée s'il n'existe qu'un seul parcours, et pour le bloc Début (RG068).
- **Classification** : 3. Logique des parcours et appartenance

## RG043
- **Description** : La copie d'un parcours reprend les rattachements de ses blocs.
- **Classification** : 3. Logique des parcours et appartenance

## RG044
- **Description** : La séquence de lecture d'un parcours est calculée en profondeur depuis le bloc Début, en ne suivant que les transitions du parcours, les branches étant ordonnées par identifiant de transition croissant, les cycles étant mémoïsés et les blocs inatteignables recevant un rang déterministe après les autres ; le rang de chaque bloc est recalculé à chaque modification du graphe et au chargement du projet, et n'est jamais modifiable manuellement.
- **Classification** : 3. Logique des parcours et appartenance

## 4. Visualisation et interaction

## RG045
- **Description** : La position (x, y) de chaque bloc est conservée dans les métadonnées graphiques associées au projet, entre les sessions.
- **Classification** : 4. Visualisation et interaction

## RG046
- **Description** : Les blocs s'alignent automatiquement sur la grille lors de leur création et **à la libération** de leurs déplacements (pendant le déplacement, la position est libre — évolution TSC séance 05, TSK24 : le snap en continu causait des saccades).
- **Classification** : 4. Visualisation et interaction

## RG047
- **Description** : La modification du niveau de zoom, de la position des barres de défilement ou de l'état d'un filtre (parcours ou agent) ne constitue pas une modification de la carte ni du projet, et n'est pas persistée entre les sessions.
- **Classification** : 4. Visualisation et interaction

## RG048
- **Description** : Le filtre de parcours affiche soit tous les parcours, soit un seul, dans les vues portant sur la carte narrative (vues « Journeys », « Relationships », aperçu « Export ») — il ne s'applique pas à la vue « Agents » (agents de niveau projet, vue décorrélée des participations aux blocs) ; il est désactivé par défaut à l'ouverture d'un projet ; sous filtre actif, seuls les blocs du parcours, les transitions dont les deux blocs y appartiennent et les participations/relations dont le bloc d'ancrage y appartient restent pleinement visibles — les autres éléments sont estompés (degré d'opacité défini en configuration) et non interactifs.
- **Classification** : 4. Visualisation et interaction

## RG049
- **Description** : Dans un espace de travail, un seul élément est sélectionné à la fois ; la création ou le clic sur un élément le sélectionne et déselectionne le précédent ; un clic dans le vide déselectionne.
- **Classification** : 4. Visualisation et interaction

## RG050
- **Description** : Un bloc ne peut pas être créé à des coordonnées chevauchant celles d'un bloc existant ; sa position est ajustée automatiquement pour éviter tout chevauchement.
- **Classification** : 4. Visualisation et interaction

## RG051
- **Description** : Lorsqu'un bloc déplacé dépasse la partie visible de l'espace de travail, le défilement s'ajuste pour maintenir le bloc visible.
- **Classification** : 4. Visualisation et interaction

## RG052
- **Description** : Le tracé d'une transition ne doit jamais chevaucher un bloc qui n'en est ni la source ni la cible ; le routage de la transition s'ajuste automatiquement, sans modifier les coordonnées des blocs ni les données du projet (ajustement purement graphique).
- **Classification** : 4. Visualisation et interaction

## RG053
- **Description** : La zone cliquable d'un élément graphique (bloc, transition) est définie par sa forme géométrique, élargie au-delà de l'épaisseur de son trait.
- **Classification** : 4. Visualisation et interaction

## RG054
- **Description** : Les notes des blocs et des transitions s'affichent en infobulle dès le survol, sans délai.
- **Classification** : 4. Visualisation et interaction

## RG055
- **Description** : À l'ouverture d'un menu contextuel, l'élément situé sous le curseur est d'abord sélectionné ; le menu contextuel reste aligné sur le menu applicatif (mêmes actions et gestionnaires) selon la vue active et la sélection courante. Sur la grille vide de la vue « Journeys », les entrées de création portent des libellés propres au menu contextuel (« New Block », « New Transition ») — acté séance 04 (TSK16).
- **Classification** : 4. Visualisation et interaction

## RG056
- **Description** : Le focus de navigation croisée entre les vues (y compris la vue « Relations ») est un état visuel temporaire : il ne marque ni la carte ni le projet comme modifiés et n'est pas persisté.
- **Classification** : 4. Visualisation et interaction

## 5. Architecture technique et modèle de données

## RG057
- **Description** : Les agents appartiennent au projet, et non à la carte narrative.
- **Classification** : 5. Architecture technique et modèle de données

## RG058
- **Description** : L'interface ne modifie jamais directement le modèle métier : toute modification passe par les couches applicatives (use cases et services).
- **Classification** : 5. Architecture technique et modèle de données

## RG059
- **Description** : Aucune valeur n'est codée en dur dans l'interface : dimensions, couleurs, textes par défaut et limites proviennent du fichier de configuration de l'application.
- **Classification** : 5. Architecture technique et modèle de données

## RG060
- **Description** : Les métadonnées de représentation graphique (positions des blocs, ordre des lignes/colonnes de la matrice « Relationships » — RG070) sont stockées dans un fichier dédié associé au projet et restaurées à la réouverture.
- **Classification** : 5. Architecture technique et modèle de données

## RG061
- **Description** : Le projet est enregistré dans un fichier unique structuré (JSON) contenant les métadonnées et les données, associé au fichier de métadonnées graphiques.
- **Classification** : 5. Architecture technique et modèle de données

## RG062
- **Description** : L'auteur peut à tout moment désigner l'un des parcours de la carte comme parcours par défaut ; la désignation remplace le parcours par défaut courant et ne modifie pas le parcours actif. Il n'existe toujours qu'un seul parcours par défaut (RG039).
- **Classification** : 3. Logique des parcours et appartenance

## RG063
- **Description** : Le filtre agent affiche, dans les vues portant sur la carte narrative, soit tous les éléments, soit seulement les blocs auxquels l'agent participe, les transitions dont les deux blocs sont ainsi visibles, et les participations/relations dont le bloc d'ancrage est visible ; les autres éléments sont estompés (même degré d'opacité que le filtre de parcours, défini en configuration) et non interactifs. Le filtre agent est désactivé par défaut à l'ouverture d'un projet, n'est pas persisté entre les sessions, ne marque ni la carte ni le projet comme modifiés, et ne s'applique pas à la vue « Agents ».
- **Classification** : 4. Visualisation et interaction

## RG064
- **Description** : Lorsqu'un filtre de parcours et un filtre agent sont actifs simultanément, un élément n'est pleinement visible que s'il appartient au parcours filtré ET à la visibilité induite par l'agent (intersection des deux filtres).
- **Classification** : 4. Visualisation et interaction

## RG065
- **Description** : Dans la vue « Agents », l'espace de travail a le même fond sombre que la vue « Journeys » mais est habillé de points à la place d'une grille (espacement, rayon et couleur définis en configuration ; purement décoratifs) ; les cartes agent sont déplaçables librement en 2D pendant le déplacement, dans les limites de la scène (aucun verrouillage d'axe, aucun snap en cours de drag — retour TSC séance 04 : le snap continu rendait les déplacements étranges) ; **à la libération du déplacement**, la carte se positionne sur la cellule la plus proche d'une **grille de cellules invisible** (taille des cellules en configuration `agents_view_cell_width`/`agents_view_cell_height`, ancrée sur l'origine de la scène) ; si cette cellule est occupée par une autre carte, la carte est placée sur la cellule libre la plus proche ; la position est également ancrée sur une cellule à la création et au chargement (évolution TSC séance 05, TSK21) ; à la **création** d'un agent, la carte est placée sur la première cellule libre à droite de la boîte englobante des cartes existantes (cellule par défaut si aucune carte) (TSK22) ; lors d'un **déplacement**, la cellule de dépôt doit se trouver dans la boîte englobante des autres cartes élargie d'une cellule de chaque côté — la boîte du groupe ne grandit donc que d'une cellule par déplacement — sinon la carte est ramenée sur la cellule libre la plus proche dans cette zone (carte unique : aucune contrainte, placement libre) (TSK23).
- **Classification** : 4. Visualisation et interaction

## RG066
- **Description** : Chaque agent du projet est représenté dans la vue « Agents » par une carte de dimensions supérieures à celles d'un bloc (définies en configuration), sans ports, affichant le libellé et le type ; sélection unique ; note en infobulle au survol ; menu contextuel aligné sur le menu applicatif (édition, copie, suppression, association à un bloc). Aucun badge de comptage des participations n'est affiché sur la carte : les participations et relations sont traitées dans d'autres vues.
- **Classification** : 4. Visualisation et interaction

## RG067
- **Description** : Les positions des cartes agent de la vue « Agents » sont mémorisées au niveau projet dans le répertoire des métadonnées graphiques (fichier layout projet, distinct des layouts par carte narrative, conformément à la structure des données métier : les agents appartiennent au projet) et restaurées à la réouverture ; elles n'ont aucune valeur métier.
- **Classification** : 5. Architecture technique et modèle de données

## RG068
- **Description** : Le bloc Début appartient à tous les parcours de la carte narrative et l'auteur ne peut jamais modifier ce rattachement : à la création d'un parcours, le bloc Début y est automatiquement rattaché ; dans le dialogue d'édition du bloc Début, la liste des parcours est désactivée (RG042) ; la suppression d'un parcours ne le concerne jamais (RG034). Acté séance 06 ; implémentation prévue en tâche dédiée avant TSK20.
- **Classification** : 3. Logique des parcours et appartenance

## RG069
- **Description** : Dans la vue « Relationships », la matrice affiche **tous les agents du projet**, même ceux qui n'ont aucune relation ; la cellule (A, B) affiche le type de l'état de la paire A-B au bloc sélectionné, c'est-à-dire la relation ancrée au dernier bloc de rang inférieur ou égal au rang du bloc sélectionné (donnée dérivée, jamais stockée) — une seule relation par (bloc, paire), donc un seul type par cellule (RG035) ; la liste des blocs du panneau latéral est ordonnée du haut vers le bas par **rang minimal sur tous les parcours** (ex æquo par identifiant de bloc), restreinte aux blocs visibles sous les filtres actifs (intersection RG064) ; le bloc sélectionné par défaut est le bloc Début (RG068) — à l'arrivée depuis un bloc sélectionné dans « Journeys », ce bloc s'il appartient au filtre actif, sinon le Début (un élément hors filtre n'est pas sélectionnable) ; sous filtre agent actif, les agents non concernés sont estompés (même opacité que RG063) et la création d'une relation les concernant est interdite. Actée séance 06.
- **Classification** : 4. Visualisation et interaction

## RG070
- **Description** : Dans la vue « Relationships », l'ordre initial des lignes et des colonnes de la matrice est alphabétique sur le libellé de l'agent (ex æquo par identifiant) ; l'auteur peut déplacer chaque ligne et chaque colonne (glisser l'en-tête) ; l'ordre résultant est persisté au niveau projet dans le fichier layout projet (comme RG067) et restauré à la réouverture ; sans valeur métier. Actée séance 06.
- **Classification** : 4. Visualisation et interaction
