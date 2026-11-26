# TSK41 — Libellés de la vue « Preview » : « Participations: » / « Relationships: »

- **Statut** : Review (26-11-2026) ; indépendante (poursuite de #TSK39/#TSK40, Review).
- **Origine** : ultime modification mineure demandée par TSC en séance 12.

## Demande TSC (26-11-2026, séance 12)

Dans la vue « Preview », pour chaque bloc :
1. la ligne des agents participants affichée avec « Agents: » devient « **Participations:** » ;
2. chaque relation ancrée au bloc est préfixée par « **Relationships:** ».

## Cause racine / modification

| Point | Où | Modification |
|---|---|---|
| « Agents: » → « Participations: » | `PreviewService._block_html` (`src/core/services/preview_service.py:223`) : `<p><em>Agents: …</em></p>` | `<p><em>Participations: …</em></p>` (commentaire TSK41) |
| Préfixe « Relationships: » | `_block_html`, boucle des relations ancrées (`:233-241`) : `<p>{label}</p>` | `<p>Relationships: {label}</p>` (le lien de note reste dans le label) |

Hors périmètre : la ligne « Agents: … » de l'infobulle du badge (`ParticipationBadgeService.tooltip_agents_line`) et la ligne « Agents: » du dialogue d'édition du bloc restent inchangées.

## Plan d'implémentation

1. `preview_service.py` : les 2 libellés (+ commentaires/docstring TSK41).
2. Tests : `tests/test_preview/test_preview_service.py` — `test_participating_agents_rendered_under_block_content` assert `Participations: Alice, Bob` et `Relationships: Alice — Bob : friend` (ordre content → participations → relations conservé).
3. Specs FR/EN : `03_features` (FN033), `04_interface` §7, `conception/05_preview` — préfixes « Participations: » / « Relationships: » (TSK41).
4. Vérifications : `py_compile`, pyflakes, suite complète offscreen.
5. Kanban : TSK41 → Review. Commit+push sur `dev` uniquement sur demande explicite TSC (demandée ensuite : « Ok, tu peux faire le commit et pousser »).

## Journal

- 2026-11-26 : créée en To do puis passée en Doing (demande TSC séance 12).
- 2026-11-26 : **implémentée et passée en Review** — `_block_html` : `<p><em>Participations: …</em></p>` (au lieu de « Agents: ») et `<p>Relationships: {label}</p>` pour chaque relation ancrée (lien de note conservé dans le label) ; docstring module mention TSK41 ; test `test_participating_agents_rendered_under_block_content` mis à jour (« Participations: Alice, Bob », « Relationships: Alice — Bob : friend », ordre content → participations → relations) ; specs FR/EN (`03_features` FN033, `04_interface` §7, conception `05_preview`) à jour. **Vérifications** : py_compile OK ; pyflakes clean ; suite complète **192 tests passed + 3 failed pré-existants** (`test_block_drag_offscreen.py`, reproductibles arbre propre `a05771a`). **Commit+push sur `dev` effectués sur demande explicite TSC** (demande du 26-11-2026 : « Ok, tu peux faire le commit et pousser la modification sur le dépôt »).
