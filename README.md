# AI Vision Overlay / HUD Platform

**Single-Player Games • External • Safe • Modular • Enterprise-Grade**

## Overview

An external AI-powered overlay/HUD system for single-player games that uses computer vision and OCR to understand game state and provide tactical awareness, accessibility assistance, and situational AI support.

### Core Philosophy
> "We do not read the game. We reconstruct game state through perception."

## Key Features

- **100% External**: No DLL injection, memory modification, or game hooks
- **AI Vision-Based**: Screen capture + computer vision + OCR only
- **Anti-Cheat Compliant**: Designed with security and compliance in mind
- **Modular Architecture**: Enterprise-grade plugin system
- **Real-Time Overlay**: Transparent HUD with tactical information
- **Profile System**: Game-specific configurations and rules

## Architecture

```
Game (untouched)
 → Screen Capture Engine
 → Frame Preprocessor
 → AI Vision Core
 → OCR & UI Parsing
 → Scene Understanding
 → Context & Event Engine
 → Decision & Priority Manager
 → Overlay / HUD Renderer
 → Control Panel / Profiles / Plugins
```

## Modules

### 1. Screen Capture Engine
- OS-native desktop capture (60-144 FPS)
- Multi-monitor support
- HDR-ready, ultra-low latency (<50ms)

### 2. Frame Preprocessor
- Scaling, normalization, ROI cropping
- Quality modes: QUALITY / BALANCED / PERFORMANCE

### 3. AI Vision Core
- Entity detection (enemies, NPCs, allies, objects)
- Real-time tracking with persistent IDs
- Pose & action recognition
- Threat scoring and proximity analysis

### 4. OCR & UI Parsing
- Health, stamina, mana extraction
- Cooldown timers and status icons
- Combat message parsing

### 5. Scene Understanding
- Temporal smoothing and noise reduction
- State confidence fusion
- Scene classification

### 6. Context & Event Engine
- Finite State Machine (FSM)
- Rule engine with priority logic
- Event emission and filtering

### 7. Decision & Priority Manager
- Event arbitration and escalation
- De-duplication with visual cooldowns
- Alert prioritization

### 8. Overlay / HUD Renderer
- Transparent, always-on-top overlay
- Click-through support, DPI aware
- Minimal, contextual visual design

### 9. Control Panel UI
- System status dashboard
- Profile manager
- No-code rule editor
- AI preview and diagnostics

### 10. Profile System
- Game-specific configurations
- Hot-switchable profiles
- Model, rule, and HUD theme management

### 11. Plugin/Extension System
- Strict API boundaries with versioning
- Sandbox isolation
- Hot-loadable custom modules

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/Games-AI-Tracker.git
cd Games-AI-Tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .

# Install development dependencies (optional)
pip install -e ".[dev]"
```

## Quick Start

```bash
# Launch control panel
ai-vision-control

# Or run directly
python -m core.main
```

## Configuration

Create a game profile in `profiles/`:

```yaml
name: "Dark Souls III"
game_id: "darksouls3"
capture:
  fps: 60
  roi: [0, 0, 1920, 1080]
ai:
  model: "yolov8n"
  confidence: 0.6
ocr:
  zones:
    health: [50, 900, 200, 50]
    stamina: [50, 950, 200, 30]
rules:
  - state: HIGH_RISK_COMBAT
    conditions:
      - enemy.distance < 3
      - enemy.threat_score > 0.7
    actions:
      - emit: CRITICAL_DANGER
hud:
  theme: "tactical_minimal"
  show_proximity_rings: true
```

## Performance Targets

- **End-to-end latency**: <50ms
- **CPU overhead**: <15%
- **GPU overhead**: <10%
- **Memory footprint**: <500MB

## Reliability & Fail-Safe

- **Watchdog** per module
- **Crash isolation** with safe mode
- **Graceful degradation** under load
- **Auto-recovery** mechanisms

## Development Roadmap

### MVP (v0.1)
- ✅ Screen capture engine
- ✅ Basic AI detection
- ✅ Simple HUD overlay
- ✅ Profile system

### V1 (v1.0)
- [ ] Full OCR integration
- [ ] Visual rule editor
- [ ] Plugin SDK release
- [ ] Multi-game profiles

### V2+ (Future)
- [ ] Advanced pose estimation
- [ ] Long-term behavior modeling
- [ ] Marketplace-ready plugins
- [ ] Cloud profile sync

## Project Structure

```
Games-AI-Tracker/
├── src/
│   ├── core/              # Core application logic
│   ├── modules/           # System modules (capture, AI, OCR, etc.)
│   ├── ui/                # Control panel and overlay UI
│   ├── plugins/           # Plugin system and base classes
│   └── utils/             # Shared utilities
├── profiles/              # Game-specific configuration profiles
├── models/                # AI model weights
├── docs/                  # Documentation
├── tests/                 # Unit and integration tests
└── examples/              # Example plugins and profiles
```

## Safety & Compliance

This system is designed for **single-player games only** and follows these principles:

- No game modification or reverse engineering
- No competitive advantage in multiplayer
- Respects anti-cheat systems
- Focused on accessibility and learning

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please read CONTRIBUTING.md for guidelines.

## Support

- Documentation: `/docs`
- Issues: GitHub Issues
- Discussions: GitHub Discussions
