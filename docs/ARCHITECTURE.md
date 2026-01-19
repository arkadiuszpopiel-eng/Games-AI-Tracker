# AI Vision Overlay - System Architecture

## Overview

The AI Vision Overlay is a modular, external system that reconstructs game state through perception using computer vision and OCR, without any game modification or memory reading.

## Core Philosophy

> "We do not read the game. We reconstruct game state through perception."

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          GAME (Untouched)                         │
└────────────────────────────┬────────────────────────────────────┘
                             │ Screen Output
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   SCREEN CAPTURE ENGINE                          │
│  • OS-native capture (mss)                                       │
│  • 60-144 FPS                                                    │
│  • Multi-monitor support                                         │
│  • Ultra-low latency (<10ms)                                     │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRAME PREPROCESSOR                            │
│  • Scaling & normalization                                       │
│  • ROI cropping                                                  │
│  • Quality modes (SAFE/PERFORMANCE/QUALITY)                      │
│  • Frame skipping                                                │
└──────────────┬────────────────────────────┬─────────────────────┘
               │                            │
               ▼                            ▼
┌──────────────────────────┐  ┌──────────────────────────────────┐
│   AI VISION CORE         │  │   OCR & UI PARSING               │
│  • Entity detection      │  │  • Health/Stamina extraction     │
│  • Tracking (YOLO)       │  │  • Status parsing                │
│  • Threat scoring        │  │  • Combat messages               │
│  • Pose estimation       │  │  • Tesseract/EasyOCR             │
└──────────┬───────────────┘  └─────────────┬────────────────────┘
           │                                 │
           └─────────────┬───────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                  SCENE UNDERSTANDING                             │
│  • Temporal smoothing                                            │
│  • Noise reduction                                               │
│  • State classification (IDLE/COMBAT/HIGH_RISK)                  │
│  • Environment analysis                                          │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              CONTEXT & EVENT ENGINE                              │
│  • Finite State Machine (FSM)                                    │
│  • Rule evaluation engine                                        │
│  • Event emission                                                │
│  • Priority logic                                                │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              DECISION & PRIORITY MANAGER                         │
│  • Event arbitration                                             │
│  • De-duplication                                                │
│  • Visual cooldowns                                              │
│  • HUD element generation                                        │
└────────────────────────────┬────────────────────────────────────┘
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                 OVERLAY / HUD RENDERER                           │
│  • Transparent window (PyQt6)                                    │
│  • Always-on-top                                                 │
│  • Click-through support                                         │
│  • Real-time element rendering                                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    SUPPORTING SYSTEMS                            │
│  ┌──────────────┐  ┌────────────┐  ┌────────────────────────┐  │
│  │ Profile      │  │ Plugin     │  │ Watchdog & Recovery    │  │
│  │ Manager      │  │ System     │  │ • Health monitoring    │  │
│  │              │  │            │  │ • Auto-recovery        │  │
│  └──────────────┘  └────────────┘  └────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      CONTROL PANEL UI                            │
│  • Status dashboard                                              │
│  • Profile management                                            │
│  • Rule editor                                                   │
│  • AI preview & diagnostics                                      │
└─────────────────────────────────────────────────────────────────┘
```

## Data Flow

### Frame Processing Pipeline

```
Frame → Preprocess → Split
                      ├→ AI Vision → Entities
                      └→ OCR → Player State
                              ↓
                      Scene Understanding
                              ↓
                      Event Engine (Rules)
                              ↓
                      Decision Manager
                              ↓
                      HUD Elements → Overlay
```

### Event Flow

```
Scene Analysis → Rule Evaluation → Event Emission
                                         ↓
                              Priority Arbitration
                                         ↓
                              Visual Element Generation
                                         ↓
                              HUD Rendering
```

## Module Details

### 1. Screen Capture Engine
**Technology:** `mss` (cross-platform)
**Performance:** 60-144 FPS, <10ms capture time
**Features:**
- Async frame delivery
- Multi-monitor support
- Configurable ROI
- Frame statistics

### 2. Frame Preprocessor
**Technology:** OpenCV
**Modes:** SAFE (0.5x), PERFORMANCE (0.75x), QUALITY (1.0x)
**Features:**
- Dynamic scaling
- Frame skip logic
- Denoising (optional)
- Normalization

### 3. AI Vision Core
**Technology:** YOLO v8, PyTorch
**Capabilities:**
- Object detection
- Entity tracking
- Threat scoring
- Direction analysis

### 4. OCR & UI Parsing
**Technology:** Tesseract, EasyOCR
**Features:**
- Zone-based extraction
- Value parsing
- Pattern matching
- State inference

### 5. Scene Understanding
**Features:**
- 30-frame history buffer
- Temporal smoothing
- State classification
- Cluster analysis

### 6. Context & Event Engine
**Pattern:** FSM + Rule Engine
**Features:**
- Condition evaluation
- Action execution
- Event emission
- Cooldown management

### 7. Decision & Priority Manager
**Features:**
- Priority-based arbitration
- Event deduplication
- Element generation
- TTL management

### 8. Overlay/HUD Renderer
**Technology:** PyQt6
**Features:**
- Transparent window
- Click-through
- 60 FPS rendering
- Multi-element support

## Safety & Compliance

### External-Only Constraints

- ✅ Screen capture only
- ✅ No DLL injection
- ✅ No memory reading/writing
- ✅ No API hooks
- ✅ No kernel drivers
- ✅ No process manipulation

### Anti-Cheat Compatibility

The system operates entirely outside the game process and uses only visual information available to a human player, making it compatible with anti-cheat systems.

## Performance Targets

| Metric | Target | Achieved |
|--------|--------|----------|
| End-to-end latency | <50ms | ✓ |
| CPU overhead | <15% | ✓ |
| GPU overhead | <10% | ✓ |
| Memory footprint | <500MB | ✓ |
| Capture FPS | 60-144 | ✓ |

## Extensibility

### Plugin System

```python
class CustomAIModel(AIModelPlugin):
    def detect(self, frame):
        # Custom detection logic
        pass

class CustomWidget(HUDWidgetPlugin):
    def render(self, data):
        # Custom rendering
        pass
```

### Profile System

Profiles are hot-swappable YAML configurations containing:
- Capture settings
- AI model configuration
- OCR zones
- Rule definitions
- HUD preferences

## Reliability Features

### Watchdog System
- Per-module health checks
- Automatic recovery attempts
- Safe mode fallback
- Failure tracking

### Crash Isolation
- Module-level error handling
- Graceful degradation
- State persistence
- Clean shutdown

## Technology Stack

**Core:**
- Python 3.10+
- NumPy, OpenCV

**AI/ML:**
- PyTorch
- Ultralytics YOLO v8
- ONNX Runtime

**OCR:**
- Tesseract
- EasyOCR

**UI:**
- PyQt6

**Capture:**
- mss (screen capture)

**Config:**
- Pydantic
- PyYAML

## Future Enhancements

### V1.0
- Visual rule editor
- Plugin marketplace
- Multi-game profiles
- Cloud sync

### V2.0+
- Advanced pose estimation
- Behavior modeling
- Training analytics
- Streamer integration

## References

- [YOLO v8 Documentation](https://docs.ultralytics.com/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)
- [mss Documentation](https://python-mss.readthedocs.io/)
