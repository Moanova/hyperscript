# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : preview_service.py
# Version      : 1
# Date         : 2026-11-23
# Content      : Reading preview of the narrative map, "Preview" view (SU010/FN033, TSK38)
# Design       : TSC (docs/conception/05_preview-FR/EN.md, TSK37)
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Service building the reading preview HTML of a narrative map (SU010/FN033, TSK38).

The preview is rendered read-only in the "Preview" view (PreviewWorkspace,
QTextBrowser). Decisions (docs/conception/05_preview-FR/EN.md, TSK37):

- sections, in order: a) project label, b) agent list "label (type)" (links
  to g), c) map label, d) journey list (links to e), e) per journey the blocks
  from Start in reading-sequence order (RG044) with label/type, content, the
  participating agents prefixed "Participations:" (TSK39 4.1, label TSK41),
  transitions inline, and the relationships prefixed "Relationships:"
  anchored on each block (agent labels 1 and 2, type, content, note - TSK39
  4.2: under the agents list, label TSK41) - the "state of relationships" is rendered
  under each anchor block, with no separate final section; f) orphan blocks
  (no incoming nor outgoing transition) of the current journey; g) all project
  agents "label (type)" (TSK39 4.4), content, note;
- branches of the journey not connected to the Start block are rendered after
  the main flow, grouped by chain and marked (RG044 already appends unreachable
  attached blocks after the reachable ones; nothing is omitted);
- journey=None -> all journeys; journey=J -> J only (active journey filter);
  agent_id -> the agent filter (RG063: blocks the agent participates in,
  transitions with both endpoints visible, relationships whose anchor block is
  visible; intersection with the journey filter RG064); elements outside the
  filters are omitted from the rendering;
- links are inert anchors (passive scroll only in the workspace); notes are
  resolved through build_note_index (anchors "#note-<kind>-<id>");
