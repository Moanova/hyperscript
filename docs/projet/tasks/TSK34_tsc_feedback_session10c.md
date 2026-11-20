# TSK34 — Retours de test TSC (séance 10, 3ᵉ salve, points 2–4 après tests de TSK32/TSK33)

- **Statut** : Review (20-11-2026) ; dépend de #TSK32 (Review), #TSK33 (Review). Le point 1 (panneau latéral non redimensionnable) est **reporté** (comportement voulu : largeur fixe en config, décision TSK31 3.2).
- **Origine** : retours de test manuel TSC après TSK32/TSK33 — 4 points, le point 1 sera revu plus tard ; points 2–4 à traiter ici.

## Analyse des retours (cause racine vérifiée dans le code)

| Retour | Symptôme | Cause racine |
|---|---|---|
| 2 | Grille de « Relationships » incomplète au premier affichage de l'onglet ; OK après toute action (scroll, drag carte, édition) | `_draw_grid()` n'est déclenché que par `_relayout` (`:509`), les `valueChanged` des ascenseurs (`:387-388`) et `resizeEvent` du workspace (`:537-540`). Aucun `showEvent` : si la page était cachée au `populate`, la grille a été dessinée pour l'ancien viewport et rien ne redessine à la première activation de l'onglet. « Journeys » a le même pattern latent (`journeys_workspace.py:189-192`). |
| 3 | `AttributeError: 'MatrixRelationshipCard' object has no attribute 'deleteLater'` à la suppression d'une relation (puis carte ramenée en case (0,0), menu « Edit » persistant) et au drag de la **dernière** carte d'agent d'une ligne/colonne | `QGraphicsItem` **n'est pas un `QObject`** (vérifié : `hasattr(QGraphicsRectItem, 'deleteLater')` → `False`) ; `relationships_workspace.py:177` appelle `self.card.deleteLater()`. `setParentItem(None)` ne retire pas l'item de la scène. L'exception interrompt `_rebuild_cells` à mi-parcours → état incohérent (symptômes en cascade). Le drag de la dernière carte fait perdre sa relation à une case → `set_content(None)` → même crash. |
| 4 | Fenêtre agrandissable mais non réductible sous ses dimensions initiales (1280×720) | `main_window.py:143-144` : `setMinimumSize(window_min_width=1280, window_min_height=720)` — le minimum fenêtre = la taille initiale. La correction TSK30 (3.3) avait seulement retiré la contribution de la vue matrice (`setMinimumSize(0,0)` sur la vue). |

## Décisions actées (séance 10, TSC)

1. **Point 1 reporté** (largeur de panneau fixe = voulu, anti bande grise TSK31 3.2).
2. **Point 2** : `showEvent` → `_draw_grid()` dans `RelationshipsWorkspace` **et** `JourneysWorkspace` (même bug latent).
3. **Point 3** : suppression de la carte par `self.scene().removeItem(self.card)` (garde `scene is not None`), plus de `setParentItem(None)`/`deleteLater`.
4. **Point 4, façon planoscript** : planoscript ne fait qu'un `setGeometry(100, 100, 1280, 720)` et **aucun `setMinimumSize`** — la taille initiale seule, le minimum effectif laissé au layout des vues (qui pilotent leur propre minimum, ex. `setMinimumSize(0,0)` TSK30 3.3). → remplacer `setMinimumSize(window_min_width/height)` par `setGeometry(100, 100, window_width, window_height)` ; config : `window_min_width/height` remplacées par `window_width/height` = 1280/720 ; FN028 (`03_features` FR/EN) et `04_interface` §2 mis à jour (1280×720 = taille **initiale**, fenêtre librement redimensionnable en réduction, chaque vue pilotant son minimum).

## Plan d'implémentation

1. `src/ui/views/relationships_workspace.py` : (3) `set_content` — `scene().removeItem(card)` ; (2) `showEvent` → `_draw_grid()`.
2. `src/ui/views/journeys_workspace.py` : (2) `showEvent` → `_draw_grid()`.
3. `src/ui/main_window.py` : (4) `setMinimumSize(...)` → `setGeometry(100, 100, window_width, window_height)`.
4. `src/config/config.json` : `window_min_width/height` → `window_width/height` (1280/720).
5. Tests : régression (3) — suppression d'une relation puis `refresh()` sans exception + carte retirée, et drag de la dernière carte d'agent sans exception (niveau workspace et MainWindow avec `QMessageBox` mocké) ; (2) — grille couvre toute la zone visible après `show()` sans autre action (Relationships via workspace, Journeys via MainWindow + onglet) ; (4) — `MainWindow` : `minimumSize()` non fixée à 1280×720 et géométrie initiale 1280×720.
6. Docs : `03_features` FN028 FR/EN, `04_interface` §2 FR/EN, kanban (TSK34 Doing), SESSIONS.md. Commit/push sur demande explicite de TSC uniquement.

## Journal

- 2026-11-20 : TSK34 créée (→ #TSK32, #TSK33) et passée en Doing (feu vert TSC) ; fiche initialisée avec l'analyse (causes racines vérifiées) et le plan ci-dessus. Implémentation lancée.
- 2026-11-20 : **implémentée** (plan exécuté tel quel) — `src/ui/views/relationships_workspace.py` (`set_content` : `scene().removeItem(card)` à la place de `setParentItem(None)`+`deleteLater()` — `QGraphicsItem` n'est pas un `QObject` ; `showEvent` → `_draw_grid()`), `src/ui/views/journeys_workspace.py` (`showEvent` → `_draw_grid()`, même bug latent), `src/ui/main_window.py` (`setMinimumSize(window_min_*)` → `setGeometry(100, 100, window_width, window_height)`, façon planoscript : aucun minimum fixe, minimum piloté par les vues), `src/config/config.json` (`window_min_width/height` → `window_width/height` = 1280/720), tests (+3 offscreen Relationships : suppression sans exception + carte retirée, drag dernière carte sans exception, grille pleine au 1ᵉʳ show ; +2 smoke MainWindow : géométrie initiale 1280×720 sans minimum fixe, `_delete_relationship_entity` sans exception avec `QMessageBox` mocké ; +1 Journeys : grille couvre la zone visible au 1ᵉʳ affichage de l'onglet), docs (`03_features` FN028 FR/EN, `04_interface` §2 FR/EN). **Vérifications** : py_compile OK ; pyflakes clean (aucun nouveau warning vs base) ; config JSON valide ; **148 tests passed + 3 failed pré-existants** (`test_block_drag_offscreen.py`, hors scope, reproductibles sur arbre propre). Passée en **Review**. Pas de commit/push (non demandé).
