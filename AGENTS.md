# AGENTS.md — Hyperscript

Règles de travail pour tout agent IA intervenant sur ce dépôt.

## Vue d'ensemble

Hyperscript est un éditeur visuel de cartes narratives :
- application desktop PySide6 (Python >= 3.10),
- composée de blocs narratifs typés reliés par des connecteurs (transitions),
- avec sauvegarde JSON,
- et layout visuel persistant.
MVP :
- espaces de travail « Agents », « Journeys », « Relationships » (faits) et « Preview » (aperçu de lecture in-app, en conception TSK37 — renommée depuis « Export ») ; l'export sur fichier (SU007/FN013, « Files › Export Map... ») reste post-MVP et grisé,
- une seule carte narrative par projet,
- sélection unique (pas de rubber band multi-sélection).

## Commandes

- Mettre en place l'environnement (une fois, depuis la racine du dépôt) : `uv venv` puis `uv sync --no-install-project` — installe tout ce qui est verrouillé dans `uv.lock` (voir README §Installation pour la procédure complète, y compris pour un tiers).
- Lancer l'application : `.venv/bin/python src/main.py` (depuis la racine du dépôt ; `python src/main.py` si le venv est activé).
- Lancer les tests : `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/ -q`
  - `tests/test_application/` (pywinauto, FNxxx) est automatiquement skipped sans session GUI.
- Vérifier la syntaxe : `.venv/bin/python -m py_compile <fichiers modifiés>`.

## Environnement reproductible (uv)

- Environnement de référence : venv uv `.venv/` (git-ignoré), créé par `uv venv` avec l'interpréteur épinglé dans `.python-version` (3.14) et les dépendances verrouillées dans `uv.lock` (commité) — identique pour tout le monde.
- Nouvelle dépendance : l'ajouter dans `pyproject.toml` (`[project.dependencies]` pour le runtime, `[dependency-groups] dev` pour les outils de test/lint), puis `uv lock`, et **commiter `uv.lock` dans le même commit** (la CI échoue sinon, `--locked`). Ne jamais recréer de `requirements*.txt` ni éditer `uv.lock` à la main.
- `.pytest_cache/` est git-ignoré.

## Pièges connus

- **Single-instance** : `src/main.py` contient un garde `QLocalServer`. Si une instance tourne déjà, un nouveau lancement **se termine silencieusement**.
  Toujours fermer complètement l'instance en cours avant de tester une modification (sinon on teste l'ancien code).
- Le working tree contient fréquemment du travail non commité : jamais de reset/checkout destructif. Les commits locaux sont possibles à tout moment, mais **aucun push ni aucune PR sans instruction explicite** de l'utilisateur (voir « Méthode de travail »).
- **Projet non installable comme package** : `uv sync` ou `pip install -e .` sans `--no-install-project` échoue (hatchling ne trouve pas de package, layout `src/` plat) — lancer l'application par `python src/main.py`. Ne lancer `uv venv` que depuis la racine du dépôt : c'est seulement là que `pyproject.toml` (`requires-python = ">=3.10"`) et `.python-version` sont pris en compte.

## Architecture

Flux : UI → use cases → services → models. L'UI ne modifie jamais directement le modèle métier : passer par les use cases/services.

```
src/
├── main.py                          # Point d'entrée (QApplication, single-instance)
├── config/                          # config.json + user_state.json et leurs loaders
├── core/
│   ├── models/                      # data_model (entités métier), view_model (layouts, enums)
│   └── services/                    # ProjectService, LayoutService, ...
├── usecases/                        # project_management, file_management, view_management
└── ui/
    ├── main_window.py               # Fenêtre principale, barre de menus, orchestration
    ├── views/events_workspace.py    # Vue graphique (QGraphicsView)
    ├── nodes/                       # base_node, block_node, agent_node, ...
    ├── widgets/                     # info_bar, ...
    ├── utils/                       # ui_utils
    └── dialogs/                     # about_dialog, change_log_dialog, component_dialog
```

## Règles métier et exigences

- Chaque règle métier RG0xx est définie dans
  `docs/specification/02_business_rules-FR.md` (versions EN/FR dans `docs/specification/`), référencée en commentaire dans le code qui l'implémente, et couverte par un test (ex. `tests/test_relations/`).
- Toute modification d'une règle métier implique la mise à jour du test correspondant.
- Les user stories (SUxxx) sont dans `docs/specification/01_user_stories-*.md` ; les tests d'application (pywinauto) suivent la nomenclature `test_fnXXX_*.py` et sont spécifiés dans `tests/SPECIFICATION.md`.
- Les entrées de menu non implémentées sont stubbées dans `main_window.py` par `self.menu_actions['clé'] = ... addAction(..., lambda: None)` : les conserver lors des refactors de menus.

## Documentation à recharger en début de séance

