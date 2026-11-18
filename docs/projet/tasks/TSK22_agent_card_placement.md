# TSK22 — Placement d'une nouvelle carte agent à côté du groupe existant

- **Statut** : Doing (18-11-2026) → dépend de #TSK21 (en Review)
- **Origine** : retour TSC séance 05 (2026-11-18) après validation du snap sur cellule (TSK21) : la création d'un nouvel agent place la carte sur la cellule fixe (0, 140) près de l'origine de la scène, donc « au centre » de la vue (ensure_visible centre dessus) même si les autres cartes sont ailleurs.

## Décision actée (feu vert TSC, option 1 seule)

- `AgentsWorkspace.next_free_card_position` : si des cartes existent, l'ancre de recherche devient la **cellule juste à droite de la boîte englobante** des cartes (x = max des origines x + `agents_view_cell_width`, y = min des origines y), puis première cellule libre par scan en anneaux (`LayoutService.find_nearest_free_position`, bornes scène) — la grappe grandit compacte vers la droite, comme le pattern « premier emplacement libre à droite de l'ancre » de la vue Journeys (TSK16 option B).
- Sans aucune carte : repli sur l'ancre par défaut (80, 80) snappée → cellule (0, 140).
- Aucun changement dans `agent_card.py` ; RG050 (pas de chevauchement) toujours garanti par construction (cellule 200×140 > carte 160×100).
- Couvre aussi la copie d'agent et la création depuis le dialogue d'association (même chemin `add_agent_card`).

## Plan d'implémentation

1. `src/ui/views/agents_workspace.py` : `next_free_card_position` ancré sur la boîte englobante quand des cartes existent.
2. Tests offscreen (`test_agents_workspace_offscreen.py`) : placement initial en ligne (0,140)/(200,140)/(400,140) ; nouvelle carte créée après déplacement des cartes ailleurs → cellule adjacente au groupe, sur cellule, sans chevauchement ; workspace vide → (0, 140).
3. Spec FR/EN : RG065 (+ placement à la création), `04_interface` §5, matrices ; kanban TSK22 Doing → Review.

## Journal

- 2026-11-18 : tâche créée et passée en Doing (TSK21 en Review). Option 1 retenue seule (ancre = boîte englobante des cartes existantes) ; options écartées : ancre carte sélectionnée, ancre centre du viewport, centroïde.
- 2026-11-18 : **travaux réalisés** — `agents_workspace.py` v3 : `next_free_card_position` ancré sur la cellule (max_x + cell_w, min_y) de la boîte englobante des cartes existantes quand il y en a, repli sur l'ancre par défaut (80, 80) → cellule (0, 140) sinon, puis `snap_to_grid` + `find_nearest_free_position` (bornes scène) ; aucun changement dans `agent_card.py`. Tests offscreen v3 : placement initial en ligne (0,140)/(200,140)/(400,140), workspace vide → (0,140), nouvelle carte après déplacement du groupe en (1000,980)/(1200,1120) → cellule (1400, 980) adjacente, sur cellule, sans chevauchement ; tests existants ajustés (A1 démarre à (200,140)). Spec FR/EN : RG065 (+ phrase création), 04_interface §5, matrices. py_compile OK, **73 tests passed + 1 skipped** (offscreen Qt skippé sans libGL dans le sandbox — à valider sur poste de dev). Passée en Review.
