# TSK35 — Panneau latéral redimensionnable + repliable par icône de contrôle

- **Statut** : Review (20-11-2026) ; dépend de #TSK33 (Done), #TSK34 (Done). C'est le point 1 reporté de la 3ᵉ salve TSK34.
- **Origine** : étude demandée par TSC séance 10 (« la possibilité de redimensionner le panneau latéral, et aussi de le replier ou déplier à partir d'un icône de contrôle — faisable ? comment ? »). Réponse : oui — conception ci-dessous, actée par « ok, crée et implémente ».

## Conception actée (séance 10)

Le verrouillage actuel vient de `FiltersSidePanel.setFixedWidth(PANEL_WIDTH_PX)` (min = max = 260 → slot verrouillé, curseur trompeur) et du pin `setSizes` dans `SidePanelSplitter.resizeEvent` (TSK31 3.2, anti bande grise).

1. **Redimensionnement libre par le handle** : `setFixedWidth` → `setMinimumWidth(PANEL_MIN_WIDTH_PX)` (nouvelle clé config `side_panel_min_width_px` = **180**) ; suppression du pin `setSizes` dans `resizeEvent` (les tailles d'un splitter remplissent toujours sa largeur — plus de bande exposée). Le handle devient réellement draggable ; au resize de la fenêtre, la vue absorbe (stretch factor 0,1).
2. **Repli/dépli via icône** : handle personnalisé — override `createHandle()` → `SidePanelHandle(QSplitterHandle)` qui peint un **chevron** (◀ ouvert / ▶ replié, couleur `text_secondary`) ; clic sans drag (`mouseReleaseEvent` à < 4 px du press) → `toggle_collapse()` ; collapse = `panel.hide()` + `setSizes([w, 0])`, expand = `panel.show()` + restauration de `_expanded_width`. Le handle reste visible même replié (meilleur qu'un bouton dans le panneau, caché au repli). Drag du handle quand replié → Qt réaffiche le panneau.
3. **Persistance** : largeur persistée en **app-level** dans `src/config/user_state.json` via `user_state_loader` (clé `side_panel_width_px`, défaut = config `side_panel_width_px` = 260) — même mécanisme que `last_project_dir`. **Synchro entre les deux vues** : `SidePanelSplitter.panel_width_changed = Signal(int)` (émis sur `splitterMoved` et `set_panel_width`) → MainWindow applique la largeur à l'autre splitter (garde `_syncing_panel_width` anti-récursion) et persiste. **État replié : de session uniquement** (comme les filtres, RG047) — la largeur, elle, persiste.

## Plan d'implémentation

1. `src/config/config.json` : ajouter `"side_panel_min_width_px": 180`.
2. `src/ui/widgets/filters_side_panel.py` :
   - `PANEL_MIN_WIDTH_PX` (config) ; `FiltersSidePanel._build_ui` : `setFixedWidth` → `setMinimumWidth(PANEL_MIN_WIDTH_PX)` ;
   - `SidePanelHandle(QSplitterHandle)` (chevron peint dans `paintEvent`, clic → `toggle_collapse`) ;
   - `SidePanelSplitter` : `panel_width_changed = Signal(int)`, `createHandle()` perso, `collapsed`/`_expanded_width`, `set_panel_width(w)` (clamp min, `setSizes`), `collapse()`/`expand()`/`toggle_collapse()`, `_on_splitter_moved` → émet la largeur (si non replié), **suppression du pin `resizeEvent`** (stylesheet sombre conservé).
3. `src/ui/main_window.py` : `__init__` → `self._syncing_panel_width = False` ; `_init_workspace` → après création des deux workspaces : lire `int(_get_user_state("side_panel_width_px", PANEL_WIDTH_PX))`, connecter `panel_width_changed` des deux splitters (`journeys_splitter`, `relationships_workspace._splitter`) → `_on_side_panel_width_changed(w, source)` (applique aux autres + `_set_user_state`), puis `set_panel_width(...)` initial ; import `PANEL_WIDTH_PX`.
4. Tests (avec `user_state_loader._STATE_PATH` redirigé vers tmp via fixture autouse dans les fichiers construisant MainWindow) :
   - splitter autonome/workspace : `set_panel_width(320)` → largeur panneau 320 + signal émis + clamp au min (180) ; `panel.x()+panel.width() == sp.width()` au resize (plus de bande grise sans pin) ;
   - handle : `isinstance(sp.handle(1), SidePanelHandle)` ; clic (press/release sans déplacement) → `collapsed` True, `sizes()[-1] == 0`, panneau caché ; 2ᵉ clic → restauré à `_expanded_width` ;
   - MainWindow : largeur persistée (`_get_user_state`) et réappliquée à la création ; synchro Journeys ↔ Relationships (changer sur un splitter → l'autre suit) ;
   - mise à jour du test TSK31 `test_no_gray_strip_on_the_right_of_the_panel` (appeler `set_panel_width(_PANEL_WIDTH)` avant le resize) et `test_panel_slot_pinned_to_panel_width_on_resize` (TSK33).
5. Docs : `04_interface` §4/§6 FR/EN (panneau redimensionnable, repliable via chevron du handle, largeur persistée app-level, min en config), kanban (TSK35 Doing), SESSIONS.md. Commit/push sur demande explicite de TSC uniquement.

## Journal

- 2026-11-20 : TSK35 créée (→ #TSK33, #TSK34) et passée en Doing (feu vert TSC) ; conception actée ci-dessus (min 180 px, replié = session). Fiche initialisée. Implémentation lancée.
- 2026-11-20 : **implémentée** (plan exécuté tel quel) — `src/config/config.json` (`side_panel_min_width_px` = 180), `src/ui/widgets/filters_side_panel.py` (`FiltersSidePanel` : `setFixedWidth` → `setMinimumWidth` ; nouveau `SidePanelHandle` (chevron peint dans `paintEvent`, clic sans drag → `toggle_collapse`) ; `SidePanelSplitter` : `panel_width_changed = Signal(int)`, `createHandle()` perso, `set_panel_width` (clamp min), `collapse()`/`expand()`/`toggle_collapse()`, `resizeEvent` réapplique la **largeur courante** au lieu de l'ancien pin fixe TSK31), `src/ui/main_window.py` (largeur initiale depuis `user_state`, connexion `panel_width_changed` des deux splitters → `_on_side_panel_width_changed` : synchro + `_set_user_state("side_panel_width_px", …)`, garde `_syncing_panel_width`), tests (+2 nouveaux TSK35 : redimensionnement/persistance/synchro/min + clic handle repli/dépli ; 2 tests de pin TSK31/TSK33 mis à jour pour la nouvelle API ; fixture autouse d'isolation `user_state_loader._STATE_PATH`/`_state` vers tmp dans les 2 fichiers construisant MainWindow — le vrai `user_state.json` est suivi par git), docs `04_interface` §4/§6 FR/EN. **Vérifications** : py_compile OK ; pyflakes identique à l'arbre de base ; config JSON valide ; **150 tests passed + 3 failed pré-existants** (hors scope) ; `user_state.json` du dépôt non pollué par les tests ; rendu vérifié par capture offscreen (chevron peint sur le handle, repli [1280, 0] panneau caché, dépli [1016, 260] restauré). Passée en **Review**. Pas de commit/push (non demandé).
