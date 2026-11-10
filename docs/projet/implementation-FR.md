# Hyperscript ::: Matrice de traçabilité de l'implémentation


- **Date de dernière modification** : 10-11-2026
- **Description** : état et localisation de l'implémentation des règles de gestion (RG), des fonctionnalités (FN), des entrées du menu général et des scenarii d'utilisation (SU) dans la base de code.


## Conventions

- **Statuts** : `not-started` (spécifié, aucun code) ; `stub` (entrée de menu stubbée, action vide) ; `greyed-MVP` (présente mais grisée en MVP) ; `partial` (implémentation partielle) ; `implemented` (implémenté, test passant) ; `post-MVP` (hors périmètre MVP).
- **Liens bidirectionnels** : chaque RG/FN implémentée porte son identifiant en commentaire dans le code (`# RG040: …`, `# FN023: …` — pratique planoscript) ; tests unitaires nommés `test_rgXXX_*.py` ; tests d'application `test_fnXXX_*.py` (pywinauto, skippés sans session GUI), spécifiés par leur ID `T-xxx` dans `tests/SPECIFICATION.md`.
- Cette matrice est l'index lisible de ces liens ; les identifiants (RG/FN/SU/T) sont des ancres stables, vérifiables par grep dans `src/` et `tests/`.
- **Mise à jour** : à chaque passage de tâche kanban en Review puis Done ; une ligne ne passe `implemented` que si le commentaire d'ID est présent dans le code et que le test associé existe et passe.
- **État initial** (phase spécifications, aucun code) : toutes les lignes sont `not-started`, sauf les entrées grisées en MVP (`greyed-MVP`) signalées dans `05_menu` et `03_features`.

---

## A. Règles de gestion (`02_business_rules-*.md`)


### 1. Gestion du projet et cycle de vie