- the preview never marks the map nor the project as modified (read-only).
"""

from html import escape
from typing import Dict, List, Optional, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from core.models.data_model import (
        Agent, Block, Journey, NarrativeMap, Project, Relationship,
    )

from core.services.agent_filter_service import AgentFilterService
from core.services.journey_filter_service import JourneyFilterService
from core.services.participation_service import ParticipationService
from core.services.relationship_service import RelationshipService


def _esc(text) -> str:
    return escape(text if text is not None else "")


def _body(content) -> str:
    """Content as body text (line breaks preserved); empty content -> empty."""
    if not content:
        return ""
    return f"<p>{_esc(content).replace(chr(10), '<br>')}</p>"


def _label_anchor(kind: str, entity, label: str) -> str:
    """Label; when the entity carries a note, wrap it in an inert note anchor
    (hover tooltip resolved by the workspace through build_note_index)."""
    if getattr(entity, "note", None):
        return f'<a href="#note-{kind}-{entity.id}">{_esc(label)}</a>'
    return _esc(label)


class PreviewService:
    """Builds the read-only reading preview of a narrative map (TSK38)."""

    @staticmethod
    def build_note_index(project: 'Project', narrative_map: 'NarrativeMap') -> Dict[str, str]:
        """Map note anchors ("#note-<kind>-<id>") to their note text."""
        index: Dict[str, str] = {}
        for b in narrative_map.block:
            if b.note:
                index[f"#note-block-{b.id}"] = b.note
        for t in narrative_map.transition:
            if t.note:
                index[f"#note-transition-{t.id}"] = t.note
        for r in narrative_map.relationship:
            if r.note:
                index[f"#note-relationship-{r.id}"] = r.note
        for a in project.agent:
            if a.note:
                index[f"#note-agent-{a.id}"] = a.note
        return index

    @staticmethod
    def build_preview_html(project: 'Project', narrative_map: 'NarrativeMap',
                           journey: Optional['Journey'] = None,
                           agent_id: Optional[int] = None) -> str:
        """Return the reading preview HTML of the map.

        journey: None -> all journeys; a Journey -> that journey only (active
        journey filter). agent_id: agent filter (RG063), intersected with the
        journey filter (RG064). Elements outside the filters are omitted.
        """
        visible: Set[int] = JourneyFilterService.visible_block_ids(
            narrative_map, journey.id if journey is not None else None)
        if agent_id is not None:
            visible &= AgentFilterService.visible_block_ids(narrative_map, agent_id)

        journeys: List['Journey'] = [journey] if journey is not None else list(narrative_map.journey)
        agents: List['Agent'] = sorted(project.agent, key=lambda a: (a.lb, a.id))
        blocks_by_id = {b.id: b for b in narrative_map.block}

        parts = [f"<h1>{_esc(project.lb)}</h1>"]
        # b) agent list, links to the agents section g)
        parts.append("<h2>Agents</h2>")
        parts.append("<ul>")
        for a in agents:
            # TSK39 (4.4): the agent type in parentheses after the label
            parts.append(f'<li><a href="#agent-{a.id}">{_esc(a.lb)} ({_esc(a.typ)})</a></li>')
        parts.append("</ul>")
        # c) map label
        parts.append(f"<h2>{_esc(narrative_map.lb)}</h2>")
        # d) journey list, links to the journey sections e)
        parts.append("<h2>Journeys</h2>")
        parts.append("<ul>")
        for j in journeys:
            parts.append(f'<li><a href="#journey-{j.id}">{_esc(j.lb)}</a></li>')
        parts.append("</ul>")
        # e) journeys
        for j in journeys:
            parts.append(PreviewService._journey_section_html(
                narrative_map, j, blocks_by_id, agents, visible))
        # f) orphan blocks (no incoming nor outgoing transition)
        parts.append(PreviewService._orphans_section_html(narrative_map, blocks_by_id, journeys))
        # g) agents detail
        parts.append('<h2 id="agents">Agents</h2>')
        for a in agents:
            # TSK39 (4.4): the agent type in parentheses after the label
            parts.append(f'<h3 id="agent-{a.id}">{_label_anchor("agent", a, f"{a.lb} ({a.typ})")}</h3>')
            parts.append(_body(a.content))
        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Journey flow (section e)
    # ------------------------------------------------------------------
    @staticmethod
    def _journey_section_html(nm: 'NarrativeMap', journey: 'Journey',
                              blocks_by_id: Dict[int, 'Block'], agents: List['Agent'],
                              visible: Set[int]) -> str:
        attached = {jn.block_id for jn in nm.journey_node if jn.journey_id == journey.id}
        order = {jn.block_id: jn.sequence_order
                 for jn in nm.journey_node if jn.journey_id == journey.id}
        in_journey = sorted(attached, key=lambda bid: order.get(bid, 1 << 30))

        # reachable from the Start block through transitions within the journey (RG044 DFS)
        start = next((b for b in nm.block if b.typ == "Start"), None)
        reachable: Set[int] = set()
        if start is not None and start.id in attached:
            stack = [start.id]
            while stack:
                bid = stack.pop()
                if bid in reachable:
                    continue
                reachable.add(bid)
                for t in nm.transition:
                    if t.from_block_id == bid and t.to_block_id in attached \
                            and t.to_block_id not in reachable:
                        stack.append(t.to_block_id)

        shown = [bid for bid in in_journey if bid in visible]
        flow = [bid for bid in shown if bid in reachable]
        rest = [bid for bid in shown if bid not in reachable]

        parts = [f'<h2 id="journey-{journey.id}">{_esc(journey.lb)}</h2>']
        for bid in flow:
            parts.append(PreviewService._block_html(nm, blocks_by_id, agents, bid, attached, visible))
        if rest:
            parts.append(PreviewService._unreachable_chains_html(
                nm, blocks_by_id, agents, rest, attached, visible))
        return "\n".join(parts)

    @staticmethod
    def _unreachable_chains_html(nm, blocks_by_id, agents, rest, attached, visible) -> str:
        """Branches of the journey not connected to the Start block: rendered
        after the main flow, grouped by chain (root = no incoming transition
        within the journey), with a visible marker. Nothing is omitted."""
        incoming = {t.to_block_id for t in nm.transition
                    if t.to_block_id in attached and t.from_block_id in attached}
        roots = [bid for bid in rest if bid not in incoming]
        remaining = set(rest)
        parts = ["<p><em>Branch not connected to the Start block:</em></p>"]
        for root in roots:
            chain: List[int] = []
            stack = [root]
            while stack:
                bid = stack.pop()
                if bid in chain or bid not in remaining:
                    continue
                chain.append(bid)
                remaining.discard(bid)
                for t in nm.transition:
                    if t.from_block_id == bid and t.to_block_id in remaining:
                        stack.append(t.to_block_id)
            for bid in chain:
                parts.append(PreviewService._block_html(nm, blocks_by_id, agents, bid, attached, visible))
        for bid in sorted(remaining):  # cycles among unreachable blocks
            parts.append(PreviewService._block_html(nm, blocks_by_id, agents, bid, attached, visible))
        return "\n".join(parts)

    @staticmethod
    def _block_html(nm: 'NarrativeMap', blocks_by_id: Dict[int, 'Block'],
                    agents: List['Agent'], block_id: int, attached: Set[int],
                    visible: Set[int]) -> str:
        b = blocks_by_id[block_id]
        agent_by_id = {a.id: a for a in agents}
        parts = [f'<h3 id="block-{block_id}">'
                 f'{_label_anchor("block", b, f"{b.lb} ({b.typ})")}</h3>']
        parts.append(_body(b.content))
        # TSK39 (4.1): the participating agents, under the block content
        # (TSK39 4.3: the structured condition fields were removed in session 12)
        # TSK41 (session 12): prefix "Participations:" instead of "Agents:"
        participants = sorted(
            agent_by_id[p.agent_id].lb
            for p in ParticipationService.get_block_participations(nm, block_id)
            if p.agent_id in agent_by_id)
        if participants:
            parts.append(f"<p><em>Participations: {', '.join(_esc(lb) for lb in participants)}</em></p>")
        # transitions rendered inline (outgoing, within the journey, visible)
        for t in sorted(nm.transition, key=lambda t: t.id):
            if t.from_block_id == block_id and t.to_block_id in attached and t.to_block_id in visible:
                target = blocks_by_id[t.to_block_id]
                label = f"&rarr; {_esc(target.lb)}"
                if t.note:
                    label = f'<a href="#note-transition-{t.id}">{label}</a>'
                parts.append(f"<p>{label}</p>")
        # relationships anchored on this block (state of relationships, section e)
        # TSK41 (session 12): each relationship line is prefixed "Relationships:"
        for r in RelationshipService.get_block_relationships(nm, block_id):
            a1 = agent_by_id.get(r.agent_1_id)
            a2 = agent_by_id.get(r.agent_2_id)
            pair = f"{_esc(a1.lb if a1 else '?')} — {_esc(a2.lb if a2 else '?')}"
            label = f"{pair} : {_esc(r.typ)}"
            if r.note:
                label = f'<a href="#note-relationship-{r.id}">{label}</a>'
            parts.append(f"<p>Relationships: {label}</p>")
            parts.append(_body(r.content))
        return "\n".join(parts)

    # ------------------------------------------------------------------
    # Orphans (section f)
    # ------------------------------------------------------------------
    @staticmethod
    def _orphans_section_html(nm: 'NarrativeMap', blocks_by_id: Dict[int, 'Block'],
                              journeys: List['Journey']) -> str:
        """Orphan blocks: no incoming nor outgoing transition (adopted
        definition, TSK37). Scoped to the rendered journey(s) when a journey
        filter is active, else to the whole map; not restricted by the agent
        filter (orphans have no relation)."""
        touched = {t.from_block_id for t in nm.transition} | {t.to_block_id for t in nm.transition}
        if len(journeys) == 1:
            scope = {jn.block_id for jn in nm.journey_node if jn.journey_id == journeys[0].id}
        else:
            scope = set(blocks_by_id)
        orphans = [b for b in nm.block if b.id not in touched and b.id in scope]
        orphans.sort(key=lambda b: (b.lb, b.id))
        parts = ["<h2>Orphan blocks</h2>"]
        if not orphans:
            parts.append("<p><em>None</em></p>")
        else:
            parts.append("<ul>")
            for b in orphans:
                label = _label_anchor("block", b, f"{b.lb} ({b.typ})")
                parts.append(f"<li>{label}{_body(b.content)}</li>")
            parts.append("</ul>")
        return "\n".join(parts)
