# Hyperscript ::: Scenarii d'utilisation

## Document Version
- **Version** : 1.0
- **Date** : 09-11-2026
- **Statut** : initial.


---

## SU001 : Gérer un projet narratif
- **Description** : En tant qu'auteur, je peux créer, ouvrir, enregistrer, renommer et fermer un projet narratif afin de regrouper, retrouver et poursuivre le travail sur ma carte narrative.
- **Complément** :
    - Un projet est un document local contenant les métadonnées du projet, les agents et la ou les cartes narratives.
    - Un seul projet peut être ouvert dans l'application à tout moment.
    - Un projet nouvellement créé est un projet non enregistré : il existe en mémoire mais n'est associé à aucun fichier tant que l'utilisateur ne l'a pas sauvegardé.
    - Chaque projet possède un identifiant stable, un nom, une date de création et une date de dernière modification.
    - Le chemin du fichier est un état de l'application ; il ne constitue pas une donnée métier portable du projet.
    - Un nouveau projet est nommé « Nouveau projet » et contient une carte narrative nommée « Carte narrative principale ».
- **Critères d'acceptation** :
    - L'utilisateur peut créer un projet depuis le menu, un raccourci clavier ou le message d'accueil.
    - L'utilisateur peut ouvrir un fichier projet valide depuis le système de fichiers ; en cas de fichier invalide, incompatible ou illisible, l'application affiche une erreur claire et conserve le projet ouvert inchangé.
    - L'utilisateur peut enregistrer un projet non enregistré en choisissant un nom et un emplacement ; enregistrer les modifications d'un projet déjà associé à un fichier sans nouvelle boîte de dialogue ; enregistrer une copie sous un autre nom ou un autre emplacement (la copie devient le projet courant).
    - L'utilisateur peut fermer un projet ; si le projet est modifié lors d'une fermeture, d'une ouverture, d'une création ou d'une sortie, l'application propose « Enregistrer », « Ne pas enregistrer », « Annuler ».
    - Un projet enregistré est ajouté à la liste des projets récents, qui respecte la limite configurée et retire les fichiers qui n'existent plus.
- **Périmètre MVP** :
    - Chaque projet ne contient qu'une seule carte narrative.
    - Pas de migration des projets planoscript existants.


## SU002 : Gérer une carte narrative
- **Description** : En tant qu'auteur, je peux nommer et modifier le contenu de la carte narrative de mon projet afin de définir mon récit.
- **Complément** :
    - Une carte narrative appartient à un et un seul projet ; elle possède un identifiant stable, un nom, une date de création et une date de dernière modification.
    - Un projet contient toujours au moins une carte narrative.
    - Une carte est considérée comme modifiée lorsque l'utilisateur ajoute, modifie ou supprime un bloc, une transition, une participation ou une relation, ou modifie la position d'un bloc dans l'espace de travail.
    - La modification de la position des barres de défilement ne constitue pas une modification de la carte.
- **Critères d'acceptation** :
    - L'utilisateur peut renommer la carte en éditant directement son libellé ou via une boîte de dialogue.
    - Toute modification met à jour la date de dernière modification de la carte et celle du projet.
- **Périmètre MVP** :
    - Une seule carte narrative par projet : la création, la duplication, la suppression, la navigation entre cartes et l'import/export de carte ne sont pas disponibles. Seuls le renommage et la modification du contenu sont fonctionnels en MVP (l'export sur fichier, SU007, est hors MVP — entrée « Files › Export Map » grisée ; l'aperçu in-app, vue « Export » (SU010), fait partie du MVP minimal).


