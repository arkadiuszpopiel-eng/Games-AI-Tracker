"""
Detekcja i optymalizacja dla różnych trybów okna gry.
Wspiera: Fullscreen, Borderless Windowed, Windowed
"""

import sys
from typing import Optional, Tuple, Dict
from dataclasses import dataclass
from loguru import logger

if sys.platform == "win32":
    try:
        import win32gui
        import win32process
        import win32api
        import win32con
        WINDOWS_AVAILABLE = True
    except ImportError:
        WINDOWS_AVAILABLE = False
        logger.warning("pywin32 not available - limited window detection")
else:
    WINDOWS_AVAILABLE = False


@dataclass
class WindowInfo:
    """Informacje o oknie gry."""
    title: str
    hwnd: int
    rect: Tuple[int, int, int, int]  # (left, top, right, bottom)
    is_fullscreen: bool
    is_borderless: bool
    is_windowed: bool
    width: int
    height: int
    process_name: str


class WindowDetector:
    """
    Detektor trybu okna gry.

    Wspierane tryby:
    - Fullscreen Exclusive (pełny ekran ekskluzywny)
    - Borderless Windowed (pełne okno bez ramek) ⭐ ZALECANE
    - Windowed (okno z ramką)
    """

    def __init__(self):
        self.game_window: Optional[WindowInfo] = None

    def detect_game_window(self, process_name: Optional[str] = None) -> Optional[WindowInfo]:
        """
        Wykryj okno gry.

        Args:
            process_name: Opcjonalna nazwa procesu gry (np. "DarkSoulsIII.exe")

        Returns:
            WindowInfo lub None jeśli nie znaleziono
        """
        if not WINDOWS_AVAILABLE:
            logger.warning("Detekcja okien dostępna tylko na Windows z pywin32")
            return None

        if process_name:
            window = self._find_window_by_process(process_name)
        else:
            window = self._find_foreground_window()

        if window:
            self.game_window = window
            self._log_window_info(window)

        return window

    def _find_window_by_process(self, process_name: str) -> Optional[WindowInfo]:
        """Znajdź okno po nazwie procesu."""
        if not WINDOWS_AVAILABLE:
            return None

        found_window = None

        def callback(hwnd, _):
            nonlocal found_window
            if win32gui.IsWindowVisible(hwnd):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    import psutil
                    process = psutil.Process(pid)
                    if process.name().lower() == process_name.lower():
                        found_window = self._analyze_window(hwnd)
                        return False  # Stop enumeration
                except:
                    pass
            return True

        win32gui.EnumWindows(callback, None)
        return found_window

    def _find_foreground_window(self) -> Optional[WindowInfo]:
        """Znajdź aktywne okno na pierwszym planie."""
        if not WINDOWS_AVAILABLE:
            return None

        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            return self._analyze_window(hwnd)
        return None

    def _analyze_window(self, hwnd: int) -> WindowInfo:
        """Analizuj okno i określ jego tryb."""
        if not WINDOWS_AVAILABLE:
            return None

        # Pobierz informacje
        title = win32gui.GetWindowText(hwnd)
        rect = win32gui.GetWindowRect(hwnd)
        left, top, right, bottom = rect
        width = right - left
        height = bottom - top

        # Sprawdź styl okna
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        ex_style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)

        # Pobierz nazwę procesu
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        process_name = "unknown"
        try:
            import psutil
            process = psutil.Process(pid)
            process_name = process.name()
        except:
            pass

        # Określ tryb okna
        has_caption = bool(style & win32con.WS_CAPTION)
        has_border = bool(style & win32con.WS_BORDER)
        is_maximized = win32gui.IsZoomed(hwnd)

        # Pobierz rozdzielczość ekranu
        screen_width = win32api.GetSystemMetrics(0)
        screen_height = win32api.GetSystemMetrics(1)

        # Logika detekcji trybu
        is_fullscreen = False
        is_borderless = False
        is_windowed = False

        if not has_caption and not has_border and width >= screen_width and height >= screen_height:
            # Borderless Windowed - pełne okno bez ramek ⭐
            is_borderless = True
        elif width >= screen_width and height >= screen_height and is_maximized:
            # Może być fullscreen exclusive
            is_fullscreen = True
        elif has_caption or has_border:
            # Windowed z ramką
            is_windowed = True
        else:
            # Domyślnie borderless jeśli zajmuje cały ekran
            if width >= screen_width * 0.9 and height >= screen_height * 0.9:
                is_borderless = True
            else:
                is_windowed = True

        return WindowInfo(
            title=title,
            hwnd=hwnd,
            rect=rect,
            is_fullscreen=is_fullscreen,
            is_borderless=is_borderless,
            is_windowed=is_windowed,
            width=width,
            height=height,
            process_name=process_name
        )

    def _log_window_info(self, window: WindowInfo):
        """Loguj informacje o oknie."""
        mode = "NIEZNANY"
        if window.is_borderless:
            mode = "BORDERLESS WINDOWED ⭐ (Zalecane)"
        elif window.is_fullscreen:
            mode = "FULLSCREEN EXCLUSIVE"
        elif window.is_windowed:
            mode = "WINDOWED (z ramką)"

        logger.info(f"🎮 Wykryto okno gry: {window.title}")
        logger.info(f"   Tryb: {mode}")
        logger.info(f"   Rozdzielczość: {window.width}x{window.height}")
        logger.info(f"   Proces: {window.process_name}")
        logger.info(f"   HWND: {window.hwnd}")

    def get_capture_region(self) -> Optional[Dict]:
        """
        Zwróć region do przechwytywania dla wykrytego okna.

        Returns:
            Dict z regionem lub None dla pełnego ekranu
        """
        if not self.game_window:
            return None

        window = self.game_window

        # Dla borderless windowed i fullscreen - pełny ekran
        if window.is_borderless or window.is_fullscreen:
            return None  # mss użyje pełnego ekranu

        # Dla windowed - przytnij do okna (bez ramki)
        if window.is_windowed:
            left, top, right, bottom = window.rect

            # Uwzględnij grubość ramki (około 8px) i tytuł (około 30px)
            border = 8
            titlebar = 30

            return {
                "left": left + border,
                "top": top + titlebar,
                "width": window.width - (2 * border),
                "height": window.height - titlebar - border
            }

        return None

    def print_recommendations(self):
        """Wyświetl rekomendacje dla wykrytego trybu."""
        if not self.game_window:
            print("\n⚠️  Nie wykryto okna gry")
            return

        window = self.game_window

        print("\n" + "="*60)
        print("REKOMENDACJE DLA TRYBU OKNA")
        print("="*60)

        if window.is_borderless:
            print("✅ Tryb: BORDERLESS WINDOWED (Pełne okno bez ramek)")
            print("\nZalety:")
            print("  ✅ Najlepszy dla capture - brak opóźnień")
            print("  ✅ Łatwe przełączanie między aplikacjami")
            print("  ✅ Overlay działa płynnie")
            print("  ✅ Brak problemów z Alt+Tab")
            print("\nUstawienia:")
            print("  • Capture FPS: 60-144 (pełna wydajność)")
            print("  • ROI: auto (pełny ekran)")
            print("  • Latencja: <5ms")

        elif window.is_fullscreen:
            print("⚠️  Tryb: FULLSCREEN EXCLUSIVE")
            print("\nWady:")
            print("  ⚠️  Może mieć problemy z Alt+Tab")
            print("  ⚠️  Overlay może nie działać płynnie")
            print("  ⚠️  Capture może być wolniejszy")
            print("\n💡 REKOMENDACJA:")
            print("  Zmień w ustawieniach gry na:")
            print("  'Pełne okno bez ramek' / 'Borderless Windowed'")
            print("\nJeśli nie możesz zmienić:")
            print("  • Capture FPS: 60 (ogranicz)")
            print("  • ROI: użyj mniejszego regionu")

        elif window.is_windowed:
            print("ℹ️  Tryb: WINDOWED (Okno z ramką)")
            print("\nUwagi:")
            print("  ℹ️  Capture będzie przycinał ramkę")
            print("  ℹ️  Overlay może zakrywać część UI")
            print("\n💡 REKOMENDACJA:")
            print("  Dla najlepszej wydajności zmień na:")
            print("  'Pełne okno bez ramek' / 'Borderless Windowed'")

        print("="*60 + "\n")


def test_window_detection():
    """Test detekcji okien."""
    print("🔍 Test detekcji trybu okna...\n")

    detector = WindowDetector()

    # Test 1: Aktywne okno
    print("Test 1: Wykrywanie aktywnego okna")
    window = detector.detect_game_window()

    if window:
        print(f"✅ Wykryto okno: {window.title}")
        print(f"   Tryb: ", end="")
        if window.is_borderless:
            print("Borderless Windowed ⭐")
        elif window.is_fullscreen:
            print("Fullscreen")
        elif window.is_windowed:
            print("Windowed")

        detector.print_recommendations()

        # Region capture
        region = detector.get_capture_region()
        if region:
            print(f"\nRegion capture: {region}")
        else:
            print("\nRegion capture: Pełny ekran")

    else:
        print("❌ Nie wykryto okna")
        print("\n💡 Wskazówka:")
        print("   1. Upewnij się że gra jest uruchomiona")
        print("   2. Kliknij w okno gry aby było aktywne")
        print("   3. Uruchom test ponownie")


if __name__ == "__main__":
    test_window_detection()
