# Hyperscript ::: Matrice de traçabilité de l'implémentation


- **Date de dernière modification** : 11-11-2026
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
| --- | --- | --- | --- | --- | --- |
| RG001 | Un projet est un document local (format JSON) contenant ses métadonnées, ses… | not-started | — | — | — |
| RG002 | Un seul projet peut être ouvert dans l'application à tout moment. | not-started | — | — | — |
| RG003 | Un projet nouvellement créé est un projet non enregistré : il existe en mémoire… | implemented | src/core/services/project_service.py · ProjectService.create_project | tests/test_project/test_project_service.py | projet non enregistré (pas de fichier associé) |
| RG004 | Chaque projet possède un identifiant stable, un nom, une date de création, une… | not-started | — | — | — |
| RG005 | Les projets enregistrés ou ouverts avec succès sont ajoutés à la liste des… | not-started | — | — | — |
| RG006 | La commande « Save » n'est active que si le projet ouvert est modifié ; « Save… | not-started | — | — | — |
| RG007 | Lorsqu'aucun projet n'est ouvert, les entrées des menus Files (Close, Save,… | not-started | — | — | — |
| RG008 | À l'ouverture ou à la création d'un projet, les entrées des menus Files (Close,… | not-started | — | — | — |
| RG009 | L'ouverture d'un projet ne remplace le projet courant qu'après lecture et… | implemented | src/core/services/project_service.py · load_project | tests/test_project/test_project_service.py | fichier invalide/incompatible : projet courant inchangé |
| RG010 | L'application n'ouvre un projet que si sa version de format est supportée ;… | implemented | src/core/services/project_service.py · load_project (format_version) | tests/test_project/test_project_service.py | — |
| RG011 | Une sauvegarde ne remplace le fichier existant qu'après écriture complète et… | not-started | — | — | — |
| RG012 | « Save as... » crée ou remplace un fichier à l'emplacement choisi (avec… | not-started | — | — | — |
| RG013 | Un nouveau projet est nommé « Nouveau projet » et contient une carte narrative… | implemented | project_service.py · create_project + usecases/project_management/create_project_usecase.py | tests/test_project/test_project_service.py | — |
| RG014 | Un projet contient toujours au moins une carte narrative (en MVP : exactement… | not-started | — | — | — |
| RG015 | Une seule instance de l'application peut tourner à la fois ; si une instance… | not-started | — | — | — |
| RG016 | Aucun projet planoscript existant n'est migré : les fichiers planoscript sont… | implemented | project_service.py · load_project (rejet si format_version absent) | tests/test_project/test_project_service.py | fichiers planoscript = incompatibles |
| RG017 | L'export sur fichier est hors périmètre MVP (seul l'aperçu in-app, vue « Export… | not-started | — | — | — |

### 2. Structure de la carte narrative

| RG | Résumé | Statut | Code (fichier · symbole) | Test unitaire | Notes |
| --- | --- | --- | --- | --- | --- |
| RG018 | Chaque carte narrative possède un identifiant stable. | not-started | — | — | — |
| RG019 | Chaque bloc, transition, participation, relation, parcours et rattachement d'un… | not-started | — | — | — |
| RG020 | Les libellés des blocs, transitions, participations, relations, parcours et… | not-started | — | — | — |
| RG021 | Une carte narrative contient toujours au moins un parcours. | not-started | — | — | — |
| RG022 | La suppression d'une carte narrative est irréversible et entraîne la… | not-started | — | — | — |
| RG023 | La suppression d'un bloc entraîne la suppression en cascade de ses transitions,… | implemented | core/services/transition_service.py (delete_block_cascade) | tests/test_transitions/test_transition_service.py | cascade testée |
| RG024 | La suppression du dernier parcours d'une carte est impossible. | implemented | usecases/journey_management/delete_journey_usecase.py | tests/test_journeys/test_journey_usecases.py | dernier parcours refusé (message UI) |
| RG025 | Chaque carte narrative possède un et un seul bloc Début, créé automatiquement à… | implemented | usecases/project_management/create_project_usecase.py; usecases/view_management/ (delete/duplicate) | tests/test_project/test_project_service.py; tests/test_blocks/test_block_usecases.py | Start jamais supprimable ni duplicable |
| RG026 | Un bloc Fin ne peut recevoir aucune transition sortante (degré sortant 0). En… | implemented | core/services/transition_service.py (matrice : Fin → aucune cible) | tests/test_transitions/test_transition_service.py | via la matrice RG028 |
| RG027 | Un bloc peut avoir plusieurs transitions entrantes et plusieurs transitions… | implemented | core/services/transition_service.py | tests/test_transitions/test_transition_service.py | 0..n dans les limites de la matrice RG028 |
| RG028 | Le chaînage est contraint par la matrice des types de blocs autorisés (Début→Scène/Pivot ; Scène→Scène/Pivot/Fin ; Pivot→Condition ; Condition→Scène/Fin ; Fin→aucune), cycles… | implemented | core/services/transition_service.py (ALLOWED_TARGET_TYPES) | tests/test_transitions/test_transition_service.py | matrice actée séance 03 ; cycles autorisés ; unicité paire ordonnée |
| RG029 | Le type d'un bloc est choisi à sa création et immuable ensuite. | implemented | core/models/data_model.py (Block.__post_init__); usecases/view_management/update_block_usecase.py | tests/test_blocks/test_block_usecases.py | type non modifiable à l'édition |
| RG030 | Un bloc Pivot : entrantes depuis Début/Scène uniquement, sortantes vers Condition… | implemented | core/services/transition_service.py (matrice) | tests/test_transitions/test_transition_service.py | révisée séance 03 : promotion Scène→Pivot supprimée |
| RG031 | Un bloc Condition : entrantes depuis Pivot uniquement, sortantes vers Scène/Fin… | implemented | core/services/transition_service.py (matrice); core/models/data_model.py (condition) | tests/test_transitions/; tests/test_blocks/ | révisée séance 03 : ET non exprimable, OU conservé |
| RG032 | Il ne peut exister qu'une seule participation par couple (bloc, agent). | not-started | — | — | — |
| RG033 | La suppression d'un agent entraîne la suppression en cascade de toutes ses… | not-started | — | — | — |
| RG034 | La suppression d'un parcours réaffecte au parcours par défaut les rattachements… | implemented | usecases/journey_management/delete_journey_usecase.py | tests/test_journeys/test_journey_usecases.py | réaffectation au parcours par défaut (aucun bloc orphelin) |
| RG035 | Une relation est binaire (exactement deux agents), dirigée et typée, et ancrée… | not-started | — | — | — |
| RG036 | Dans la vue « Agents », les colonnes (blocs) sont ordonnées par défaut par… | not-started | — | — | À re-concevoir avec la vue « Agents ». |

### 3. Logique des parcours et appartenance

| RG | Résumé | Statut | Code (fichier · symbole) | Test unitaire | Notes |
| --- | --- | --- | --- | --- | --- |
| RG037 | À la création d'une carte narrative, un parcours par défaut est automatiquement… | implemented | usecases/project_management/create_project_usecase.py | tests/test_project/test_project_service.py | parcours par défaut créé et activé |
| RG038 | La copie d'un parcours ne modifie pas le parcours activé quanf le filtre de… | implemented | usecases/journey_management/duplicate_journey_usecase.py | tests/test_journeys/test_journey_usecases.py | copie non activée |
| RG039 | Il existe toujours un parcours par défaut, et un seul ; si le parcours par… | implemented | core/services/journey_service.py; delete/set_default use cases | tests/test_journeys/test_journey_usecases.py | un seul default ; repli default/actif à la suppression |
| RG040 | Aucun bloc orphelin : tout bloc appartient à au moins un parcours ; à sa… | implemented | core/services/journey_service.py (attach_new_block); create/duplicate block use cases | tests/test_blocks/test_block_usecases.py | parcours actif si filtre activé, défaut sinon |
| RG041 | L'appartenance à un parcours est dérivée et jamais stockée : une transition… | implemented | core/services/journey_filter_service.py; core/services/journey_sequence_service.py | tests/test_journeys/test_journey_filter_service.py; test_journey_sequence_service.py | appartenance dérivée (jamais stockée) |
| RG042 | Les parcours auxquels un bloc est rattaché se modifient via la liste des… | not-started | — | — | — |
| RG043 | La copie d'un parcours reprend les rattachements de ses blocs. | implemented | usecases/journey_management/duplicate_journey_usecase.py | tests/test_journeys/test_journey_usecases.py | rattachements des blocs copiés |
| RG044 | La séquence de lecture d'un parcours est calculée en profondeur depuis le bloc… | implemented | core/services/journey_sequence_service.py | tests/test_journeys/test_journey_sequence_service.py | DFS depuis Start, branches par id de transition croissant, cycles mémoïsés, repli déterministe |

### 4. Visualisation et interaction

| RG | Résumé | Statut | Code (fichier · symbole) | Test unitaire | Notes |
| --- | --- | --- | --- | --- | --- |
| RG045 | La position (x, y) de chaque bloc est conservée dans les métadonnées graphiques… | not-started | — | — | — |
| RG046 | Les blocs s'alignent automatiquement sur la grille lors de leur création et de… | partial | core/services/layout_service.py (snap_to_grid); ui/nodes/base_node.py (itemChange) | — | test offscreen à valider sur poste de dev (libGL absent dans le sandbox) |
| RG047 | La modification du niveau de zoom, de la position des barres de défilement ou… | not-started | — | — | — |
| RG048 | Le filtre de parcours affiche soit tous les parcours, soit un seul, dans toutes… | partial | core/services/journey_filter_service.py; ui/views/journeys_workspace.py; ui/main_window.py | tests/test_journeys/test_journey_filter_service.py | service testé (opacité config journey_filter_opacity) ; rendu visuel (opacité 0.25 + désactivation) à valider offscreen |
| RG049 | Dans un espace de travail, un seul élément est sélectionné à la fois ; la… | partial | ui/views/journeys_workspace.py (_select_item_only, _clear_all_selections) | — | test offscreen à valider |
| RG050 | Un bloc ne peut pas être créé à des coordonnées chevauchant celles d'un bloc… | partial | core/services/layout_service.py (find_non_overlapping_position); ui/views/journeys_workspace.py (next_free_position) | — | test offscreen à valider |
| RG051 | Lorsqu'un bloc déplacé dépasse la partie visible de l'espace de travail, le… | not-started | — | — | — |
| RG052 | Le tracé d'une transition ne doit jamais chevaucher un bloc qui n'en est ni la… | not-started | — | — | — |
| RG053 | La zone cliquable d'un élément graphique (bloc, transition) est définie par sa… | partial | ui/nodes/base_node.py; ui/nodes/connection.py (shape()/boundingRect élargis) | — | test offscreen à valider |
| RG054 | Les notes des blocs et des transitions s'affichent en infobulle dès le survol,… | partial | ui/nodes/base_node.py; ui/nodes/connection.py (hoverEnterEvent → QToolTip.showText immédiat) | — | test offscreen à valider |
| RG055 | À l'ouverture d'un menu contextuel, l'élément situé sous le curseur est d'abord… | partial | ui/views/journeys_workspace.py; ui/main_window.py (_show_workspace_context_menu construit depuis les QAction du menu général) | — | test offscreen à valider |
| RG056 | Le focus de navigation croisée entre les vues (y compris la vue « Relations »)… | not-started | — | — | — |

### 5. Architecture technique et modèle de données

| RG | Résumé | Statut | Code (fichier · symbole) | Test unitaire | Notes |
| --- | --- | --- | --- | --- | --- |
| RG057 | Les agents appartiennent au projet, et non à la carte narrative. | not-started | — | — | — |
| RG058 | L'interface ne modifie jamais directement le modèle métier : toute modification… | implemented | architecture : UI → signaux → use cases/services (aucune écriture du modèle dans ui/) | — | vérifié par grep (pas de mutation du modèle dans src/ui/) |
| RG059 | Aucune valeur n'est codée en dur dans l'interface : dimensions, couleurs,… | not-started | — | — | — |
| RG060 | Les métadonnées de représentation graphique (positions des blocs, ordre des… | partial | core/services/layout_service.py; ui/main_window.py (_do_save / _init_workspace) | — | persistance câblée au save/load ; roundtrip layout à valider |
| RG061 | Le projet est enregistré dans un fichier unique structuré (JSON) contenant les… | implemented | project_service.py · save_project/load_project (JSON unique) | tests/test_project/test_project_service.py | fichier layouts séparé géré par LayoutService (RG060) |
| RG062 | L'auteur peut à tout moment désigner l'un des parcours de la carte comme… | implemented | usecases/journey_management/set_default_journey_usecase.py; ui/dialogs/journey_selection_dialog.py | tests/test_journeys/test_journey_usecases.py | désignation remplace le défaut, actif inchangé |

## B. Fonctionnalités (`03_features-*.md`)


### Hyperscript ::: Fonctionnalités

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

### Application

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN001 | Lancer l'application | partial | — | src/main.py (garde single-instance) + ui/main_window.py (écran d'accueil) | — | — (test appli T-xxx à venir) | test GUI à valider sur poste de dev |
| FN002 | Quitter l'application | partial | Files › Quit | ui/main_window.py · _handle_quit/closeEvent + QuitApplicationUseCase | — | tests/test_project/test_file_usecases.py (logique) | — |
| FN003 | Afficher l'historique des changements | partial | About › Change Log | ui/dialogs/change_log_dialog.py + core/services/change_log_service.py | — | — | menu About › Change Log câblé |
| FN004 | Afficher l'information « à propos » | partial | About › About Hyperscript | ui/dialogs/about_dialog.py + core/services/about_service.py | — | — | menu About › About Hyperscript câblé |

### Projet

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN005 | Créer un nouveau projet | implemented | Files › New Project... | usecases/project_management/create_project_usecase.py + main_window.py · _create_project | — | tests/test_project/test_project_service.py | — |
| FN006 | Ouvrir un projet | partial | Files › Open... | main_window.py · _open_project + LoadProjectUseCase | — | tests/test_project/test_file_usecases.py | boîte de dialogue fichier câblée |
| FN007 | Ouvrir un projet récent | greyed-MVP | Files › Recent Projects | — | — | — | — |
| FN008 | Enregistrer le projet | partial | Files › Save | main_window.py · _save_project/_do_save + SaveProjectUseCase | — | tests/test_project/test_file_usecases.py | — |
| FN009 | Enregistrer le projet sous... | partial | Files › Save as... | main_window.py · _save_project_as | — | tests/test_project/test_file_usecases.py | — |
| FN010 | Fermer le projet | partial | Files › Close | main_window.py · _close_project + ProjectService.close_project | — | tests/test_project/test_file_usecases.py | — |
| FN011 | Modifier le libellé du projet | not-started | — | — | — | — | — |

### Carte narrative

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN012 | Renommer la carte narrative | not-started | — | — | — | — | — |
| FN013 | Exporter la carte narrative en document de lecture | greyed-MVP | Files › Export Map... | — | — | — | — |

### Blocs narratifs

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN014 | Créer un bloc narratif | implemented | Project › Narrative Blocks › New | usecases/view_management/create_block_usecase.py; ui/main_window.py (_create_new_block) | — | — | tests/test_blocks/test_block_usecases.py |
| FN015 | Modifier les attributs d'un bloc | implemented | Project › Narrative Blocks › Edit... | usecases/view_management/update_block_usecase.py; ui/dialogs/block_dialog.py | — | — | tests/test_blocks/test_block_usecases.py |
| FN016 | Dupliquer un bloc | implemented | — | usecases/view_management/duplicate_block_usecase.py; ui/main_window.py | — | — | tests/test_blocks/test_block_usecases.py |
| FN017 | Déplacer un bloc | partial | — | ui/nodes/base_node.py (itemChange, snap RG046); ui/main_window.py (_on_workspace_modified) | — | — | test offscreen à valider |
| FN018 | Supprimer un bloc | implemented | Project › Narrative Blocks › Delete... | usecases/view_management/delete_block_usecase.py; ui/main_window.py | — | — | tests/test_blocks/test_block_usecases.py |
| FN019 | Gérer le rattachement d'un bloc aux parcours | implemented | — | usecases/view_management/update_block_usecase.py (journey_ids); ui/dialogs/block_dialog.py | — | — | tests/test_blocks/test_block_usecases.py |

### Transitions

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN020 | Créer une transition | implemented | Project › Transitions › New | usecases/view_management/create_transition_usecase.py; ui/views/journeys_workspace.py (tracé); ui/main_window.py | — | — | tests/test_transitions/ |
| FN021 | Annoter et modifier une transition | implemented | Project › Transitions › Edit... | usecases/view_management/update_transition_usecase.py; ui/dialogs/transition_dialog.py | — | — | tests/test_transitions/test_transition_usecases.py |
| FN022 | Supprimer une transition | implemented | Project › Transitions › Delete... | usecases/view_management/delete_transition_usecase.py; ui/main_window.py | — | — | tests/test_transitions/test_transition_usecases.py |

### Parcours

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN023 | Créer un parcours | implemented | Project › Journeys › New | usecases/journey_management/create_journey_usecase.py | — | — | tests/test_journeys/test_journey_usecases.py |
| FN024 | Renommer et décrire un parcours | implemented | — | usecases/journey_management/update_journey_usecase.py; ui/dialogs/journey_dialog.py | — | — | tests/test_journeys/test_journey_usecases.py |
| FN025 | Dupliquer un parcours | implemented | — | usecases/journey_management/duplicate_journey_usecase.py | — | — | tests/test_journeys/test_journey_usecases.py |
| FN026 | Activer un parcours | implemented | — | usecases/journey_management/activate_journey_usecase.py; ui/main_window.py (_activate_journey, Display > Journey) | — | — | tests/test_journeys/test_journey_usecases.py |
| FN027 | Supprimer un parcours | implemented | — | usecases/journey_management/delete_journey_usecase.py | — | — | tests/test_journeys/test_journey_usecases.py |
| FN038 | Définir le parcours par défaut | not-started | Project › Journeys › Set as Default... | — | — | — | — |

### Visualisation

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN028 | Naviguer dans l'espace de travail | partial | — | ui/views/journeys_workspace.py (grille 20/80, scène 4000×4000 extensible, auto-scroll 50 px) | — | — | test offscreen à valider |
| FN029 | Filtrer l'affichage par parcours | partial | — | core/services/journey_filter_service.py; ui/views/journeys_workspace.py; ui/main_window.py (Display > Journey dynamique) | — | — | tests/test_journeys/test_journey_filter_service.py (service) ; rendu visuel offscreen à valider |

### Agents et participations

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN030 | Associer des agents à un bloc | not-started | — | — | — | — | — |
| FN031 | Gérer les agents du projet | not-started | Project › Agents | — | — | — | — |
| FN032 | Naviguer entre les vues (navigation croisée) | not-started | — | — | — | — | — |
| FN033 | Aperçu d'export (espace de travail « Export ») | not-started | — | — | — | — | — |

### Relations entre agents

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN034 | Gérer une relation entre agents | not-started | Project › Relationships | — | — | — | — |

### Conditions

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN035 | Gérer la condition d'un bloc Condition | implemented | — | usecases/view_management/update_block_usecase.py (condition); ui/dialogs/block_dialog.py | — | — | tests/test_blocks/test_block_usecases.py |

### Vue « Relations »

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN036 | Vue « Relations » | not-started | — | — | — | — | — |

### Configuration

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| FN037 | Liste des types de relations | not-started | — | — | — | — | — |

### Hors périmètre MVP / à définir en phase de conception

| FN | Titre | Statut | Point d'entrée UI (menu) | Use case / service | Modèle | Test appli (T-xxx) | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |

## C. Entrées du menu général (`05_menu-*.yaml`)

| Chemin | Libellé | Raccourci | Statut | Clé `main_window.py` |
| --- | --- | --- | --- | --- |
| Fichiers | Fichiers |  | not-started | — |
| Fichiers › Nouveau projet... | Nouveau projet... | Ctrl+N | partial | menu_actions['new'] |
| Fichiers › Ouvrir... | Ouvrir... | Ctrl+O | partial | menu_actions['open'] |
| Fichiers › Fermer | Fermer | Ctrl+W | partial | menu_actions['close'] |
| Fichiers › Enregistrer | Enregistrer | Ctrl+S | partial | menu_actions['save'] |
| Fichiers › Enregistrer sous... | Enregistrer sous... | Ctrl+Shift+S | partial | menu_actions['save_as'] |
| Fichiers › Exporter la carte... | Exporter la carte... |  | greyed-MVP | — |
| Fichiers › Importer une carte... | Importer une carte... |  | greyed-MVP | — |
| Fichiers › Projets récents | Projets récents |  | greyed-MVP | — |
| Fichiers › Quitter | Quitter | Ctrl+Q | partial | menu_actions['quit'] |
| Édition | Édition |  | greyed-MVP | — |
| Édition › Annuler | Annuler | Ctrl+Z | greyed-MVP | — |
| Édition › Rétablir | Rétablir | Ctrl+Y | greyed-MVP | — |
| Édition › Couper | Couper | Ctrl+X | greyed-MVP | — |
| Édition › Copier | Copier | Ctrl+C | greyed-MVP | — |
| Édition › Coller | Coller | Ctrl+V | greyed-MVP | — |
| Affichage | Affichage |  | partial | — |
| Affichage › Parcours | Parcours |  | implemented | main_window._rebuild_journey_menu (dynamique, cochable, FN026/FN029) |
| Affichage › Zoom | Zoom |  | not-started | — |
| Affichage › Zoom › Avant | Avant | Ctrl+= | greyed-MVP | — |
| Affichage › Zoom › Arrière | Arrière | Ctrl+- | greyed-MVP | — |
| Affichage › Zoom › Réinitialiser | Réinitialiser | Ctrl+0 | greyed-MVP | — |
| Projet | Projet |  | partial | — |
| Projet › Vue | Vue |  | stub | menu_actions['view_*'] (stubs — vues activées par la barre d'onglets) |
| Projet › Vue › Parcours | Parcours |  | stub | menu_actions['view_journeys'] |
| Projet › Vue › Agents | Agents |  | stub | menu_actions['view_agents'] |
| Projet › Vue › Relations | Relations |  | stub | menu_actions['view_relationships'] |
| Projet › Vue › Export | Export |  | stub | menu_actions['view_export'] |
| Projet › Agents | Agents |  | stub | menu_actions['agents_*'] (stubs — vue Agents hors MVP) |
| Projet › Agents › Nouveau... | Nouveau... |  | stub | menu_actions['agents_new'] |
| Projet › Agents › Éditer... | Éditer... |  | stub | menu_actions['agents_edit'] |
| Projet › Agents › Copier | Copier |  | stub | menu_actions['agents_copy'] |
| Projet › Agents › Supprimer... | Supprimer... |  | stub | menu_actions['agents_delete'] |
| Projet › Agents › Associer à un bloc... | Associer à un bloc... |  | stub | menu_actions['agents_associate'] |
| Projet › Blocs narratifs | Blocs narratifs |  | implemented | menu_actions['blocks_*'] |
| Projet › Blocs narratifs › Nouveau | Nouveau |  | implemented | menu_actions['blocks_new'] |
| Projet › Blocs narratifs › Nouveau › Scène | Scène |  | implemented | menu_actions['blocks_new_scene'] |
| Projet › Blocs narratifs › Nouveau › Pivot | Pivot |  | implemented | menu_actions['blocks_new_pivot'] |
| Projet › Blocs narratifs › Nouveau › Condition | Condition |  | implemented | menu_actions['blocks_new_condition'] |
| Projet › Blocs narratifs › Nouveau › Fin | Fin |  | implemented | menu_actions['blocks_new_ending'] |
| Projet › Blocs narratifs › Éditer... | Éditer... |  | implemented | menu_actions['blocks_edit'] (BlockDialog, FN015) |
| Projet › Blocs narratifs › Copier | Copier |  | implemented | menu_actions['blocks_copy'] (FN016) |
| Projet › Blocs narratifs › Supprimer... | Supprimer... |  | implemented | menu_actions['blocks_delete'] (FN018) |
| Projet › Transitions | Transitions |  | implemented | menu_actions['transitions_*'] |
| Projet › Transitions › Nouvelle | Nouvelle |  | implemented | menu_actions['transitions_new'] (FN020, tracé) |
| Projet › Transitions › Éditer... | Éditer... |  | implemented | menu_actions['transitions_edit'] (TransitionDialog, FN021) |
| Projet › Transitions › Supprimer... | Supprimer... |  | implemented | menu_actions['transitions_delete'] (FN022) |
| Projet › Parcours | Parcours |  | implemented | menu_actions['journeys_*'] |
| Projet › Parcours › Nouveau | Nouveau |  | implemented | menu_actions['journeys_new'] (FN023) |
| Projet › Parcours › Éditer... | Éditer... |  | implemented | menu_actions['journeys_edit'] (JourneyDialog, FN024) |
| Projet › Parcours › Copier | Copier |  | implemented | menu_actions['journeys_copy'] (FN025) |
| Projet › Parcours › Définir par défaut... | Définir par défaut... |  | implemented | menu_actions['journeys_set_default'] (FN038) |
| Projet › Parcours › Supprimer... | Supprimer... |  | implemented | menu_actions['journeys_delete'] (FN027) |
| Projet › Relations | Relations |  | stub | menu_actions['relationships_*'] (stubs — vue Relations hors MVP) |
| Projet › Relations › Nouvelle... | Nouvelle... |  | stub | menu_actions['relationships_new'] |
| Projet › Relations › Éditer... | Éditer... |  | stub | menu_actions['relationships_edit'] |
| Projet › Relations › Supprimer... | Supprimer... |  | stub | menu_actions['relationships_delete'] |
| À propos | À propos |  | not-started | — |
| À propos › Historique des changements | Historique des changements |  | partial | menu_actions['change_log'] |
| À propos › À propos d'Hyperscript | À propos d'Hyperscript |  | partial | menu_actions['about'] |

## D. Scénarios d'utilisation (`01_user_stories-*.md`)

| SU | Titre | FN couvertes | Statut agrégé |
| --- | --- | --- | --- |
| SU001 | Gérer un projet narratif | FN001, FN002, FN005, FN006, FN007, FN008, FN009, FN010, FN011 | not-started |
| SU002 | Gérer une carte narrative | FN012, FN013 | not-started |
| SU003 | Gérer un bloc narratif | FN014, FN015, FN016, FN017, FN018, FN019, FN035 | partial |
| SU004 | Gérer une transition entre blocs | FN020, FN021, FN022, FN035 | implemented |
| SU005 | Gérer un parcours | FN019, FN023, FN024, FN025, FN026, FN027, FN038 | implemented |
| SU006 | Visualiser la carte narrative (vue « Parcours ») | FN017, FN028, FN029 | partial |
| SU007 | Exporter la carte narrative | FN013, FN033 | not-started |
| SU008 | Gérer les participations agent-bloc | FN030, FN031 | not-started |
| SU009 | Gérer la vue agents — initialisé, à finaliser après la phase de conception | FN031, FN032 | not-started |
| SU010 | Visualiser l'aperçu d'export — initialisé, à finaliser après la phase de conception | FN033 | not-started |
| SU011 | Gérer une relation entre agents | FN034, FN037 | not-started |
| SU012 | Gérer la vue « Relations » — initialisée, à finaliser après la phase de conception | FN032, FN036 | not-started |