## SU003 : Gérer un bloc narratif
- **Description** : En tant qu'auteur, je peux créer, nommer, déplacer, modifier ou supprimer un bloc narratif afin de définir le contenu des enchaînements de mon récit.
- **Complément** :
    - Le bloc narratif est l'unité de récit de la carte narrative. Son type — Début, Scène, Pivot, Condition ou Fin — est choisi à la création et immuable ensuite ; chaque type a un rendu visuel spécifique.
    - Chaque bloc possède un identifiant unique au sein de la carte, un libellé (non soumis à unicité), une note et un contenu narratif.
    - Chaque bloc dispose de deux ports, entrant et sortant, destinés à la création des transitions.
    - Chaque bloc est déplaçable dans l'espace de travail mais non redimensionnable ; il s'aligne automatiquement sur la grille à la création et lors des déplacements ; sa position est conservée entre les sessions.
    - À la création d'une carte narrative, un bloc Début unique est créé automatiquement.
    - Un bloc Fin ne peut pas recevoir de transition sortante.
    - Un bloc Pivot possède au moins deux transitions sortantes ; la promotion Scène → Pivot est automatique et unidirectionnelle lorsqu'une deuxième transition sortante est créée (jamais l'inverse).
    - Un bloc Condition possède exactement une transition entrante (depuis un Pivot) et une sortante (vers la scène gardée) ; il porte une condition structurée : nature (choix / artefact / compétence / flag), référence éventuelle vers un agent Artefact, libellé. Chaîner des blocs Condition équivaut à un ET ; deux blocs Condition issus d'un même Pivot équivalent à un OU.
    - Rattachement aux parcours : ce sont les blocs qui sont rattachés aux parcours. Aucun bloc orphelin : tout bloc appartient à au moins un parcours ; tout bloc nouvellement créé est automatiquement rattaché au parcours par défaut ; un bloc ne peut pas être retiré de son dernier parcours.
    - La suppression d'un bloc entraîne la suppression en cascade de ses transitions, participations, relations ancrées et rattachements aux parcours.
- **Critères d'acceptation** :
    - L'utilisateur peut créer un bloc depuis le menu général ou le menu contextuel, en choisissant son type ; le bloc est automatiquement rattaché au parcours par défaut et positionné sur la grille à l'emplacement désigné.
    - L'utilisateur peut dupliquer un bloc (copie avec nom distinctif et nouvel identifiant, rattachée au parcours par défaut).
    - L'utilisateur peut modifier les attributs éditables d'un bloc via un dialogue d'édition.
    - L'utilisateur peut supprimer un bloc avec confirmation ; la suppression s'effectue en cascade selon le complément.
    - L'utilisateur peut déplacer un bloc par glisser-déposer (souris, stylet ou tactile) avec alignement automatique sur la grille.
    - Toute création, duplication, modification, déplacement ou suppression de bloc marque la carte, donc le projet, comme modifiés.
- **Périmètre MVP** :
    - Pas de barre d'outils : les actions ne sont gérées que par menu.


## SU004 : Gérer une transition entre blocs
- **Description** : En tant qu'auteur, je peux créer, annoter, modifier ou supprimer une transition entre deux blocs afin de définir les enchaînements de mon récit.
- **Complément** :
    - Une transition est dirigée d'un bloc source vers un bloc cible ; le chaînage est libre, y compris les cycles (par ex. Scène → Pivot → Condition → la même Scène).
    - Il ne peut exister qu'une seule transition par paire ordonnée de blocs.
    - Une transition porte une note textuelle, affichée en infobulle au survol. Elle ne porte pas de condition : la condition structurée est portée par le bloc Condition.
    - Appartenance aux parcours dérivée : une transition appartient à un parcours si et seulement si ses deux blocs y appartiennent.
    - La suppression d'une transition supprime ses rattachements aux parcours ; elle est indépendante de la suppression des blocs, hormis la cascade définie en SU003.
- **Critères d'acceptation** :
    - L'utilisateur peut initier la création d'une transition depuis le menu « Projet » ou le menu contextuel : sélection du bloc source, tracé temporaire suivant le curseur jusqu'au clic sur le port du bloc cible.
    - L'application empêche la création d'une transition en double entre deux blocs déjà reliés.
    - L'utilisateur peut annoter une transition par du texte libre via un dialogue d'édition.
    - L'utilisateur peut supprimer une transition avec confirmation préalable.
    - Toute création, modification ou suppression de transition marque la carte, donc le projet, comme modifiés.
- **Périmètre MVP** :
    - Pas de barre d'outils : actions par menu uniquement.


