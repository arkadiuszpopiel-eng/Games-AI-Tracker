# AI Vision Overlay - API Reference

## Core Types

### Entity

Represents a detected entity in the game.

```python
@dataclass
class Entity:
    id: int                          # Persistent tracking ID
    type: EntityType                 # ENEMY, ALLY, NPC, etc.
    bbox: BoundingBox                # Position and size
    confidence: float                # Detection confidence (0-1)
    velocity: float                  # Movement speed
    direction: Optional[str]         # Movement direction
    pose: Optional[str]              # Pose/action
    threat_score: float              # Threat level (0-1)
    distance_estimate: float         # Estimated distance
    metadata: Dict[str, Any]         # Additional data
    timestamp: float                 # Detection time
```

### SceneAnalysis

Complete scene analysis result.

```python
@dataclass
class SceneAnalysis:
    state: SceneState                # Scene classification
    confidence: float                # Classification confidence
    entities: List[Entity]           # Detected entities
    player_state: PlayerState        # Player information
    environment_data: Dict[str, Any] # Environmental analysis
    timestamp: float                 # Analysis time
```

### Event

System event for triggering actions.

```python
@dataclass
class Event:
    type: str                        # Event type
    priority: EventPriority          # Priority level
    data: Dict[str, Any]             # Event data
    timestamp: float                 # Event time
    source: Optional[str]            # Event source
    cooldown: float                  # Cooldown duration
```

## Modules

### Screen Capture Engine

```python
from modules.capture import ScreenCaptureEngine
from core.config import CaptureConfig

config = CaptureConfig(fps=60, monitor=0)
engine = ScreenCaptureEngine(config)

engine.start()
frame = engine.get_frame(timeout=0.1)
engine.stop()
```

### AI Vision Core

```python
from modules.ai_vision import AIVisionCore
from core.config import AIModelConfig

config = AIModelConfig(model="yolov8n", confidence=0.6)
vision = AIVisionCore(config)

entities = vision.detect(frame)

for entity in entities:
    print(f"Entity {entity.id}: {entity.type} at {entity.bbox}")
```

### OCR Engine

```python
from modules.ocr import OCREngine
from core.config import OCRConfig

config = OCRConfig(
    engine="tesseract",
    zones={"health": [50, 900, 200, 40]}
)
ocr = OCREngine(config)

results = ocr.extract_zones(frame)
player_state = ocr.extract_player_state(results)

print(f"HP: {player_state.hp}/{player_state.hp_max}")
```

### Scene Understanding

```python
from modules.scene_understanding import SceneUnderstanding

scene = SceneUnderstanding(history_size=30)

analysis = scene.analyze(entities, player_state)

print(f"Scene: {analysis.state} ({analysis.confidence})")
print(f"Entities: {len(analysis.entities)}")
```

### Event Engine

```python
from modules.event_engine import ContextEngine
from core.config import Rule

rules = [
    Rule(
        name="low_health",
        state="*",
        conditions=["player.hp < 30"],
        actions=[{"type": "emit", "payload": "LOW_HEALTH"}]
    )
]

engine = ContextEngine(rules)
events = engine.process(analysis)

for event in events:
    print(f"Event: {event.type} (priority: {event.priority})")
```

### Decision Manager

```python
from modules.decision_manager import DecisionManager

manager = DecisionManager(max_concurrent_alerts=3)
hud_elements = manager.process(events, analysis)

for element in hud_elements:
    print(f"HUD: {element.type} at {element.position}")
```

### HUD Renderer

```python
from modules.overlay import HUDRenderer
from core.config import HUDConfig

config = HUDConfig(theme="tactical_minimal", opacity=0.8)
renderer = HUDRenderer(config)

renderer.start()
renderer.render(hud_elements)
renderer.stop()
```

## Plugin Development

### AI Model Plugin

```python
from plugins import AIModelPlugin

class CustomAIModel(AIModelPlugin):
    def __init__(self):
        super().__init__()
        self.name = "CustomModel"
        self.version = "1.0.0"
        self.api_version = "1.0"

    def initialize(self, config):
        # Load your model
        return True

    def detect(self, frame):
        # Perform detection
        entities = []
        # ... detection logic
        return entities

    def shutdown(self):
        # Cleanup
        pass
```

### HUD Widget Plugin

```python
from plugins import HUDWidgetPlugin

class CustomWidget(HUDWidgetPlugin):
    def __init__(self):
        super().__init__()
        self.name = "CustomWidget"
        self.version = "1.0.0"

    def initialize(self, config):
        return True

    def render(self, data):
        # Render custom widget
        pass

    def shutdown(self):
        pass
```

