"""Core type definitions and data structures."""

from typing import NamedTuple, List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import time


class EntityType(Enum):
    """Entity classification types."""
    UNKNOWN = "unknown"
    ENEMY = "enemy"
    ALLY = "ally"
    NPC = "npc"
    OBJECT = "object"
    ITEM = "item"
    HAZARD = "hazard"


class SceneState(Enum):
    """Scene state classifications."""
    IDLE = "idle"
    EXPLORATION = "exploration"
    COMBAT = "combat"
    HIGH_RISK_COMBAT = "high_risk_combat"
    BOSS_FIGHT = "boss_fight"
    MENU = "menu"
    LOADING = "loading"
    CUTSCENE = "cutscene"


class EventPriority(Enum):
    """Event priority levels."""
    DEBUG = 0
    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5


@dataclass
class BoundingBox:
    """Bounding box representation."""
    x: int
    y: int
    width: int
    height: int

    @property
    def center(self) -> tuple[int, int]:
        """Get center point."""
        return (self.x + self.width // 2, self.y + self.height // 2)

    @property
    def area(self) -> int:
        """Get area."""
        return self.width * self.height


@dataclass
class Entity:
    """Detected entity representation."""
    id: int
    type: EntityType
    bbox: BoundingBox
    confidence: float
    velocity: float = 0.0
    direction: Optional[str] = None
    pose: Optional[str] = None
    threat_score: float = 0.0
    distance_estimate: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class Frame:
    """Captured frame data."""
    frame_id: int
    buffer: Any  # numpy array
    width: int
    height: int
    timestamp_ns: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OCRResult:
    """OCR extraction result."""
    zone: str
    text: str
    confidence: float
    bbox: Optional[BoundingBox] = None
    parsed_value: Any = None


@dataclass
class PlayerState:
    """Player state information."""
    hp: Optional[int] = None
    hp_max: Optional[int] = None
    stamina: Optional[int] = None
    stamina_max: Optional[int] = None
    mana: Optional[int] = None
    mana_max: Optional[int] = None
    combat_state: Optional[str] = None
    status_effects: List[str] = field(default_factory=list)
    alerts: List[str] = field(default_factory=list)


@dataclass
class SceneAnalysis:
    """Scene understanding result."""
    state: SceneState
    confidence: float
    entities: List[Entity]
    player_state: PlayerState
    environment_data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)


@dataclass
class Event:
    """System event."""
    type: str
    priority: EventPriority
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    source: Optional[str] = None
    cooldown: float = 0.0


@dataclass
class HUDElement:
    """HUD element to render."""
    type: str  # arrow, ring, text, icon, etc.
    position: tuple[int, int]
    data: Dict[str, Any]
    color: tuple[int, int, int, int]  # RGBA
    priority: int = 0
    ttl: Optional[float] = None  # Time to live in seconds