| RG | Résumé | Statut | Code (fichier · symbole) | Test unitaire | Notes |
|---|---|---|---|---|---|
| RG001 | Un projet est un document local (format JSON) contenant ses métadonnées, ses… | not-started | — | — | — |
| RG002 | Un seul projet peut être ouvert dans l'application à tout moment. | not-started | — | — | — |
| RG003 | Un projet nouvellement créé est un projet non enregistré : il existe en mémoire… | not-started | — | — | — |
| RG004 | Chaque projet possède un identifiant stable, un nom, une date de création, une… | not-started | — | — | — |
| RG005 | Les projets enregistrés ou ouverts avec succès sont ajoutés à la liste des… | not-started | — | — | — |
| RG006 | La commande « Save » n'est active que si le projet ouvert est modifié ; « Save… | not-started | — | — | — |
| RG007 | Lorsqu'aucun projet n'est ouvert, les entrées des menus Files (Close, Save,… | not-started | — | — | — |
| RG008 | À l'ouverture ou à la création d'un projet, les entrées des menus Files (Close,… | not-started | — | — | — |
| RG009 | L'ouverture d'un projet ne remplace le projet courant qu'après lecture et… | not-started | — | — | — |
| RG010 | L'application n'ouvre un projet que si sa version de format est supportée ;… | not-started | — | — | — |
| RG011 | Une sauvegarde ne remplace le fichier existant qu'après écriture complète et… | not-started | — | — | — |
| RG012 | « Save as... » crée ou remplace un fichier à l'emplacement choisi (avec… | not-started | — | — | — |
| RG013 | Un nouveau projet est nommé « Nouveau projet » et contient une carte narrative… | not-started | — | — | — |
| RG014 | Un projet contient toujours au moins une carte narrative (en MVP : exactement… | not-started | — | — | — |
| RG015 | Une seule instance de l'application peut tourner à la fois ; si une instance… | not-started | — | — | — |
| RG016 | Aucun projet planoscript existant n'est migré : les fichiers planoscript sont… | not-started | — | — | — |
| RG017 | L'export sur fichier est hors périmètre MVP (seul l'aperçu in-app, vue « Export… | not-started | — | — | — |

### 2. Structure de la carte narrative

| RG | Résumé | Statut | Code (fichier · symbole) | Test unitaire | Notes |
|---|---|---|---|---|---|
| RG018 | Chaque carte narrative possède un identifiant stable. | not-started | — | — | — |
| RG019 | Chaque bloc, transition, participation, relation, parcours et rattachement d'un… | not-started | — | — | — |
| RG020 | Les libellés des blocs, transitions, participations, relations, parcours et… | not-started | — | — | — |
| RG021 | Une carte narrative contient toujours au moins un parcours. | not-started | — | — | — |
| RG022 | La suppression d'une carte narrative est irréversible et entraîne la… | not-started | — | — | — |
| RG023 | La suppression d'un bloc entraîne la suppression en cascade de ses transitions,… | not-started | — | — | — |
| RG024 | La suppression du dernier parcours d'une carte est impossible. | not-started | — | — | — |
| RG025 | Chaque carte narrative possède un et un seul bloc Début, créé automatiquement à… | not-started | — | — | — |
| RG026 | Un bloc Fin ne peut recevoir aucune transition sortante (degré sortant 0). En… | not-started | — | — | — |
| RG027 | Un bloc peut avoir plusieurs transitions entrantes et plusieurs transitions… | not-started | — | — | — |
| RG028 | Le chaînage par transition est libre (de tout bloc vers tout bloc, cycles… | not-started | — | — | — |
| RG029 | Le type d'un bloc est choisi à sa création et immuable ensuite. | not-started | — | — | — |
| RG030 | Un bloc Pivot possède au moins deux transitions sortantes ; la promotion Scène… | not-started | — | — | Règle sujette à révision en cours de conception si le besoin apparaît. |
| RG031 | Un bloc Condition possède exactement une transition entrante (depuis un Pivot)… | not-started | — | — | Règle sujette à révision en cours de conception si le besoin apparaît. |
| RG032 | Il ne peut exister qu'une seule participation par couple (bloc, agent). | not-started | — | — | — |
| RG033 | La suppression d'un agent entraîne la suppression en cascade de toutes ses… | not-started | — | — | — |
| RG034 | La suppression d'un parcours réaffecte au parcours par défaut les rattachements… | not-started | — | — | — |
| RG035 | Une relation est binaire (exactement deux agents), dirigée et typée, et ancrée… | not-started | — | — | — |
| RG036 | Dans la vue « Agents », les colonnes (blocs) sont ordonnées par défaut par… | not-started | — | — | À re-concevoir avec la vue « Agents ». |

### 3. Logique des parcours et appartenance

| RG | Résumé | Statut | Code (fichier · symbole) | Test unitaire | Notes |
|---|---|---|---|---|---|
| RG037 | À la création d'une carte narrative, un parcours par défaut est automatiquement… | not-started | — | — | — |
| RG038 | La copie d'un parcours ne modifie pas le parcours activé quanf le filtre de… | not-started | — | — | — |
| RG039 | Il existe toujours un parcours par défaut, et un seul ; si le parcours par… | not-started | — | — | — |
| RG040 | Aucun bloc orphelin : tout bloc appartient à au moins un parcours ; à sa… | not-started | — | — | — |
| RG041 | L'appartenance à un parcours est dérivée et jamais stockée : une transition… | not-started | — | — | — |
| RG042 | Les parcours auxquels un bloc est rattaché se modifient via la liste des… | not-started | — | — | — |
| RG043 | La copie d'un parcours reprend les rattachements de ses blocs. | not-started | — | — | — |
| RG044 | La séquence de lecture d'un parcours est calculée en profondeur depuis le bloc… | not-started | — | — | — |

### 4. Visualisation et interaction

| RG | Résumé | Statut | Code (fichier · symbole) | Test unitaire | Notes |
|---|---|---|---|---|---|
| RG045 | La position (x, y) de chaque bloc est conservée dans les métadonnées graphiques… | not-started | — | — | — |
| RG046 | Les blocs s'alignent automatiquement sur la grille lors de leur création et de… | not-started | — | — | — |
| RG047 | La modification du niveau de zoom, de la position des barres de défilement ou… | not-started | — | — | — |
| RG048 | Le filtre de parcours affiche soit tous les parcours, soit un seul, dans toutes… | not-started | — | — | — |
| RG049 | Dans un espace de travail, un seul élément est sélectionné à la fois ; la… | not-started | — | — | — |
| RG050 | Un bloc ne peut pas être créé à des coordonnées chevauchant celles d'un bloc… | not-started | — | — | — |
| RG051 | Lorsqu'un bloc déplacé dépasse la partie visible de l'espace de travail, le… | not-started | — | — | — |
| RG052 | Le tracé d'une transition ne doit jamais chevaucher un bloc qui n'en est ni la… | not-started | — | — | — |
| RG053 | La zone cliquable d'un élément graphique (bloc, transition) est définie par sa… | not-started | — | — | — |
| RG054 | Les notes des blocs et des transitions s'affichent en infobulle dès le survol,… | not-started | — | — | — |
| RG055 | À l'ouverture d'un menu contextuel, l'élément situé sous le curseur est d'abord… | not-started | — | — | — |
| RG056 | Le focus de navigation croisée entre les vues (y compris la vue « Relations »)… | not-started | — | — | — |

### 5. Architecture technique et modèle de données

| RG | Résumé | Statut | Code (fichier · symbole) | Test unitaire | Notes |
|---|---|---|---|---|---|
| RG057 | Les agents appartiennent au projet, et non à la carte narrative. | not-started | — | — | — |
| RG058 | L'interface ne modifie jamais directement le modèle métier : toute modification… | not-started | — | — | — |
| RG059 | Aucune valeur n'est codée en dur dans l'interface : dimensions, couleurs,… | not-started | — | — | — |
| RG060 | Les métadonnées de représentation graphique (positions des blocs, ordre des… | not-started | — | — | — |
| RG061 | Le projet est enregistré dans un fichier unique structuré (JSON) contenant les… | not-started | — | — | — |
| RG062 | L'auteur peut à tout moment désigner l'un des parcours de la carte comme… | not-started | — | — | — |

## B. Fonctionnalités (`03_features-*.md`)


### Hyperscript ::: Fonctionnalités

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
|---|---|---|---|---|---|---|---|

### Application

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
|---|---|---|---|---|---|---|---|
| FN001 | Lancer l'application | not-started | — | — | — | — | — |
| FN002 | Quitter l'application | not-started | Files › Quit | — | — | — | — |
| FN003 | Afficher l'historique des changements | not-started | About › Change Log | — | — | — | — |
| FN004 | Afficher l'information « à propos » | not-started | About › About Hyperscript | — | — | — | — |

### Projet

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
|---|---|---|---|---|---|---|---|
| FN005 | Créer un nouveau projet | not-started | Files › New Project... | — | — | — | — |
| FN006 | Ouvrir un projet | not-started | Files › Open... | — | — | — | — |
| FN007 | Ouvrir un projet récent | greyed-MVP | Files › Recent Projects | — | — | — | — |
| FN008 | Enregistrer le projet | not-started | Files › Save | — | — | — | — |
| FN009 | Enregistrer le projet sous... | not-started | Files › Save as... | — | — | — | — |
| FN010 | Fermer le projet | not-started | Files › Close | — | — | — | — |
| FN011 | Modifier le libellé du projet | not-started | — | — | — | — | — |

### Carte narrative

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
|---|---|---|---|---|---|---|---|
| FN012 | Renommer la carte narrative | not-started | — | — | — | — | — |
| FN013 | Exporter la carte narrative en document de lecture | greyed-MVP | Files › Export Map... | — | — | — | — |

### Blocs narratifs

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
|---|---|---|---|---|---|---|---|
| FN014 | Créer un bloc narratif | not-started | Project › Narrative Blocks › New | — | — | — | — |
| FN015 | Modifier les attributs d'un bloc | not-started | Project › Narrative Blocks › Edit... | — | — | — | — |
| FN016 | Dupliquer un bloc | not-started | — | — | — | — | — |
| FN017 | Déplacer un bloc | not-started | — | — | — | — | — |
| FN018 | Supprimer un bloc | not-started | Project › Narrative Blocks › Delete... | — | — | — | — |
| FN019 | Gérer le rattachement d'un bloc aux parcours | not-started | — | — | — | — | — |

### Transitions

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
|---|---|---|---|---|---|---|---|
| FN020 | Créer une transition | not-started | Project › Transitions › New | — | — | — | — |
| FN021 | Annoter et modifier une transition | not-started | Project › Transitions › Edit... | — | — | — | — |
| FN022 | Supprimer une transition | not-started | Project › Transitions › Delete... | — | — | — | — |

### Parcours

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
|---|---|---|---|---|---|---|---|
| FN023 | Créer un parcours | not-started | Project › Journeys › New | — | — | — | — |
| FN024 | Renommer et décrire un parcours | not-started | — | — | — | — | — |
| FN025 | Dupliquer un parcours | not-started | — | — | — | — | — |
| FN026 | Activer un parcours | not-started | — | — | — | — | — |
| FN027 | Supprimer un parcours | not-started | — | — | — | — | — |
| FN038 | Définir le parcours par défaut | not-started | Project › Journeys › Set as Default... | — | — | — | — |

### Visualisation

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
|---|---|---|---|---|---|---|---|
| FN028 | Naviguer dans l'espace de travail | not-started | — | — | — | — | — |
| FN029 | Filtrer l'affichage par parcours | not-started | — | — | — | — | — |

### Agents et participations

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
|---|---|---|---|---|---|---|---|
| FN030 | Associer des agents à un bloc | not-started | — | — | — | — | — |
| FN031 | Gérer les agents du projet | not-started | Project › Agents | — | — | — | — |
| FN032 | Naviguer entre les vues (navigation croisée) | not-started | — | — | — | — | — |
| FN033 | Aperçu d'export (espace de travail « Export ») | not-started | — | — | — | — | — |

### Relations entre agents

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
|---|---|---|---|---|---|---|---|
| FN034 | Gérer une relation entre agents | not-started | Project › Relationships | — | — | — | — |

### Conditions

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
|---|---|---|---|---|---|---|---|
| FN035 | Gérer la condition d'un bloc Condition et la promotion Scène → Pivot | not-started | — | — | — | — | — |

### Vue « Relations »

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
|---|---|---|---|---|---|---|---|
| FN036 | Vue « Relations » | not-started | — | — | — | — | — |

### Configuration

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
|---|---|---|---|---|---|---|---|
| FN037 | Liste des types de relations | not-started | — | — | — | — | — |

### Hors périmètre MVP / à définir en phase de conception

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
|---|---|---|---|---|---|---|---|

## C. Entrées du menu général (`05_menu-*.yaml`)

| Chemin | Libellé | Raccourci | Statut | Clé `main_window.py` |
|---|---|---|---|---|
| Fichiers | Fichiers |  | not-started | — |
| Fichiers › Nouveau projet... | Nouveau projet... | Ctrl+N | not-started | — |
| Fichiers › Ouvrir... | Ouvrir... | Ctrl+O | not-started | — |
| Fichiers › Fermer | Fermer | Ctrl+W | not-started | — |
| Fichiers › Enregistrer | Enregistrer | Ctrl+S | not-started | — |
| Fichiers › Enregistrer sous... | Enregistrer sous... | Ctrl+Shift+S | not-started | — |
| Fichiers › Exporter la carte... | Exporter la carte... |  | greyed-MVP | — |
| Fichiers › Importer une carte... | Importer une carte... |  | greyed-MVP | — |
| Fichiers › Projets récents | Projets récents |  | greyed-MVP | — |
| Fichiers › Quitter | Quitter | Ctrl+Q | not-started | — |
| Édition | Édition |  | greyed-MVP | — |
| Édition › Annuler | Annuler | Ctrl+Z | greyed-MVP | — |
| Édition › Rétablir | Rétablir | Ctrl+Y | greyed-MVP | — |
| Édition › Couper | Couper | Ctrl+X | greyed-MVP | — |
| Édition › Copier | Copier | Ctrl+C | greyed-MVP | — |
| Édition › Coller | Coller | Ctrl+V | greyed-MVP | — |
| Affichage | Affichage |  | not-started | — |
| Affichage › Parcours | Parcours |  | not-started | — |
| Affichage › Zoom | Zoom |  | not-started | — |
| Affichage › Zoom › Avant | Avant | Ctrl+= | greyed-MVP | — |
| Affichage › Zoom › Arrière | Arrière | Ctrl+- | greyed-MVP | — |
| Affichage › Zoom › Réinitialiser | Réinitialiser | Ctrl+0 | greyed-MVP | — |
| Projet | Projet |  | not-started | — |
| Projet › Vue | Vue |  | not-started | — |
| Projet › Vue › Parcours | Parcours |  | not-started | — |
| Projet › Vue › Agents | Agents |  | not-started | — |
| Projet › Vue › Relations | Relations |  | not-started | — |
| Projet › Vue › Export | Export |  | not-started | — |
| Projet › Agents | Agents |  | not-started | — |
| Projet › Agents › Nouveau... | Nouveau... |  | not-started | — |
| Projet › Agents › Éditer... | Éditer... |  | not-started | — |
| Projet › Agents › Copier | Copier |  | not-started | — |
| Projet › Agents › Supprimer... | Supprimer... |  | not-started | — |
| Projet › Agents › Associer à un bloc... | Associer à un bloc... |  | not-started | — |
| Projet › Blocs narratifs | Blocs narratifs |  | not-started | — |
| Projet › Blocs narratifs › Nouveau | Nouveau |  | not-started | — |
| Projet › Blocs narratifs › Nouveau › Scène | Scène |  | not-started | — |
| Projet › Blocs narratifs › Nouveau › Pivot | Pivot |  | not-started | — |
| Projet › Blocs narratifs › Nouveau › Condition | Condition |  | not-started | — |
| Projet › Blocs narratifs › Nouveau › Fin | Fin |  | not-started | — |
| Projet › Blocs narratifs › Éditer... | Éditer... |  | not-started | — |
| Projet › Blocs narratifs › Copier | Copier |  | not-started | — |
| Projet › Blocs narratifs › Supprimer... | Supprimer... |  | not-started | — |
| Projet › Transitions | Transitions |  | not-started | — |
| Projet › Transitions › Nouvelle | Nouvelle |  | not-started | — |
| Projet › Transitions › Éditer... | Éditer... |  | not-started | — |
| Projet › Transitions › Supprimer... | Supprimer... |  | not-started | — |
| Projet › Parcours | Parcours |  | not-started | — |
| Projet › Parcours › Nouveau | Nouveau |  | not-started | — |
| Projet › Parcours › Éditer... | Éditer... |  | not-started | — |
| Projet › Parcours › Copier | Copier |  | not-started | — |
| Projet › Parcours › Définir par défaut... | Définir par défaut... |  | not-started | — |
| Projet › Parcours › Supprimer... | Supprimer... |  | not-started | — |
| Projet › Relations | Relations |  | not-started | — |
| Projet › Relations › Nouvelle... | Nouvelle... |  | not-started | — |
| Projet › Relations › Éditer... | Éditer... |  | not-started | — |
| Projet › Relations › Supprimer... | Supprimer... |  | not-started | — |
| À propos | À propos |  | not-started | — |
| À propos › Historique des changements | Historique des changements |  | not-started | — |
| À propos › À propos d'Hyperscript | À propos d'Hyperscript |  | not-started | — |

## D. Scénarios d'utilisation (`01_user_stories-*.md`)

| SU | Titre | FN couvertes | Statut agrégé |
|---|---|---|---|
| SU001 | Gérer un projet narratif | FN001, FN002, FN005, FN006, FN007, FN008, FN009, FN010, FN011 | not-started |
| SU002 | Gérer une carte narrative | FN012, FN013 | not-started |
| SU003 | Gérer un bloc narratif | FN014, FN015, FN016, FN017, FN018, FN019, FN035 | not-started |
| SU004 | Gérer une transition entre blocs | FN020, FN021, FN022, FN035 | not-started |
| SU005 | Gérer un parcours | FN019, FN023, FN024, FN025, FN026, FN027, FN038 | not-started |
| SU006 | Visualiser la carte narrative (vue « Parcours ») | FN017, FN028, FN029 | not-started |
| SU007 | Exporter la carte narrative | FN013, FN033 | not-started |
| SU008 | Gérer les participations agent-bloc | FN030, FN031 | not-started |
| SU009 | Gérer la vue agents — initialisé, à finaliser après la phase de conception | FN031, FN032 | not-started |
| SU010 | Visualiser l'aperçu d'export — initialisé, à finaliser après la phase de conception | FN033 | not-started |
| SU011 | Gérer une relation entre agents | FN034, FN037 | not-started |
| SU012 | Gérer la vue « Relations » — initialisée, à finaliser après la phase de conception | FN032, FN036 | not-started |