## SU005 : Gérer un parcours
- **Description** : En tant qu'auteur, je peux créer, nommer, décrire, dupliquer, activer ou supprimer un parcours afin de définir les fils alternatifs de mon récit.
- **Complément** :
    - Un parcours appartient à une carte narrative ; il possède un identifiant unique au sein de la carte, ainsi qu'un libellé et une note éditables.
    - Chaque carte contient toujours au moins un parcours ; à la création de la carte, un parcours initial est créé, activé et nommé par défaut.
    - Les blocs sont rattachés aux parcours ; un bloc peut appartenir à plusieurs parcours. L'appartenance d'une transition à un parcours est dérivée de ses deux blocs ; celle d'une participation ou d'une relation est dérivée de son bloc d'ancrage.
    - À la création d'un nouveau parcours, celui-ci devient automatiquement le parcours actif.
    - Tout bloc nouvellement créé est rattaché au parcours par défaut.
    - La suppression du dernier parcours d'une carte est impossible ; l'application affiche un message explicatif.
    - La séquence de lecture d'un parcours est calculée en profondeur depuis le bloc Début (elle sert à l'aperçu et à l'export).
- **Critères d'acceptation** :
    - L'utilisateur peut créer un parcours depuis le menu « Projet » ; il devient automatiquement le parcours courant.
    - L'utilisateur peut renommer un parcours et modifier sa note via un dialogue d'édition.
    - L'utilisateur peut dupliquer un parcours (nom distinctif, nouvel identifiant ; les rattachements des blocs du parcours source sont copiés).
    - L'utilisateur peut activer un parcours en le sélectionnant dans la liste des parcours ou depuis le menu « Projet ».
    - L'utilisateur peut supprimer un parcours avec confirmation préalable, sauf s'il s'agit du dernier ; si le parcours supprimé était celui par défaut, le plus ancien parcours restant le devient.
    - L'utilisateur peut modifier les parcours auxquels un bloc est rattaché, sans pouvoir le retirer de son dernier parcours.
    - Toute opération sur un parcours marque la carte, donc le projet, comme modifiés.
- **Périmètre MVP** :
    - Pas de contrôle de cohérence des parcours (impasses, branches non terminées, Pivot à une seule branche, Fin non atteinte) : fonctionnalité hors MVP.
    - Pas de barre d'outils : actions par menu uniquement.


