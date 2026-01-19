# AI Vision Overlay - Usage Guide

## Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/Games-AI-Tracker.git
cd Games-AI-Tracker

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Running the System

#### Option 1: Control Panel (GUI)

```bash
ai-vision-control
```

This launches the graphical control panel where you can:
- Select game profiles
- Monitor system status
- Configure AI settings
- Edit rules
- View diagnostics

#### Option 2: Command Line

```bash
# List available profiles
ai-vision --list-profiles

# Run with specific profile
ai-vision --profile darksouls3

# Run with default profile
ai-vision
```

## Creating a Game Profile

### Step 1: Create YAML File

Create a new file in `profiles/` directory:

```yaml
name: "Your Game"
game_id: "yourgame"
version: "1.0"

capture:
  fps: 60
  roi: null  # Full screen
  monitor: 0

ai:
  model: "yolov8n"
  confidence: 0.6
  device: "auto"

ocr:
  engine: "tesseract"
  language: "eng"
  zones:
    health: [x, y, width, height]
    stamina: [x, y, width, height]

rules: []

hud:
  theme: "tactical_minimal"
  opacity: 0.8

performance:
  mode: "PERFORMANCE"
```

### Step 2: Calibrate OCR Zones

1. Take a screenshot of your game
2. Use an image editor to find coordinates of UI elements
3. Update the `zones` section with correct coordinates

Example:
```yaml
ocr:
  zones:
    health: [50, 900, 200, 40]  # x, y, width, height
    stamina: [50, 945, 200, 30]
```

### Step 3: Define Rules

Rules trigger events based on game state:

```yaml
rules:
  - name: "low_health_alert"
    state: "*"  # Any state
    priority: 9
    conditions:
      - "player.hp < 30"
    actions:
      - type: "emit"
        payload: "LOW_HEALTH"
    cooldown: 5.0
```

### Step 4: Test Profile

```bash
ai-vision --profile yourgame
```

## Rule System

### Condition Syntax

Rules support various condition formats:

```yaml
# Numeric comparison
- "enemy.distance < 150"
- "player.hp > 50"
- "enemy.threat_score >= 0.7"

# Multiple conditions (AND logic)
conditions:
  - "enemy.distance < 200"
  - "player.hp < 50"
```

### Available Fields

**Enemy:**
- `enemy.distance` - Distance to closest enemy
- `enemy.threat_score` - Threat level (0-1)
- `enemy.velocity` - Movement speed

**Player:**
- `player.hp` - Current health
- `player.hp_max` - Maximum health
- `player.stamina` - Current stamina

**Environment:**
- `environment.total_enemies` - Number of enemies
- `environment.enemy_density` - Enemies per area
- `environment.avg_proximity` - Average enemy distance

**Scene:**
- `scene.state` - Current scene state
- `scene.confidence` - State confidence

### Action Types

**emit** - Trigger an event
```yaml
- type: "emit"
  payload: "CRITICAL_DANGER"
```

**log** - Log a message
```yaml
- type: "log"
  payload: "Enemy detected"
```

## HUD Customization

### Themes

Available themes:
- `tactical_minimal` - Clean, minimal tactical display
- `modern` - Modern gaming UI style
- `retro` - Retro/classic style

### Display Options

```yaml
hud:
  theme: "tactical_minimal"
  show_proximity_rings: true    # Rings around enemies
  show_direction_arrows: true   # Direction indicators
  show_health_warnings: true    # Health alerts
  opacity: 0.8                  # Overall transparency
  scale: 1.0                    # UI scale
```

## Performance Tuning

### Performance Modes

**SAFE Mode**
- Lowest resource usage
- 0.5x resolution
- Frame skipping enabled
- Best for low-end systems

```yaml
performance:
  mode: "SAFE"
```

**PERFORMANCE Mode** (Default)
- Balanced settings
- 0.75x resolution
- Adaptive quality
- Recommended for most users

```yaml
performance:
  mode: "PERFORMANCE"
```

**QUALITY Mode**
- Maximum accuracy
- Full resolution
- No frame skipping
- Best for high-end systems

```yaml
performance:
  mode: "QUALITY"
```

### AI Model Selection

Models listed by speed vs accuracy:

- `yolov8n` - Fastest, lowest accuracy
- `yolov8s` - Balanced
- `yolov8m` - Slower, better accuracy
- `yolov8l` - Slowest, best accuracy

```yaml
ai:
  model: "yolov8s"
  confidence: 0.6  # Detection threshold
  device: "auto"   # auto/cpu/cuda
```

## Troubleshooting

### High Latency

If you're experiencing >50ms latency:

1. **Reduce resolution**
   ```yaml
   performance:
     mode: "SAFE"
   ```

2. **Enable frame skipping**
   ```yaml
   performance:
     frame_skip: true
   ```

3. **Use smaller AI model**
   ```yaml
   ai:
     model: "yolov8n"
   ```

4. **Check CPU/GPU usage**
   - Open control panel diagnostics tab
   - Monitor resource usage

### OCR Not Working

1. **Verify zone coordinates**
   - Take screenshot
   - Check UI element positions
   - Update OCR zones

2. **Try different OCR engine**
   ```yaml
   ocr:
     engine: "easyocr"  # or "tesseract"
   ```

3. **Check language setting**
   ```yaml
   ocr:
     language: "eng"
   ```

### Overlay Not Showing

1. **Check overlay is enabled**
   - Control panel → HUD tab
   - Verify settings

2. **Verify game is in windowed/borderless mode**
   - Overlay works best with borderless window
   - May not work with exclusive fullscreen

3. **Check Windows settings**
   - Disable Game Mode
   - Check overlay permissions

### AI Detection Issues

1. **Adjust confidence threshold**
   ```yaml
   ai:
     confidence: 0.5  # Lower = more detections
   ```

2. **Try different model**
   ```yaml
   ai:
     model: "yolov8s"  # Larger model
   ```

3. **Check ROI settings**
   - Ensure capture region is correct
   - Test with full screen first

## Advanced Usage

### Custom Plugins

Create custom AI models or HUD widgets:

```python
from plugins import AIModelPlugin

class MyCustomModel(AIModelPlugin):
    def __init__(self):
        super().__init__()
        self.name = "CustomModel"

    def detect(self, frame):
        # Your detection logic
        return entities
```

### Multiple Monitors

```yaml
capture:
  monitor: 1  # 0 = primary, 1 = secondary, etc.
```

### Recording & Analysis

Enable telemetry for analysis:

```yaml
# In system config
telemetry_enabled: true
```

Logs saved to `logs/` directory.

## Best Practices

1. **Start with default profile**
   - Test with provided profiles first
   - Understand system behavior

2. **Calibrate OCR carefully**
   - Use precise coordinates
   - Test all UI elements

3. **Use appropriate performance mode**
   - SAFE for laptops/low-end
   - PERFORMANCE for most cases
   - QUALITY for analysis/streaming

4. **Monitor system resources**
   - Check diagnostics regularly
   - Adjust settings if needed

5. **Keep rules simple**
   - Start with basic rules
   - Add complexity gradually

## Safety Reminders

- ✅ **Single-player only**
- ✅ **No competitive advantage**
- ✅ **Accessibility focus**
- ⚠️ **Check game ToS**
- ⚠️ **Disable in multiplayer**

## Getting Help

- Documentation: `/docs`
- GitHub Issues: Report bugs and request features
- Examples: Check `examples/` directory