Au début de chaque séance de travail, recharger dans le contexte (sans que cela dispense de relire la section ciblée au moment d'une modification) :
- Tous les documents de `docs/specification/` (versions FR ou EN au choix, le contenu est identique) : user stories, règles de gestion, features, interface, menu, data model, périmètre MVP.
- `docs/project/kanban.md` (état des tâches, dépendances, fichier de détail de la tâche en cours dans `docs/project/tasks/`).

## Suivi de projet

- L'avancement est suivi dans `docs/project/kanban.md` (épiques EPCnn, tâches TSKnn, dépendances `→ #TSKnn` déclarées uniquement sur la tâche dépendante).
- `docs/project/kanban.md` est la source unique de vérité.
- Le détail d'une tâche TSKnn (analyse, décisions, journal) est consigné dans `docs/project/tasks/TSKnn_*.md`, créé au passage en Doing.
- Une tâche ne passe en Doing que si ses dépendances sont en Review ou en Done.

## Méthode de travail (types de séances)

Règle générale : toute action qui met à jour la base de code (séance d'implémentation ou non) peut être **commitée localement**, mais seuls les **push** (directement sur `dev`, sans PR) et les **PR** (passage `dev` → `main`, avec CI) sont effectués sur **instruction explicite** de l'utilisateur. Le merge de la PR reste à la charge de l'utilisateur.

### Conception / re-conception
- Échange conversationnel : analyse, propositions, décisions actées.
- Livrables : notes de conception dans `docs/conception/` (FR/EN) et mises à jour des specs `docs/specification/` (FR/EN) si décision actée ; tâche créée dans `docs/project/kanban.md` si besoin.

### Implémentation
- 1/ Établir le plan d'implémentation avec l'utilisateur ; 2/ implémenter la tâche sélectionnée ; 3/ implémenter et exécuter les tests de validation.
- Tout se fait sur la branche `dev`. Si la boucle implémentation/test dépasse 3 itérations sans satisfaire 100 % des tests : arrêter et établir l'état des lieux pour décision utilisateur. En cas d'ambiguïté, demander les compléments nécessaires.
- Livrables : code + tests + docstrings, fiche `docs/project/tasks/TSKnn_*.md`, kanban (Doing → Review après implémentation + tests, → Done après validation utilisateur).

### Validation
- Exécution des tests et revue des tâches en Review ; retours de l'utilisateur.
- Livrables : résultats des tests consignés, kanban (Review → Done), correctifs éventuels.

### Explication / appropriation de la base de code
- Réponses et explications pour le concepteur (celui qui veut s'approprier la base de code) : architecture, flux, patterns.
- Livrable : aucun fichier modifié.

### Re-documentation
- Mise à jour de la documentation existante (`README.md`, `AGENTS.md`, `docs/`, `SESSIONS.md`) et création de nouveaux documents si nécessaire (ex. rétro-spécification technique).
- Livrables : documents mis à jour ou créés.

### Fin de séance (tous types)
- `SESSIONS.md` renseigné : contenu des travaux, problèmes rencontrés, choix actés.
- Tout blocage non résolu en séance est consigné dans `BLOCKERS.md` (créé à la racine si absent).

## Conventions

- Aucune valeur codée en dur pour l'UI : passer par config.json (`config.config_loader.get` avec valeur par défaut) ou par une constante de classe (ex. `HIT_AREA_WIDTH`).
- Docstrings et commentaires de code : anglais. Messages de commit : français, préfixés par la date (ex. `2026-10-10 : ...`).
- Diff minimal : ne pas modifier ce qui n'est pas demandé ; retirer complètement le code mort (pas de `_unused`, pas de shims de compatibilité).
- Découplage Qt : le workspace communique avec MainWindow via des signaux plutôt que par appel de méthodes privées d'un autre composant.

## Patterns UI établis (ne pas faire régresser)

- **Hit-testing** : zone cliquable définie par `shape()` (QPainterPathStroker) avec un `boundingRect()` couvrant la zone — jamais la seule épaisseur du stylo (voir `Connection.shape`).
- **Infobulles** : affichage immédiat dans `hoverEnterEvent` via `QToolTip.showText()` ; le workspace avale l'événement `ToolTip` automatique de Qt (`EventsWorkspace.viewportEvent`). Ne pas réintroduire le mécanisme automatique (délai système + infobulle en double).
- **Menu contextuel** : pattern `menu.exec()` + dispatch sur l'action retournée (voir `EventsWorkspace.show_context_menu`) — pas de timer, pas de drapeaux d'état, une seule connexion par signal.
- **Feedback de sélection** : brancher `set_selected_appearance` via `itemChange(ItemSelectedChange)` (pattern commun à BaseNode et Connection).
- **Sélection au clic droit** : sélectionner l'item sous le curseur avant d'ouvrir le menu contextuel.

## Vérifications attendues après chaque modification

1. `.venv/bin/python -m py_compile` sur chaque fichier modifié.
2. `.venv/bin/python -m pyflakes src` (doit rester clean ; vérifié aussi en CI).
3. Suite de tests complète (commande ci-dessus).
4. Pour l'UI Qt : test ciblé offscreen (script jetable, non commité), instancier le composant réel, simuler les événements Qt, vérifier par rendu `QImage` si le point à valider est visuel.
5. Ne pas lancer l'application en tâche de fond pour tester : préférer les tests offscreen (voir single-instance).

## CI (GitHub Actions)

- Workflow : `.github/workflows/ci.yml`, déclenché sur `push` et `pull_request` vers `main` (plus `workflow_dispatch` pour un lancement manuel).
- Étapes : `uv venv` + `uv sync --no-install-project --locked` (échoue si `uv.lock` est périmé : régénérer le lock avec `uv lock` à chaque changement de `pyproject.toml`), libs système Qt (apt), `compileall -q src`, `pyflakes src`, `QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest tests/ -q`.
- Le lint porte sur `src/` uniquement (`tests/` a des warnings pyflakes pré-existants, hors scope). Les tests Qt offscreen se skippent proprement si les libs Qt sont absentes.