### Rule Pack Plugin

```python
from plugins import RulePackPlugin
from core.config import Rule

class CustomRulePack(RulePackPlugin):
    def __init__(self):
        super().__init__()
        self.name = "SoulsLikeRules"
        self.version = "1.0.0"

    def initialize(self, config):
        return True

    def get_rules(self):
        return [
            Rule(
                name="boss_alert",
                state="HIGH_RISK_COMBAT",
                conditions=["enemy.threat_score > 0.85"],
                actions=[{"type": "emit", "payload": "BOSS_FIGHT"}]
            )
        ]

    def shutdown(self):
        pass
```

## Profile Management

### Profile Manager

```python
from utils.profile_manager import ProfileManager

manager = ProfileManager()

# List profiles
profiles = manager.list_profiles()

# Activate profile
manager.activate_profile("darksouls3")

# Get active profile
profile = manager.get_active_profile()

# Create new profile
new_profile = manager.create_default_profile("mygame", "My Game")
manager.save_profile(new_profile)
```

## Watchdog System

### Watchdog

```python
from utils.watchdog import Watchdog

watchdog = Watchdog(check_interval=5.0, max_failures=3)

# Register module
watchdog.register_module(
    name="capture",
    check_fn=lambda: capture_engine.is_running,
    recovery_fn=lambda: capture_engine.start()
)

watchdog.start()

# Check status
status = watchdog.get_status()
print(f"Module status: {status}")

watchdog.stop()
```

## Main Pipeline

### AI Vision Pipeline

```python
from core.pipeline import AIVisionPipeline
from core.config import GameProfile, SystemConfig

profile = GameProfile.from_yaml("profiles/darksouls3.yaml")
system_config = SystemConfig()

pipeline = AIVisionPipeline(profile, system_config)

pipeline.start()

# Get statistics
stats = pipeline.get_statistics()
print(f"FPS: {stats['fps']:.1f}")
print(f"Latency: {stats['avg_latency_ms']:.1f}ms")

pipeline.stop()
```

## Configuration

### Game Profile

```python
from core.config import GameProfile, CaptureConfig, AIModelConfig

profile = GameProfile(
    name="My Game",
    game_id="mygame",
    capture=CaptureConfig(fps=60, monitor=0),
    ai=AIModelConfig(model="yolov8s", confidence=0.65)
)

# Save to file
profile.to_yaml("profiles/mygame.yaml")

# Load from file
loaded = GameProfile.from_yaml("profiles/mygame.yaml")
```

### System Config

```python
from core.config import SystemConfig
from pathlib import Path

config = SystemConfig(
    log_level="INFO",
    log_dir=Path("logs"),
    profile_dir=Path("profiles"),
    watchdog_interval=5.0,
    crash_recovery=True
)
```

## Events

### Event Types

Predefined event types:
- `LOW_HEALTH` - Player health below threshold
- `CRITICAL_HEALTH` - Player health critically low
- `CRITICAL_DANGER` - Immediate threat detected
- `HIGH_ENEMY_DENSITY` - Many enemies nearby
- `BOSS_FIGHT` - Boss encounter detected
- `AMBUSH_WARNING` - Potential ambush detected

### Event Priority

```python
class EventPriority(Enum):
    DEBUG = 0
    INFO = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5
```

## HUD Elements

### Element Types

- `text` - Text display
- `arrow` - Direction arrow
- `ring` - Proximity ring
- `zone` - Threat zone
- `border` - Screen border effect

### Creating HUD Elements

```python
from core.types import HUDElement

element = HUDElement(
    type="text",
    position=(960, 100),
    data={"text": "Warning", "size": 24, "bold": True},
    color=(255, 0, 0, 255),  # RGBA
    priority=5,
    ttl=3.0  # Time to live in seconds
)
```

## Utility Functions

### Logging

```python
from loguru import logger

logger.info("Information message")
logger.warning("Warning message")
logger.error("Error message")
logger.debug("Debug message")
```

### Performance Monitoring

```python
import time

start = time.perf_counter()
# ... code to measure
elapsed_ms = (time.perf_counter() - start) * 1000

print(f"Operation took {elapsed_ms:.1f}ms")
```

## Error Handling

All modules implement graceful error handling:

```python
try:
    result = module.process(data)
except Exception as e:
    logger.error(f"Processing error: {e}")
    # Fallback to safe mode or skip frame
```

## Best Practices

1. **Always check is_running** before operations
2. **Use context managers** where appropriate
3. **Handle exceptions** gracefully
4. **Monitor performance** metrics
5. **Log important events** at appropriate levels
6. **Clean up resources** in shutdown methods
