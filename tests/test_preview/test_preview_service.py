# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : test_preview_service.py
# Version      : 1
# Date         : 2026-11-23
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""Unit tests for PreviewService (TSK38) - the reading preview HTML of a
narrative map (SU010/FN033, conception docs/conception/05_preview-FR/EN.md).

Covered: sections a)-g) in order, RG044 reading order of the journey flow,
transitions inline, relationships anchored under their block (point e),
orphan blocks (no incoming nor outgoing transition), unreachable branches
marked, journey filter, agent filter (RG063/RG064 intersection), HTML
escaping, note anchors, and the read-only guarantee (never marks modified).
"""

from core.models.data_model import Block, Journey, Participation
from core.services.project_service import ProjectService
from core.services.journey_service import JourneyService
from core.services.transition_service import TransitionService
from core.services.journey_sequence_service import JourneySequenceService
from core.services.preview_service import PreviewService
from usecases.project_management import CreateProjectUseCase
from usecases.agent_management.create_agent_usecase import CreateAgentUseCase
from usecases.relationship_management.create_relationship_usecase import CreateRelationshipUseCase


def make_project():
    service = ProjectService()
    project = CreateProjectUseCase(service).execute()
    return service, project, project.narrative_maps[0]


def add_block(nm, typ, lb=None, journey_id=None, note=None, content=None, condition=None):
    block = Block(id=nm.get_next_id('block'), lb=lb or typ, typ=typ,
                  note=note, content=content, condition=condition)
    nm.block.append(block)
    JourneyService.attach_block(nm, block.id, journey_id or nm.journey[0].id)
    return block


def start_block(nm):
    return next(b for b in nm.block if b.typ == "Start")


def test_sections_a_to_g_in_order():
    service, project, nm = make_project()
    a = CreateAgentUseCase(service).execute(lb="Alice")
    j = nm.journey[0]
    html = PreviewService.build_preview_html(project, nm)
    i_h1 = html.index(f"<h1>{project.lb}</h1>")                       # a) project
    i_agents_list = html.index("<h2>Agents</h2>")                      # b) agent list
    i_map = html.index(f"<h2>{nm.lb}</h2>")                             # c) map label
    i_journeys = html.index("<h2>Journeys</h2>")                       # d) journey list
    i_journey_sec = html.index(f'<h2 id="journey-{j.id}">')            # e) journey flow
    i_orphans = html.index("<h2>Orphan blocks</h2>")                   # f) orphans
    i_agents_sec = html.index('<h2 id="agents">')                      # g) agents detail
    assert i_h1 < i_agents_list < i_map < i_journeys < i_journey_sec < i_orphans < i_agents_sec
    # b) links to g), d) links to e)
    assert f'<a href="#agent-{a.id}">Alice</a>' in html
    assert f'<a href="#journey-{j.id}">' in html
    # g) agent detail with type and anchor
    assert f'<h3 id="agent-{a.id}">' in html


def test_flow_follows_rg044_order_and_renders_block_fields():
    service, project, nm = make_project()
    start = start_block(nm)
    s1 = add_block(nm, "Scene", "S1", content="line1\nline2")
    s2 = add_block(nm, "Scene", "S2")
    p = add_block(nm, "Pivot", "P1")
    TransitionService.create_transition(nm, start.id, s1.id)   # t1
    TransitionService.create_transition(nm, start.id, p.id)     # t2
    TransitionService.create_transition(nm, s1.id, s2.id)       # t3
    JourneySequenceService.recompute_all(nm)  # RG044 ranks
    html = PreviewService.build_preview_html(project, nm)
    # RG044 order: Start, S1, S2, P1 (branch of S1 explored before P1)
    i_start = html.index(f'id="block-{start.id}"')
    i_s1 = html.index(f'id="block-{s1.id}"')
    i_s2 = html.index(f'id="block-{s2.id}"')
    i_p = html.index(f'id="block-{p.id}"')
    assert i_start < i_s1 < i_s2 < i_p
    # label + type, content with preserved line break
    assert "S1 (Scene)" in html[i_s1:i_s2]
    assert "line1<br>line2" in html[i_s1:i_s2]


def test_transition_rendered_inline_with_note_anchor():
    service, project, nm = make_project()
    start = start_block(nm)
    s1 = add_block(nm, "Scene", "S1")
    t = TransitionService.create_transition(nm, start.id, s1.id, note="go on")
    html = PreviewService.build_preview_html(project, nm)
    i_start = html.index(f'id="block-{start.id}"')
    i_s1 = html.index(f'id="block-{s1.id}"')
    seg = html[i_start:i_s1]
    assert "&rarr;" in seg and "S1" in seg
    assert f'#note-transition-{t.id}' in seg


def test_condition_block_renders_its_condition():
    service, project, nm = make_project()
    add_block(nm, "Condition", "C1", condition={"kind": "Choice", "options": "A, B"})
    html = PreviewService.build_preview_html(project, nm)
    assert "Condition Choice" in html
    assert "options=A, B" in html


def test_relationships_rendered_under_their_anchor_block():
    service, project, nm = make_project()
    start = start_block(nm)
    s1 = add_block(nm, "Scene", "S1")
    s2 = add_block(nm, "Scene", "S2")
    TransitionService.create_transition(nm, start.id, s1.id)
    TransitionService.create_transition(nm, s1.id, s2.id)
    JourneySequenceService.recompute_all(nm)
    a1 = CreateAgentUseCase(service).execute(lb="Alice")
    a2 = CreateAgentUseCase(service).execute(lb="Bob")
    nm.participation.append(Participation(id=nm.get_next_id('participation'), block_id=s1.id, agent_id=a1.id))
    nm.participation.append(Participation(id=nm.get_next_id('participation'), block_id=s1.id, agent_id=a2.id))
    r = CreateRelationshipUseCase(service).execute(a1.id, a2.id, "ally", s1.id,
                                                   note="rel note", content="rel content")
    html = PreviewService.build_preview_html(project, nm)
    i_s1 = html.index(f'id="block-{s1.id}"')
    i_s2 = html.index(f'id="block-{s2.id}"')
    seg = html[i_s1:i_s2]  # the anchor block's section, up to the next block
    assert "Alice" in seg and "Bob" in seg and "ally" in seg
    assert f'#note-relationship-{r.id}' in seg
    assert "rel content" in seg


def test_orphan_blocks_are_blocks_without_any_transition():
    service, project, nm = make_project()
    start = start_block(nm)
    s1 = add_block(nm, "Scene", "S1")
    TransitionService.create_transition(nm, start.id, s1.id)
    orphan = add_block(nm, "Scene", "Orphan1")  # attached, no transition at all
    # a second journey with its own orphan: scoped out when the journey filter is on
    j2 = Journey(id=nm.get_next_id('journey'), lb="J2", default=False)
    nm.journey.append(j2)
    orphan2 = add_block(nm, "Scene", "Orphan2", journey_id=j2.id)
    html_all = PreviewService.build_preview_html(project, nm)
    i_orph = html_all.index("<h2>Orphan blocks</h2>")
    i_agents = html_all.index('<h2 id="agents">')
    seg = html_all[i_orph:i_agents]
    assert "Orphan1 (Scene)" in seg
    assert "Orphan2 (Scene)" in seg
    assert "S1 (Scene)" not in seg  # connected block is not an orphan
    # journey filter on j1: orphans scoped to j1
    html_j1 = PreviewService.build_preview_html(project, nm, journey=nm.journey[0])
    seg1 = html_j1[html_j1.index("<h2>Orphan blocks</h2>"):html_j1.index('<h2 id="agents">')]
    assert "Orphan1 (Scene)" in seg1
    assert "Orphan2" not in html_j1


def test_unreachable_branch_marked_and_rendered_after_the_flow():
    service, project, nm = make_project()
    start = start_block(nm)
    s1 = add_block(nm, "Scene", "S1")
    TransitionService.create_transition(nm, start.id, s1.id)
    u1 = add_block(nm, "Scene", "U1")
    u2 = add_block(nm, "Scene", "U2")
    TransitionService.create_transition(nm, u1.id, u2.id)  # chain not connected to Start
    JourneySequenceService.recompute_all(nm)
    html = PreviewService.build_preview_html(project, nm)
    marker = "Branch not connected to the Start block"
    assert marker in html
    i_s1 = html.index(f'id="block-{s1.id}"')
    i_marker = html.index(marker)
    i_u1 = html.index(f'id="block-{u1.id}"')
    i_u2 = html.index(f'id="block-{u2.id}"')
    assert i_s1 < i_marker < i_u1 < i_u2


def test_journey_filter_renders_only_that_journey():
    service, project, nm = make_project()
    j1 = nm.journey[0]
    j2 = Journey(id=nm.get_next_id('journey'), lb="J2", default=False)
    nm.journey.append(j2)
    b_j2 = add_block(nm, "Scene", "OnlyJ2", journey_id=j2.id)
    html_all = PreviewService.build_preview_html(project, nm)
    assert f'id="journey-{j1.id}"' in html_all and f'id="journey-{j2.id}"' in html_all
    assert f'id="block-{b_j2.id}"' in html_all
    html_j1 = PreviewService.build_preview_html(project, nm, journey=j1)
    assert f'id="journey-{j1.id}"' in html_j1
    assert f'id="journey-{j2.id}"' not in html_j1
    assert f'id="block-{b_j2.id}"' not in html_j1


def test_agent_filter_omits_non_participating_blocks_rg063_rg064():
    service, project, nm = make_project()
    start = start_block(nm)
    s1 = add_block(nm, "Scene", "S1")
    s2 = add_block(nm, "Scene", "S2")
    TransitionService.create_transition(nm, start.id, s1.id)
    TransitionService.create_transition(nm, s1.id, s2.id)
    a = CreateAgentUseCase(service).execute(lb="Alice")
    nm.participation.append(Participation(id=nm.get_next_id('participation'), block_id=s1.id, agent_id=a.id))
    html = PreviewService.build_preview_html(project, nm, agent_id=a.id)
    assert f'id="block-{s1.id}"' in html
    assert f'id="block-{start.id}"' not in html
    assert f'id="block-{s2.id}"' not in html
    # RG064: intersection with the journey filter -> empty when disjoint
    j2 = Journey(id=nm.get_next_id('journey'), lb="J2", default=False)
    nm.journey.append(j2)
    b_j2 = add_block(nm, "Scene", "OnlyJ2", journey_id=j2.id)
    html_both = PreviewService.build_preview_html(project, nm, journey=j2, agent_id=a.id)
    assert f'id="block-{b_j2.id}"' not in html_both
    assert f'id="block-{s1.id}"' not in html_both


def test_html_escaping_of_labels_and_contents():
    service, project, nm = make_project()
    add_block(nm, "Scene", lb="<script>alert(1)</script>", content="a<b>&c")
    html = PreviewService.build_preview_html(project, nm)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "a&lt;b&gt;&amp;c" in html


def test_note_index_resolves_note_anchors():
    service, project, nm = make_project()
    b = add_block(nm, "Scene", "Noted", note="block note")
    a = CreateAgentUseCase(service).execute(lb="Alice", note="agent note")
    html = PreviewService.build_preview_html(project, nm)
    assert f'#note-block-{b.id}' in html
    assert f'#note-agent-{a.id}' in html
    index = PreviewService.build_note_index(project, nm)
    assert index[f'#note-block-{b.id}'] == "block note"
    assert index[f'#note-agent-{a.id}'] == "agent note"


def test_preview_never_marks_the_project_as_modified():
    service, project, nm = make_project()
    add_block(nm, "Scene", "S1")
    service.set_modified(False)
    PreviewService.build_preview_html(project, nm)
    PreviewService.build_preview_html(project, nm, journey=nm.journey[0], agent_id=None)
    PreviewService.build_note_index(project, nm)
    assert service.is_modified is False
