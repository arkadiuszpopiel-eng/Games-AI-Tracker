# AI Vision Overlay - Dokumentacja Techniczna

**System Nakładki Oparty na Sztucznej Inteligencji**

## 📋 Spis Treści

1. [Wprowadzenie](#wprowadzenie)
2. [Architektura Systemu](#architektura-systemu)
3. [Moduły](#moduły)
4. [Instalacja i Konfiguracja](#instalacja-i-konfiguracja)
5. [Użytkowanie](#użytkowanie)
6. [Tworzenie Profili](#tworzenie-profili)
7. [System Wtyczek](#system-wtyczek)
8. [Rozwiązywanie Problemów](#rozwiązywanie-problemów)

---

## Wprowadzenie

### Filozofia Projektu

> **"Nie czytamy gry. Rekonstruujemy stan gry poprzez percepcję."**

AI Vision Overlay to zaawansowany system nakładki dla gier jednoosobowych, który wykorzystuje:
- 🎯 **Wizję Komputerową** (YOLO v8) do detekcji obiektów
- 📝 **OCR** (Tesseract/EasyOCR) do odczytu interfejsu
- 🤖 **Sztuczną Inteligencję** do analizy sytuacji
- 🎮 **Nakładkę w Czasie Rzeczywistym** do wyświetlania informacji

### Kluczowe Zasady

✅ **100% Zewnętrzne** - Żadnej modyfikacji gry
✅ **Bezpieczne** - Bez wstrzykiwania DLL, bez czytania pamięci
✅ **Zgodne** - Respektuje systemy anti-cheat
✅ **Modularne** - Łatwe rozszerzanie i dostosowywanie

---

## Architektura Systemu

### Przegląd Pipeline'u

```
┌─────────────────────────────────────────┐
│           GRA (Nietknięta)              │
└──────────────────┬──────────────────────┘
                   │ Obraz ekranu
                   ▼
┌─────────────────────────────────────────┐
│    SILNIK PRZECHWYTYWANIA EKRANU        │
│  • mss (natywne API systemu)            │
│  • 60-144 FPS                           │
│  • Opóźnienie <10ms                     │
└──────────────────┬──────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│       PREPROCESOR KLATEK                │
│  • Skalowanie dynamiczne                │
│  • Przycinanie ROI                      │
│  • Tryby jakości                        │
└──────────┬────────────────┬─────────────┘
           │                │
           ▼                ▼
┌──────────────────┐  ┌──────────────────┐
│  AI VISION CORE  │  │   OCR & PARSING  │
│  • YOLO v8       │  │  • Zdrowie/Mana  │
│  • Tracking      │  │  • Status        │
│  • Threat Score  │  │  • Komunikaty    │
└────────┬─────────┘  └─────────┬────────┘
         │                      │
         └──────────┬───────────┘
                    ▼
┌─────────────────────────────────────────┐
│       ROZUMIENIE SCENY                  │
│  • Wygładzanie czasowe                  │
│  • Klasyfikacja stanu                   │
│  • Analiza środowiska                   │
└──────────────────┬──────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│    SILNIK KONTEKSTU I ZDARZEŃ           │
│  • Automat stanów (FSM)                 │
│  • Silnik reguł                         │
│  • Emisja zdarzeń                       │
└──────────────────┬──────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│    MENEDŻER DECYZJI                     │
│  • Arbitraż zdarzeń                     │
│  • Priorytetyzacja                      │
│  • Generowanie elementów HUD            │
└──────────────────┬──────────────────────┘
                   ▼
┌─────────────────────────────────────────┐
│       RENDERER NAKŁADKI                 │
│  • Przezroczyste okno (PyQt6)           │
│  • Zawsze na wierzchu                   │
│  • Click-through                        │
└─────────────────────────────────────────┘
```

### Przepływ Danych

```python
Klatka → Przetwarzanie → [AI Vision, OCR]
                              ↓
                      Analiza Sceny
                              ↓
                      Ocena Reguł
                              ↓
                      Decyzje
                              ↓
                      Elementy HUD → Wyświetlanie
```

---

## Moduły

### 1. 📹 Silnik Przechwytywania Ekranu

**Plik:** `src/modules/capture.py`

**Funkcjonalność:**
- Przechwytywanie ekranu w czasie rzeczywistym
- Obsługa wielu monitorów
- Konfigurowalny FPS (60-144)
- Region of Interest (ROI)

**Konfiguracja:**
```yaml
capture:
  monitor: 0              # Numer monitora
  fps: 60                 # Klatki na sekundę
  roi: [0, 0, 1920, 1080] # [x, y, szerokość, wysokość]
```

**Wydajność:**
- Opóźnienie przechwytywania: <10ms
- Zużycie CPU: ~5%
- Brak kompresji (pełna jakość)

---

### 2. 🔧 Preprocesor Klatek

**Plik:** `src/modules/preprocessor.py`

**Tryby Jakości:**

| Tryb | Skala | Pomiń klatki | Denoising |
|------|-------|--------------|-----------|
| QUALITY | 1.0x | 0 | ✅ |
| PERFORMANCE | 0.75x | 1 | ❌ |
| SAFE | 0.5x | 2 | ❌ |

**Zastosowanie:**
```python
preprocessor = FramePreprocessor(config)
processed = preprocessor.process(frame, roi=(100, 100, 800, 600))
```

---

### 3. 🤖 Rdzeń AI Vision

**Plik:** `src/modules/ai_vision.py`

**Modele Obsługiwane:**
- YOLOv8n (nano) - najszybszy, ~3ms
- YOLOv8s (small) - zbalansowany, ~5ms
- YOLOv8m (medium) - dokładny, ~10ms

**Detekcja Obiektów:**
```python
entities = ai_vision.detect(frame)
# Zwraca: List[Entity]
# - id: int (trwałe ID)
# - type: EntityType (ENEMY, ALLY, NPC, OBJECT)
# - bbox: BoundingBox
# - confidence: float (0-1)
# - threat_score: float (0-1)
# - velocity: float
# - direction: str
```

**Algorytm Threat Score:**
```
threat_score = (proximity * 0.5) + (size * 0.3) + (confidence * 0.2)

proximity = 1.0 - (distance_to_player / screen_height)
size = entity_area / screen_area * 50
```

---

### 4. 📝 OCR i Parsowanie UI

**Plik:** `src/modules/ocr.py`

**Silniki OCR:**
- **Tesseract** - szybki, dobry dla tekstu prostego
- **EasyOCR** - dokładniejszy, wolniejszy

**Strefy Detekcji:**
```yaml
ocr:
  zones:
    health: [50, 900, 200, 50]    # Pasek zdrowia
    stamina: [50, 950, 200, 30]   # Pasek staminy
    mana: [50, 1000, 200, 30]     # Pasek many
    status: [1700, 50, 200, 100]  # Ikony statusu
```

**Parsowanie Wartości:**
```python
# Automatyczne parsowanie:
"100/200" → {"current": 100, "max": 200}
"85%" → {"current": 85, "max": 100}
"1234" → {"current": 1234, "max": None}
```

---

### 5. 🧠 Rozumienie Sceny

**Plik:** `src/modules/scene_understanding.py`

**Stany Sceny:**
- `IDLE` - Bezczynność
- `EXPLORATION` - Eksploracja
- `COMBAT` - Walka
- `HIGH_RISK_COMBAT` - Walka wysokiego ryzyka
- `BOSS_FIGHT` - Walka z bossem
- `MENU` - Menu
- `LOADING` - Ładowanie

**Analiza Środowiska:**
```python
analysis = scene_understanding.analyze(entities, player_state)
# analysis.environment_data:
{
  "enemy_density": 2.5,           # Wrogów na 100k pixeli
  "avg_proximity": 450.0,         # Średnia odległość
  "threat_zones": [               # Strefy zagrożenia
    {
      "center": (960, 540),
      "enemy_count": 3,
      "avg_threat": 0.75
    }
  ]
}
```

---

### 6. ⚙️ Silnik Kontekstu i Zdarzeń

**Plik:** `src/modules/event_engine.py`

**Format Reguł:**
```yaml
rules:
  - name: "Ostrzeżenie o niskim zdrowiu"
    state: "*"                    # Każdy stan
    priority: 10
    cooldown: 5.0                 # 5 sekund
    conditions:
      - "player.hp < 30"
      - "player.hp_max > 0"
    actions:
      - type: "emit"
        payload: "LOW_HEALTH_WARNING"

  - name: "Niebezpieczeństwo z bliska"
    state: "HIGH_RISK_COMBAT"
    conditions:
      - "enemy.distance < 3"
      - "enemy.threat_score > 0.7"
    actions:
      - type: "emit"
        payload: "CRITICAL_DANGER"
```

**Operatory Warunków:**
- `<`, `>`, `<=`, `>=`, `==`, `!=`
- Pola: `player.*`, `enemy.*`, `scene.*`, `environment.*`

---

### 7. 🎯 Menedżer Decyzji i Priorytetów

**Plik:** `src/modules/decision_manager.py`

**Priorytety Zdarzeń:**
```
CRITICAL (5) → Czerwony
HIGH (4)     → Pomarańczowy
MEDIUM (3)   → Żółty
LOW (2)      → Biały
INFO (1)     → Szary
DEBUG (0)    → Przezroczysty
```

**Generowanie Elementów HUD:**
```python
hud_elements = decision_manager.process(events, analysis)
# Typy elementów:
# - "text"   : Tekst
# - "arrow"  : Strzałka kierunkowa
# - "ring"   : Pierścień bliskości
# - "zone"   : Strefa zagrożenia
# - "border" : Obramowanie ekranu
```

---

### 8. 🖥️ Renderer Nakładki / HUD

**Plik:** `src/modules/overlay.py`

**Właściwości Okna:**
- Frameless (bez ramki)
- Always-on-top (zawsze na wierzchu)
- Transparent background (przezroczyste tło)
- Click-through (kliknięcia przez okno)
- DPI-aware (świadomość DPI)

**Renderowanie:**
```python
# Tekst z konturem
font = QFont("Arial", 32, QFont.Weight.Bold)
color = QColor(255, 0, 0, 255)  # RGBA

# Strzałka kierunkowa
painter.drawPolygon([
    QPoint(x, y + size),     # Dół
    QPoint(x - size//2, y),  # Lewo
    QPoint(x + size//2, y)   # Prawo
])

# Pierścień
painter.drawEllipse(QPoint(x, y), radius, radius)
```

---

## Instalacja i Konfiguracja

### Automatyczna Instalacja (Zalecane)

```batch
:: Uruchom automatyczny build
build.bat

:: Instalator wykonuje:
:: 1. Sprawdzenie Python 3.10+
:: 2. Utworzenie venv
:: 3. Instalację wszystkich zależności
:: 4. Pobranie modeli AI
:: 5. Weryfikację instalacji
:: 6. Opcjonalnie: testy
```

### Struktura Po Instalacji

```
Games-AI-Tracker/
├── venv/                      # Środowisko wirtualne
│   ├── Scripts/
│   └── Lib/
├── src/                       # Kod źródłowy
├── profiles/                  # Profile gier
│   ├── darksouls3.yaml
│   └── eldenring.yaml
├── models/                    # Modele AI
│   └── yolov8n.pt
├── logs/                      # Logi aplikacji
├── docs/                      # Dokumentacja
├── build.bat                  # Instalator
└── run.bat                    # Uruchamianie
```

---

## Użytkowanie

### Szybkie Uruchomienie

```batch
:: Metoda 1: Skrypt uruchamiający (ZALECANE)
run.bat

:: Metoda 2: Panel sterowania
python -m ui.control_panel

:: Metoda 3: Tryb konsolowy
python -m core.main --profile darksouls3

:: Metoda 4: Lista profili
python -m core.main --list-profiles
```

### Panel Sterowania

**Zakładki:**
1. **📊 Status** - Stan systemu, FPS, wydajność
2. **🎮 Profile** - Zarządzanie profilami gier
3. **🤖 AI Vision** - Konfiguracja modelu, podgląd detekcji
4. **⚙️ Reguły** - Edytor reguł
5. **🎯 HUD** - Ustawienia nakładki
6. **🔧 Diagnostyka** - Logi, monitoring

**Skróty Klawiszowe:**
- `Ctrl+S` - Start/Stop
- `Ctrl+P` - Zmiana profilu
- `Ctrl+Q` - Wyjście

---

## Tworzenie Profili

### Szablon Profilu

Utwórz plik `profiles/mojagra.yaml`:

```yaml
name: "Moja Gra"
game_id: "mojagra"
version: "1.0"

# =======================
# PRZECHWYTYWANIE
# =======================
capture:
  monitor: 0              # 0 = główny monitor
  fps: 60                 # Klatki na sekundę
  roi: null               # null = pełny ekran lub [x, y, w, h]

# =======================
# WYDAJNOŚĆ
# =======================
performance:
  mode: "PERFORMANCE"     # SAFE | PERFORMANCE | QUALITY | DEBUG
  max_latency_ms: 50      # Maksymalne opóźnienie
  frame_skip: false       # Pomijanie klatek

# =======================
# MODEL AI
# =======================
ai:
  model: "yolov8n"        # yolov8n | yolov8s | yolov8m
  device: "auto"          # auto | cpu | cuda
  confidence: 0.6         # Próg pewności (0.0-1.0)
  iou_threshold: 0.45     # IoU dla NMS
  classes: []             # [] = wszystkie klasy

# =======================
# OCR
# =======================
ocr:
  engine: "tesseract"     # tesseract | easyocr
  language: "eng"         # pol dla polskiego
  zones:
    health: [50, 900, 200, 50]     # [x, y, szerokość, wysokość]
    stamina: [50, 950, 200, 30]
    mana: [50, 1000, 200, 30]
    # Dodaj własne strefy

# =======================
# REGUŁY
# =======================
rules:
  - name: "Niskie zdrowie"
    state: "*"
    priority: 10
    cooldown: 3.0
    conditions:
      - "player.hp < 30"
    actions:
      - type: "emit"
        payload: "LOW_HEALTH_WARNING"

  - name: "Wróg z bliska"
    state: "COMBAT"
    conditions:
      - "enemy.distance < 200"
      - "enemy.threat_score > 0.5"
    actions:
      - type: "emit"
        payload: "ENEMY_CLOSE"

# =======================
# HUD
# =======================
hud:
  theme: "tactical_minimal"
  opacity: 0.8
  show_fps: false
  show_proximity_rings: true
  show_direction_arrows: true
  show_threat_zones: true

# =======================
# WATCHDOG
# =======================
watchdog:
  enabled: true
  check_interval: 5.0
  recovery_attempts: 3
```

### Kalibracja Stref OCR

**Narzędzie Pomocnicze:**

Utwórz `tools/calibrate_ocr.py`:

```python
import cv2
import numpy as np
from mss import mss

def calibrate():
    with mss() as sct:
        monitor = sct.monitors[1]
        img = sct.grab(monitor)
        frame = np.array(img)

        # Pokaż obraz
        cv2.imshow("Kalibracja - Kliknij obszary", frame)

        # Wybierz obszary
        roi = cv2.selectROI("Kalibracja", frame)
        print(f"Strefa: [{roi[0]}, {roi[1]}, {roi[2]}, {roi[3]}]")

        cv2.destroyAllWindows()

if __name__ == "__main__":
    calibrate()
```

Uruchom: `python tools/calibrate_ocr.py`

---

## System Wtyczek

### Tworzenie Wtyczki AI Model

```python
# plugins/custom_detector.py

from src.plugins import AIModelPlugin
import numpy as np

class CustomDetector(AIModelPlugin):
    """Własny detektor obiektów."""

    def __init__(self):
        super().__init__()
        self.name = "CustomDetector"
        self.version = "1.0.0"
        self.api_version = "1.0"

    def initialize(self, config):
        """Inicjalizacja wtyczki."""
        # Załaduj swój model
        return True

    def detect(self, frame):
        """Detekcja obiektów."""
        # Twoja logika detekcji
        entities = []
        # ... przetwarzanie ...
        return entities

    def shutdown(self):
        """Czyszczenie zasobów."""
        pass
```

### Tworzenie Wtyczki HUD Widget

```python
# plugins/custom_widget.py

from src.plugins import HUDWidgetPlugin
from PyQt6.QtGui import QPainter

class CustomWidget(HUDWidgetPlugin):
    """Własny widget HUD."""

    def __init__(self):
        super().__init__()
        self.name = "CustomWidget"
        self.version = "1.0.0"

    def render(self, painter: QPainter, data):
        """Renderowanie widgetu."""
        # Twoja logika renderowania
        painter.drawText(100, 100, "Custom Widget!")
```

### Rejestracja Wtyczki

```yaml
# profiles/mojagra.yaml

plugins:
  ai_models:
    - plugin: "plugins.custom_detector.CustomDetector"
      enabled: true
      config:
        threshold: 0.7

  widgets:
    - plugin: "plugins.custom_widget.CustomWidget"
      enabled: true
```

---

## Rozwiązywanie Problemów

### 🔴 Problem: Python nie znaleziony

**Rozwiązanie:**
```batch
1. Pobierz Python 3.10+ z python.org
2. Podczas instalacji zaznacz "Add Python to PATH"
3. Restart komputera
4. Uruchom: build.bat
```

### 🔴 Problem: Błędy importu modułów

**Rozwiązanie:**
```batch
:: Reinstalacja zależności
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### 🔴 Problem: OCR nie działa

**Rozwiązanie:**
```batch
:: Instalacja Tesseract (Windows)
:: 1. Pobierz z: https://github.com/UB-Mannheim/tesseract/wiki
:: 2. Zainstaluj w: C:\Program Files\Tesseract-OCR
:: 3. Dodaj do PATH: C:\Program Files\Tesseract-OCR

:: Lub użyj EasyOCR
pip install easyocr
```

### 🔴 Problem: Niska wydajność

**Rozwiązania:**
```yaml
# 1. Zmień tryb wydajności
performance:
  mode: "PERFORMANCE"  # lub SAFE
  frame_skip: true

# 2. Użyj mniejszego modelu
ai:
  model: "yolov8n"  # Najszybszy

# 3. Ogranicz ROI
capture:
  roi: [400, 200, 1120, 880]  # Centrum ekranu
```

### 🔴 Problem: Nakładka nie widoczna

**Rozwiązanie:**
```python
# Sprawdź czy PyQt6 zainstalowane
pip install PyQt6

# Sprawdź uprawnienia nakładki (Windows)
# Uruchom jako Administrator
```

### 🔴 Problem: Model AI nie pobiera się

**Rozwiązanie:**
```batch
:: Ręczne pobranie modelu
python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"

:: Lub pobierz z:
:: https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
:: Umieść w: models/yolov8n.pt
```

---

## FAQ

### ❓ Czy działa z grami wieloosobowymi?

**NIE.** System jest zaprojektowany **tylko dla gier jednoosobowych**. Użycie w grach multiplayer może naruszać regulaminy i zasady fair play.

### ❓ Czy jest zgodny z systemami anti-cheat?

**TAK.** System działa całkowicie zewnętrznie, nie modyfikuje gry ani pamięci. Jednak zawsze sprawdź regulamin konkretnej gry.

### ❓ Jakie są wymagania sprzętowe?

**Minimalne:**
- CPU: 4 rdzenie, 2.5 GHz
- RAM: 8 GB
- GPU: Zintegrowana (dla CPU mode)
- Python: 3.10+

**Zalecane:**
- CPU: 6+ rdzeni, 3.0+ GHz
- RAM: 16 GB
- GPU: NVIDIA (CUDA) dla AI
- Python: 3.11

### ❓ Czy mogę używać własnych modeli AI?

**TAK.** System obsługuje wtyczki - możesz dodać własne modele poprzez system wtyczek.

### ❓ Jak dodać obsługę polskiego tekstu OCR?

```yaml
ocr:
  engine: "tesseract"
  language: "pol"  # Polski język
```

Lub dla EasyOCR:
```yaml
ocr:
  engine: "easyocr"
  language: "pl"
```

---

## Wsparcie Techniczne

### 📞 Kontakt

- **GitHub Issues**: https://github.com/yourusername/Games-AI-Tracker/issues
- **Dokumentacja**: `docs/`
- **Przykłady**: `examples/`

### 📚 Dodatkowe Zasoby

- `docs/ARCHITECTURE.md` - Szczegółowa architektura (PL)
- `docs/API_PL.md` - Dokumentacja API (PL)
- `examples/` - Przykładowe wtyczki i profile

---

## Licencja

MIT License - Zobacz plik `LICENSE`

**WAŻNE:** System przeznaczony tylko dla gier jednoosobowych. Użytkownik ponosi odpowiedzialność za zgodność z regulaminami gier.

---

**Wersja dokumentacji:** 1.0.0
**Data aktualizacji:** 2026-01-19
**Język:** Polski 🇵🇱
