# AI Vision Overlay / Nakładka HUD

**Gry Jednoosobowe • Zewnętrzna • Bezpieczna • Modularna • Klasy Enterprise**

## Przegląd

Zewnętrzny system nakładki oparty na sztucznej inteligencji dla gier jednoosobowych, który wykorzystuje wizję komputerową i OCR do zrozumienia stanu gry oraz zapewnienia wsparcia taktycznego, pomocy w dostępności i asysty sytuacyjnej AI.

### Filozofia Projektu
> "Nie czytamy gry. Rekonstruujemy stan gry poprzez percepcję."

## Kluczowe Cechy

- **100% Zewnętrzne**: Bez wstrzykiwania DLL, modyfikacji pamięci czy hooków gry
- **Oparte na AI Vision**: Tylko przechwytywanie ekranu + wizja komputerowa + OCR
- **Zgodne z Anti-Cheat**: Zaprojektowane z myślą o bezpieczeństwie i zgodności
- **Architektura Modularna**: System wtyczek klasy enterprise
- **Nakładka w Czasie Rzeczywistym**: Przezroczysty HUD z informacjami taktycznymi
- **System Profili**: Konfiguracje specyficzne dla każdej gry

## Architektura

```
Gra (nietknięta)
 → Silnik Przechwytywania Ekranu
 → Preprocesor Klatek
 → Rdzeń AI Vision
 → OCR i Parsowanie UI
 → Rozumienie Sceny
 → Silnik Kontekstu i Zdarzeń
 → Menedżer Decyzji i Priorytetów
 → Renderer Nakładki / HUD
 → Panel Sterowania / Profile / Wtyczki
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

## Instalacja

### 🚀 Automatyczna Instalacja (ZALECANE)

```bash
# Uruchom automatyczny build - zrobi wszystko za Ciebie!
build.bat
```

### Lub Instalacja Ręczna

```bash
# Klonuj repozytorium
git clone https://github.com/yourusername/Games-AI-Tracker.git
cd Games-AI-Tracker

# Utwórz wirtualne środowisko
python -m venv venv
venv\Scripts\activate

# Zainstaluj zależności
pip install -e .

# Zainstaluj zależności deweloperskie (opcjonalne)
pip install -e ".[dev]"
```

## Szybki Start

```bash
# Uruchom aplikację (automatycznie)
run.bat

# Lub uruchom panel sterowania
ai-vision-control

# Lub bezpośrednio
python -m core.main
```

## Automatyczny Build

System posiada **pełną automatyzację**:

**`build.bat`** - Kompletna instalacja:
- ✅ Sprawdzenie środowiska Python
- ✅ Utworzenie wirtualnego środowiska
- ✅ Instalacja wszystkich zależności
- ✅ Pobranie modeli AI
- ✅ Weryfikacja instalacji
- ✅ Uruchomienie testów

**`run.bat`** - Szybkie uruchomienie:
- ✅ Aktywacja środowiska
- ✅ Sprawdzenie zależności
- ✅ Uruchomienie aplikacji

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

## 🎮 Tryby Okna Gry

**⭐ ZALECANE: Pełne okno bez ramek (Borderless Windowed)**

AI Vision działa z **wszystkimi trybami okna**:
- ✅ **Borderless Windowed** - najlepszy! (<5ms latencja)
- ✅ Fullscreen Exclusive - działa (10-15ms latencja)
- ✅ Windowed - pełne wsparcie

### Dlaczego Borderless Windowed?
```
✅ Najlepsza wydajność capture
✅ Overlay zawsze widoczny
✅ Łatwe Alt+Tab
✅ Zero problemów
```

**Jak włączyć w grze:**
```
Ustawienia → Grafika → Tryb wyświetlania:
"Pełne okno bez ramek" / "Borderless Windowed"
```

📖 Więcej: `docs/TRYBY_OKNA_PL.md`

## Cele Wydajnościowe

- **Opóźnienie end-to-end**: <50ms (Borderless: <5ms capture!)
- **Obciążenie CPU**: <15%
- **Obciążenie GPU**: <10%
- **Zużycie pamięci**: <500MB

## Niezawodność i Zabezpieczenia

- **Watchdog** dla każdego modułu
- **Izolacja awarii** z trybem bezpiecznym
- **Graceful degradation** pod obciążeniem
- **Mechanizmy auto-recovery**

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
