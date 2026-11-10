# ---------------------------------------------------------------------
# Application  : Hyperscript
# Script       : data_model.py
# Version      : 1
# Date         : 2026-11-10
# Design       : TSC
# Build        : Mistral Vibe
# ---------------------------------------------------------------------
"""
Business data model of Hyperscript (docs/specification/07_data_model-*.json).

Project > NarrativeMap > Block / Transition / Participation / Relationship /
Journey / Journey_node, with Agent at project level. Entities use integer IDs
(unique per type within their container); Project and NarrativeMap use UUIDs.
The project file path is application state, not business data (FN005): it is
kept by ProjectService, never serialized.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import uuid4

# Project file format version (RG010): files without this exact version are
# rejected as incompatible (RG009/RG016: no planoscript migration).
FORMAT_VERSION = "1.0"

BLOCK_TYPES = ["Start", "Scene", "Pivot", "Condition", "End"]
AGENT_TYPES = ["Character", "Artefact"]
CONDITION_KINDS = ["Choice", "Artefact", "Skill", "Flag"]


def _to_iso(value):
    return value.isoformat() if isinstance(value, datetime) else value


def _from_iso(value):
    return datetime.fromisoformat(value) if isinstance(value, str) else value


def _entity_to_dict(obj) -> Dict[str, Any]:
    result = asdict(obj)
    for key in ("creation_date_time", "modification_date_time"):
        result[key] = _to_iso(result.get(key))
    return result


def _entity_from_dict(cls, data: Dict[str, Any]):
    data = dict(data)
    for key in ("creation_date_time", "modification_date_time"):
        if key in data:
            data[key] = _from_iso(data[key])
    return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def _check_int_id(obj, attrs) -> None:
    for attr in attrs:
        value = getattr(obj, attr)
        if not isinstance(value, int):
            setattr(obj, attr, int(value))


@dataclass
class Agent:
    """Agent of the project (Character or Artefact)."""

    id: int
    lb: str
    typ: str = "Character"  # AGENT_TYPES
    note: Optional[str] = None
    content: Optional[str] = None
    creation_date_time: datetime = field(default_factory=datetime.now)
    modification_date_time: Optional[datetime] = None

    def __post_init__(self):
        _check_int_id(self, ["id"])
        if self.typ not in AGENT_TYPES:
            raise ValueError(f"Invalid Agent.typ: {self.typ}. Must be one of: {AGENT_TYPES}")

    def to_dict(self) -> Dict[str, Any]:
        return _entity_to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Agent':
        return _entity_from_dict(cls, data)


@dataclass
class Block:
    """Narrative block; the structured condition is only carried by Condition blocks."""

    id: int
    lb: str
    typ: str = "Scene"  # BLOCK_TYPES, chosen at creation and immutable afterwards
    note: Optional[str] = None
    content: Optional[str] = None
    condition: Optional[Dict[str, Any]] = None  # only when typ == "Condition"
    creation_date_time: datetime = field(default_factory=datetime.now)
    modification_date_time: Optional[datetime] = None

    def __post_init__(self):
        _check_int_id(self, ["id"])
        if self.typ not in BLOCK_TYPES:
            raise ValueError(f"Invalid Block.typ: {self.typ}. Must be one of: {BLOCK_TYPES}")
        if self.condition is not None:
            if self.typ != "Condition":
                raise ValueError("Block.condition is only allowed when typ == 'Condition'")
            kind = self.condition.get("kind")
            if kind not in CONDITION_KINDS:
                raise ValueError(f"Invalid condition kind: {kind}. Must be one of: {CONDITION_KINDS}")

    def to_dict(self) -> Dict[str, Any]:
        return _entity_to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Block':
        return _entity_from_dict(cls, data)


@dataclass
class Transition:
    """Directed transition between two blocks (block -> block; free chaining, cycles allowed - RG028)."""

    id: int
    from_block_id: int  # Reference to Block.id
    to_block_id: int  # Reference to Block.id
    note: Optional[str] = None
    creation_date_time: datetime = field(default_factory=datetime.now)
    modification_date_time: Optional[datetime] = None

    def __post_init__(self):
        _check_int_id(self, ["id", "from_block_id", "to_block_id"])

    def to_dict(self) -> Dict[str, Any]:
        return _entity_to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transition':
        return _entity_from_dict(cls, data)


@dataclass
class Participation:
    """Participation: an agent present in a block (symmetric, matrix view)."""

    id: int
    block_id: int  # Reference to Block.id
    agent_id: int  # Reference to Agent.id
    note: Optional[str] = None
    creation_date_time: datetime = field(default_factory=datetime.now)
    modification_date_time: Optional[datetime] = None

    def __post_init__(self):
        _check_int_id(self, ["id", "block_id", "agent_id"])

    def to_dict(self) -> Dict[str, Any]:
        return _entity_to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Participation':
        return _entity_from_dict(cls, data)


@dataclass
class Relationship:
    """Directed, typed, binary agent-agent relationship, anchored to a block (RG035)."""

    id: int
    block_id: int  # Anchor block (Reference to Block.id)
    agent_a_id: int  # Reference to Agent.id
    agent_b_id: int  # Reference to Agent.id
    typ: str  # Relationship type, read from the configuration list (FN037)
    note: Optional[str] = None
    content: Optional[str] = None
    creation_date_time: datetime = field(default_factory=datetime.now)
    modification_date_time: Optional[datetime] = None

    def __post_init__(self):
        _check_int_id(self, ["id", "block_id", "agent_a_id", "agent_b_id"])

    def to_dict(self) -> Dict[str, Any]:
        return _entity_to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        return _entity_from_dict(cls, data)


@dataclass
class Journey:
    """Journey of the narrative map; exactly one is the default journey (RG039)."""

    id: int
    lb: str
    default: bool = False  # Default journey flag
    note: Optional[str] = None
    creation_date_time: datetime = field(default_factory=datetime.now)
    modification_date_time: Optional[datetime] = None

    def __post_init__(self):
        _check_int_id(self, ["id"])
        if not isinstance(self.default, bool):
            self.default = bool(self.default)

    def to_dict(self) -> Dict[str, Any]:
        return _entity_to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Journey':
        return _entity_from_dict(cls, data)


@dataclass
class Journey_node:
    """Attachment of a block to a journey (attachment is on blocks, not on transitions - RG041)."""

    id: int
    journey_id: int  # Reference to Journey.id
    block_id: int  # Reference to Block.id
    sequence_order: int  # Rank of the block in the journey sequence (computed by DFS)
    creation_date_time: datetime = field(default_factory=datetime.now)
    modification_date_time: Optional[datetime] = None

    def __post_init__(self):
        _check_int_id(self, ["id", "journey_id", "block_id", "sequence_order"])

    def to_dict(self) -> Dict[str, Any]:
        return _entity_to_dict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Journey_node':
        return _entity_from_dict(cls, data)


@dataclass
class NarrativeMap:
    """Narrative map: container for blocks, transitions, participations, relationships, journeys and journey nodes."""

    id: str  # UUID
    lb: str
    creation_date_time: datetime = field(default_factory=datetime.now)
    modification_date_time: Optional[datetime] = None
    active_journey_id: Optional[int] = None  # None = default journey

    block: List[Block] = field(default_factory=list)
    transition: List[Transition] = field(default_factory=list)
    participation: List[Participation] = field(default_factory=list)
    relationship: List[Relationship] = field(default_factory=list)
    journey: List[Journey] = field(default_factory=list)
    journey_node: List[Journey_node] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'lb': self.lb,
            'creation_date_time': _to_iso(self.creation_date_time),
            'modification_date_time': _to_iso(self.modification_date_time),
            'active_journey_id': self.active_journey_id,
            'block': [b.to_dict() for b in self.block],
            'transition': [t.to_dict() for t in self.transition],
            'participation': [p.to_dict() for p in self.participation],
            'relationship': [r.to_dict() for r in self.relationship],
            'journey': [j.to_dict() for j in self.journey],
            'journey_node': [n.to_dict() for n in self.journey_node],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NarrativeMap':
        return cls(
            id=data.get('id'),
            lb=data.get('lb'),
            creation_date_time=_from_iso(data.get('creation_date_time')),
            modification_date_time=_from_iso(data.get('modification_date_time')),
            active_journey_id=data.get('active_journey_id'),
            block=[Block.from_dict(b) for b in data.get('block', [])],
            transition=[Transition.from_dict(t) for t in data.get('transition', [])],
            participation=[Participation.from_dict(p) for p in data.get('participation', [])],
            relationship=[Relationship.from_dict(r) for r in data.get('relationship', [])],
            journey=[Journey.from_dict(j) for j in data.get('journey', [])],
            journey_node=[Journey_node.from_dict(n) for n in data.get('journey_node', [])],
        )

    def get_active_journey(self) -> Optional['Journey']:
        """Return the active journey; None active_journey_id means the default journey."""
        if self.active_journey_id is not None:
            for j in self.journey:
                if j.id == self.active_journey_id:
                    return j
        for j in self.journey:
            if j.default:
                return j
        return self.journey[0] if self.journey else None

    def get_next_id(self, entity_type: str) -> int:
        """Next available ID for an entity type (IDs are unique per type, not globally)."""
        lists = {
            'block': self.block,
            'transition': self.transition,
            'participation': self.participation,
            'relationship': self.relationship,
            'journey': self.journey,
            'journey_node': self.journey_node,
        }
        entities = lists.get(entity_type, [])
        existing = {e.id for e in entities}
        return max(existing) + 1 if existing else 1


@dataclass
class Project:
    """Project: id, label, timestamps, agents, narrative maps (single map in the MVP)."""

    id: str  # UUID
    lb: str
    creation_date_time: datetime = field(default_factory=datetime.now)
    modification_date_time: Optional[datetime] = None
    agent: List[Agent] = field(default_factory=list)
    narrative_maps: List[NarrativeMap] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'format_version': FORMAT_VERSION,
            'id': self.id,
            'lb': self.lb,
            'creation_date_time': _to_iso(self.creation_date_time),
            'modification_date_time': _to_iso(self.modification_date_time),
            'agent': [a.to_dict() for a in self.agent],
            'narrative_maps': [nm.to_dict() for nm in self.narrative_maps],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        return cls(
            id=data.get('id'),
            lb=data.get('lb'),
            creation_date_time=_from_iso(data.get('creation_date_time')),
            modification_date_time=_from_iso(data.get('modification_date_time')),
            agent=[Agent.from_dict(a) for a in data.get('agent', [])],
            narrative_maps=[NarrativeMap.from_dict(nm) for nm in data.get('narrative_maps', [])],
        )

    def get_next_id(self, entity_type: str) -> int:
        """Next available ID at project level (agents)."""
        if entity_type == 'agent':
            existing = {a.id for a in self.agent}
            return max(existing) + 1 if existing else 1
        raise ValueError(f"Unknown project-level entity type: {entity_type}")


def new_project_id() -> str:
    return str(uuid4())


def new_narrative_map_id() -> str:
    return str(uuid4())