## SU006 : Visualiser la carte narrative (vue « Parcours »)
- **Description** : En tant qu'auteur, je peux visualiser et naviguer dans l'espace de travail de la carte narrative — la vue « Parcours », graphe des blocs et de leurs transitions — afin de consulter, structurer et valider mon récit.
- **Complément** :
    - L'espace de travail est virtuellement illimité ; la navigation s'effectue au moyen de barres de défilement horizontal et vertical ; la grille d'alignement est toujours visible et active.
    - Un filtre de parcours permet d'afficher soit tous les parcours, soit un parcours sélectionné ; la visibilité suit l'appartenance dérivée (blocs du parcours, transitions dont les deux blocs appartiennent au parcours, participations et relations dont le bloc d'ancrage appartient au parcours).
    - La position des barres de défilement ne constitue pas une donnée métier et n'est pas conservée entre les sessions.
    - Le zoom est à définir durant la phase de conception.
- **Critères d'acceptation** :
    - L'application s'adapte à la taille de la fenêtre sans perte de fonctionnalité (taille minimale 1280×720).
    - L'utilisateur peut naviguer dans l'espace de travail au moyen des barres de défilement ; l'application reste stable sur un espace de 10 000×10 000 pixels et réactive (sans latence perceptible) pour une carte contenant jusqu'à 100 blocs.
    - Si le filtre de parcours est activé, l'utilisateur peut basculer d'un parcours à l'autre via la liste des parcours ou le menu « Projet » ; l'affichage se met à jour instantanément.
    - Les blocs et transitions affichés sont rendus selon leurs coordonnées et leur représentation graphique conservées.
    - Les déplacements de barres de défilement ne marquent pas la carte comme modifiée.
- **Périmètre MVP** :
    - Pas de barres d'outils.
    - Périmètre des vues non acté au-delà du minimum : vue « Parcours » et vue « Export » (SU010).
    - L'application cible exclusivement les PC sous Windows.
    - Le zoom est à définir en phase de conception.


## SU007 : Exporter la carte narrative
- **Description** : En tant qu'auteur, je peux exporter ma carte narrative sous la forme d'un document autonome en HTML, lisible dans un navigateur standard, afin de valider mon récit et de le partager avec mon équipe.
- **Complément** :
    - L'export de lecture est un document autonome : aucun serveur, aucune connexion Internet, aucune dépendance externe.
    - Il génère un dossier nommé d'après la carte narrative, contenant un fichier d'index et l'ensemble des pages nécessaires à la navigation hypertexte.
    - L'ordre de déroulement est la séquence de lecture du parcours (calculée depuis le bloc Début), indépendant des positions graphiques.
    - Restitution par bloc : libellé en titre de paragraphe et contenu en corps de texte (libellé seul si le contenu est vide) ; les transitions sont rendues en ligne ; les conditions sont rendues sur leur branche ; les relations entre agents sont listées sous leur bloc d'ancrage ; une section finale récapitule l'état des relations (dernier type connu par paire d'agents dans le parcours).
    - Chaque page de déroulement propose un lien de retour vers le sommaire.
    - L'opération d'export ne marque ni la carte ni le projet comme modifiés.
- **Critères d'acceptation** :
    - L'utilisateur peut lancer l'export depuis le menu « Fichier ».
    - Le document généré s'affiche correctement dans les navigateurs standards (Chrome, Firefox, Edge) sans connexion Internet.
    - Une page intermédiaire liste les parcours de la carte ; le clic sur un parcours affiche le déroulement linéaire complet de sa séquence.
- **Périmètre MVP** :
    - L'export sur fichier est **hors périmètre MVP** (entrée « Files › Export Map » grisée) ; dans le MVP, seul l'aperçu in-app (vue « Export », SU010/FN033) est disponible.
    - Le périmètre exact de l'export de lecture (pages, modes de lecture) sera précisé ultérieurement pour la version post-MVP.
    - L'export technique pour réimport et la lecture « par événements » sont à définir durant la phase de conception.


## SU008 : Gérer les participations agent-bloc
- **Description** : En tant qu'auteur, je peux associer un agent à un ou plusieurs blocs, et réciproquement associer un bloc à un ou plusieurs agents, afin de définir qui intervient à chaque étape de mon récit.
- **Complément** :
    - Un agent est un élément du projet, de type Personnage ou Artefact. Un bloc appartient à une carte narrative. La participation relie un agent à un bloc.
    - La participation est non orientée ; il ne peut en exister qu'une seule par couple (agent, bloc).
    - Appartenance aux parcours dérivée : une participation appartient à un parcours si et seulement si son bloc y appartient.
    - Deux points d'entrée persistants : le menu contextuel d'un bloc dans la vue « Parcours » (« Associer des agents... ») et la matrice de la vue agents (SU009, initialisée) — cocher associe, décocher dissocie ; les deux points d'entrée modifient la même donnée et se répercutent immédiatement l'un sur l'autre.
    - Les agents participants d'un bloc sont représentés par des badges affichés sur le bloc dans la vue « Parcours ».
    - La suppression d'un agent ou d'un bloc entraîne la suppression en cascade de ses participations.
- **Critères d'acceptation** :
    - L'utilisateur peut associer un agent à un bloc depuis le menu contextuel du bloc dans la vue « Parcours », ou depuis la vue agents ; il peut dissocier depuis l'un ou l'autre point d'entrée.
    - L'utilisateur peut créer un nouvel agent depuis le dialogue d'association et l'associer immédiatement au bloc courant.
    - L'application empêche la création d'une participation en double entre un agent et un bloc.
    - Les participations modifiées depuis une vue sont immédiatement visibles dans l'autre.
    - Tout agent participant à au moins un bloc est visible sous forme de badge sur ce bloc dans la vue « Parcours ».
    - Toute association, dissociation ou création d'agent marque la carte, donc le projet, comme modifiés.
- **Périmètre MVP** :
    - Les participations font partie du MVP.
    - La note portée par une participation n'est pas éditable dans le MVP.


## SU009 : Gérer la vue agents — initialisé, à finaliser après la phase de conception
- **Description** : En tant qu'auteur, je peux visualiser et éditer les participations entre les agents du projet et les blocs de la carte narrative dans un second espace de travail, afin de gérer les agents indépendamment du graphe des blocs.
- **Statut** : scenario initialisé — à finaliser après la phase de conception. Le périmètre MVP des vues n'est pas encore acté (au minimum : vue « Parcours » et vue « Export »).
- **Éléments à préciser en conception** : ordre des colonnes (le bloc Début en premier), réordonnancement manuel conservé entre les sessions, navigation croisée entre les vues « Parcours » et agents.


## SU010 : Visualiser l'aperçu d'export — initialisé, à finaliser après la phase de conception
- **Description** : En tant qu'auteur, je peux visualiser dans l'application un aperçu de lecture de ma carte narrative, tel qu'il sera restitué à l'export (espace de travail « Export »), afin de valider mon récit avant de le partager.
- **Statut** : scenario initialisé — à finaliser après la phase de conception. La vue « Export » fait partie du périmètre MVP minimal et pourra être renommée ultérieurement.
- **Éléments à préciser en conception** : lecture seule et liens inertes, dynamisme selon le filtre de parcours, ordre de restitution (séquence de lecture), restitution des relations sous leur bloc d'ancrage et de la section « état des relations », composants orphelins éventuels.


## SU011 : Gérer une relation entre agents
- **Description** : En tant qu'auteur, je peux créer, annoter, modifier ou supprimer une relation typée entre deux agents, ancrée à un bloc, afin de suivre l'évolution des relations entre personnages ou artefacts au fil de mon récit.
- **Complément** :
    - Une relation est binaire : elle relie exactement deux agents. Une évolution vers des relations à plus de deux agents est hors MVP.
    - Elle est dirigée et typée ; le type est lu dans une liste de valeurs définie dans un fichier de configuration (l'enrichissement de cette liste par l'auteur est hors MVP).
    - Elle est ancrée à un bloc : « à ce moment du récit, la relation A —type→ B est vraie ».
    - Il ne peut exister qu'une seule relation par couple (bloc, paire d'agents, type).
    - L'historique d'une paire d'agents est l'ensemble de ses relations ancrées, ordonnées selon la position de leur bloc dans le parcours ; l'état courant de la paire à un bloc est la dernière relation ancrée à un bloc situé avant ou au même rang dans ce parcours (donnée dérivée, jamais stockée).
    - Appartenance aux parcours dérivée : une relation appartient à un parcours si et seulement si son bloc d'ancrage y appartient.
    - La suppression d'un agent ou d'un bloc entraîne la suppression en cascade de ses relations.
- **Critères d'acceptation** :
    - L'utilisateur peut créer une relation depuis le menu « Projet » ou le menu contextuel : choix des deux agents, du type (dans la liste configurée) et du bloc d'ancrage.
    - L'utilisateur peut modifier une relation (type, bloc d'ancrage, note, contenu) via un dialogue d'édition.
    - L'utilisateur peut supprimer une relation avec confirmation préalable.
    - L'application empêche les doublons (bloc, paire d'agents, type).
    - Toute création, modification ou suppression de relation marque la carte, donc le projet, comme modifiés.
- **Périmètre MVP** :
    - Les relations agent-agent font partie du MVP (modèle + liste de types en configuration).
    - La vue dédiée (SU012) est initialisée séparément.


## SU012 : Gérer la vue « Relations » — initialisée, à finaliser après la phase de conception
- **Description** : En tant qu'auteur, je peux visualiser le graphe des agents et de leurs relations (arcs étiquetés par type, annotés des blocs d'ancrage) dans un espace de travail dédié, avec navigation croisée vers le bloc d'ancrage dans la vue « Parcours ».
- **Statut** : scenario initialisé — la maquette de cette vue sera définie durant la phase de conception.
