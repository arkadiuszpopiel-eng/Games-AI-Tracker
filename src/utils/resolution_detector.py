"""
Wykrywanie i dostosowywanie do różnych rozdzielczości ekranu.
Wspiera: 16:9, 21:9 (ultrawide), 32:9, 4:3, 16:10
"""

from typing import Tuple, Dict
from dataclasses import dataclass
from loguru import logger


@dataclass
class DisplayConfig:
    """Konfiguracja wyświetlania dla danej rozdzielczości."""
    width: int
    height: int
    aspect_ratio: str
    aspect_float: float
    is_ultrawide: bool
    roi_default: Tuple[int, int, int, int]
    ui_scale: float
    hud_positions: Dict[str, Tuple[int, int]]


class ResolutionDetector:
    """
    Detektor i konfigurator rozdzielczości ekranu.

    Wspierane formaty:
    - 16:9 (1920x1080, 2560x1440, 3840x2160) - Standard
    - 21:9 (2560x1080, 3440x1440) - Ultrawide
    - 32:9 (3840x1080, 5120x1440) - Super ultrawide
    - 16:10 (1920x1200, 2560x1600) - Klasyczny
    - 4:3 (1024x768, 1280x1024) - Legacy
    """

    # Znane rozdzielczości
    KNOWN_RESOLUTIONS = {
        # 16:9 - Standard
        (1920, 1080): "16:9 Full HD",
        (2560, 1440): "16:9 QHD",
        (3840, 2160): "16:9 4K UHD",

        # 21:9 - Ultrawide
        (2560, 1080): "21:9 UW-FHD",
        (3440, 1440): "21:9 UW-QHD",
        (3840, 1600): "21:9 UW-QHD+",

        # 32:9 - Super ultrawide
        (3840, 1080): "32:9 DFHD",
        (5120, 1440): "32:9 DQHD",

        # 16:10 - Klasyczny
        (1920, 1200): "16:10 WUXGA",
        (2560, 1600): "16:10 WQXGA",

        # 4:3 - Legacy
        (1024, 768): "4:3 XGA",
        (1280, 1024): "4:3 SXGA",
    }

    def __init__(self):
        self.current_config: DisplayConfig = None

    def detect(self, width: int, height: int) -> DisplayConfig:
        """
        Wykryj i skonfiguruj dla danej rozdzielczości.

        Args:
            width: Szerokość ekranu
            height: Wysokość ekranu

        Returns:
            DisplayConfig z optymalnymi ustawieniami
        """
        # Oblicz aspect ratio
        aspect_float = width / height
        aspect_ratio = self._get_aspect_ratio_name(aspect_float)
        is_ultrawide = aspect_float >= 2.0  # 21:9 i więcej

        # Nazwa rozdzielczości
        res_name = self.KNOWN_RESOLUTIONS.get((width, height), f"{width}x{height}")

        logger.info(f"🖥️  Wykryto rozdzielczość: {res_name} ({aspect_ratio})")

        if is_ultrawide:
            logger.info("📐 Wykryto ultrawide - dostosowuję interfejs")

        # Oblicz ROI (region of interest) - dla ultrawide wycinamy boki
        roi_default = self._calculate_roi(width, height, aspect_float)

        # Skala UI - dla większych rozdzielczości większe elementy
        ui_scale = self._calculate_ui_scale(width, height)

        # Pozycje elementów HUD - dostosowane do aspect ratio
        hud_positions = self._calculate_hud_positions(width, height, aspect_float)

        config = DisplayConfig(
            width=width,
            height=height,
            aspect_ratio=aspect_ratio,
            aspect_float=aspect_float,
            is_ultrawide=is_ultrawide,
            roi_default=roi_default,
            ui_scale=ui_scale,
            hud_positions=hud_positions
        )

        self.current_config = config
        return config

    def _get_aspect_ratio_name(self, aspect_float: float) -> str:
        """Określ nazwę aspect ratio."""
        if 1.25 <= aspect_float < 1.35:
            return "4:3"
        elif 1.55 <= aspect_float < 1.65:
            return "16:10"
        elif 1.75 <= aspect_float < 1.8:
            return "16:9"
        elif 2.3 <= aspect_float < 2.4:
            return "21:9"
        elif 3.5 <= aspect_float < 3.7:
            return "32:9"
        else:
            return f"{aspect_float:.2f}:1"

    def _calculate_roi(self, width: int, height: int, aspect: float) -> Tuple[int, int, int, int]:
        """
        Oblicz optymalny ROI dla danego aspect ratio.

        Dla ultrawide wycinamy boki aby skupić się na centrum.

        Returns:
            (x, y, width, height) - ROI lub (0, 0, width, height) dla pełnego ekranu
        """
        if aspect >= 2.3:  # 21:9 ultrawide
            # Dla ultrawide wycinamy 20% z każdej strony
            crop_x = int(width * 0.15)
            crop_y = 0
            crop_width = width - (2 * crop_x)
            crop_height = height

            logger.info(f"   ROI dla ultrawide: centrum {crop_width}x{crop_height}")
            return (crop_x, crop_y, crop_width, crop_height)

        elif aspect >= 3.5:  # 32:9 super ultrawide
            # Dla super ultrawide wycinamy więcej
            crop_x = int(width * 0.25)
            crop_y = 0
            crop_width = width - (2 * crop_x)
            crop_height = height

            logger.info(f"   ROI dla super ultrawide: centrum {crop_width}x{crop_height}")
            return (crop_x, crop_y, crop_width, crop_height)

        else:
            # Standardowe proporcje - pełny ekran
            return (0, 0, width, height)

    def _calculate_ui_scale(self, width: int, height: int) -> float:
        """
        Oblicz skalę UI dla danej rozdzielczości.

        Bazuje na 1920x1080 jako 1.0
        """
        base_width = 1920
        base_height = 1080

        # Średnia skala z width i height
        scale_w = width / base_width
        scale_h = height / base_height
        scale = (scale_w + scale_h) / 2

        # Ogranicz skalę do rozsądnych wartości
        scale = max(0.7, min(scale, 2.0))

        logger.info(f"   Skala UI: {scale:.2f}x")
        return scale

    def _calculate_hud_positions(self, width: int, height: int, aspect: float) -> Dict[str, Tuple[int, int]]:
        """
        Oblicz pozycje elementów HUD dostosowane do rozdzielczości.

        Returns:
            Słownik z pozycjami dla różnych elementów HUD
        """
        positions = {}

        # Centrum ekranu
        center_x = width // 2
        center_y = height // 2

        # Dla ultrawide, elementy są bliżej centrum
        if aspect >= 2.3:  # 21:9
            margin_x = int(width * 0.20)  # 20% od krawędzi
            margin_y = int(height * 0.05)
        elif aspect >= 3.5:  # 32:9
            margin_x = int(width * 0.30)  # 30% od krawędzi
            margin_y = int(height * 0.05)
        else:  # Standard 16:9
            margin_x = int(width * 0.05)  # 5% od krawędzi
            margin_y = int(height * 0.05)

        # Pozycje dla różnych elementów
        positions['top_left'] = (margin_x, margin_y)
        positions['top_center'] = (center_x, margin_y)
        positions['top_right'] = (width - margin_x, margin_y)

        positions['middle_left'] = (margin_x, center_y)
        positions['center'] = (center_x, center_y)
        positions['middle_right'] = (width - margin_x, center_y)

        positions['bottom_left'] = (margin_x, height - margin_y)
        positions['bottom_center'] = (center_x, height - margin_y)
        positions['bottom_right'] = (width - margin_x, height - margin_y)

        # Dla ultrawide, dodatkowe pozycje
        if aspect >= 2.3:
            # Lewa i prawa trzecina
            third_x = width // 3
            positions['left_third'] = (third_x, center_y)
            positions['right_third'] = (2 * third_x, center_y)

        logger.debug(f"   Pozycje HUD: {len(positions)} pozycji zdefiniowanych")
        return positions

    def get_optimal_settings(self) -> Dict:
        """
        Zwróć optymalne ustawienia dla wykrytej rozdzielczości.

        Returns:
            Słownik z rekomendowanymi ustawieniami
        """
        if not self.current_config:
            return {}

        config = self.current_config

        settings = {
            'resolution': f"{config.width}x{config.height}",
            'aspect_ratio': config.aspect_ratio,
            'is_ultrawide': config.is_ultrawide,
            'roi': config.roi_default,
            'ui_scale': config.ui_scale,
            'hud_positions': config.hud_positions,
        }

        # Rekomendacje specyficzne dla typu ekranu
        if config.is_ultrawide:
            settings['recommendations'] = {
                'use_roi': True,  # Użyj ROI aby skupić się na centrum
                'hud_layout': 'center_focused',  # Elementy bliżej centrum
                'detection_zones': 'triple',  # Lewa/Centrum/Prawa strefa
            }
        else:
            settings['recommendations'] = {
                'use_roi': False,  # Pełny ekran
                'hud_layout': 'corners',  # Elementy w rogach
                'detection_zones': 'single',  # Jedna strefa
            }

        # Rekomendacje FPS bazując na rozdzielczości
        total_pixels = config.width * config.height
        if total_pixels >= 8294400:  # 4K (3840x2160)
            settings['recommended_fps'] = 60
            settings['recommended_quality'] = 'BALANCED'
        elif total_pixels >= 4953600:  # Ultrawide QHD (3440x1440)
            settings['recommended_fps'] = 90
            settings['recommended_quality'] = 'PERFORMANCE'
        else:  # Full HD i mniej
            settings['recommended_fps'] = 120
            settings['recommended_quality'] = 'PERFORMANCE'

        return settings

    def print_info(self):
        """Wyświetl informacje o wykrytej rozdzielczości."""
        if not self.current_config:
            print("⚠️  Nie wykryto rozdzielczości")
            return

        config = self.current_config

        print("\n" + "="*60)
        print("INFORMACJE O ROZDZIELCZOŚCI EKRANU")
        print("="*60)
        print(f"Rozdzielczość:    {config.width} x {config.height}")
        print(f"Aspect Ratio:     {config.aspect_ratio} ({config.aspect_float:.2f}:1)")
        print(f"Typ:              {'📐 Ultrawide' if config.is_ultrawide else '📺 Standard'}")
        print(f"Skala UI:         {config.ui_scale:.2f}x")
        print(f"ROI:              {config.roi_default}")

        settings = self.get_optimal_settings()
        if 'recommendations' in settings:
            print("\nRekomendacje:")
            for key, value in settings['recommendations'].items():
                print(f"  {key}: {value}")
            print(f"  FPS: {settings['recommended_fps']}")
            print(f"  Jakość: {settings['recommended_quality']}")

        print("="*60 + "\n")


def detect_screen_resolution() -> Tuple[int, int]:
    """
    Wykryj rozdzielczość ekranu głównego.

    Returns:
        Tuple (width, height)
    """
    try:
        from mss import mss
        with mss() as sct:
            monitor = sct.monitors[1]  # Monitor główny
            return (monitor['width'], monitor['height'])
    except Exception as e:
        logger.warning(f"Nie można wykryć rozdzielczości: {e}")
        # Domyślnie Full HD
        return (1920, 1080)


if __name__ == "__main__":
    # Test
    print("🔍 Testowanie wykrywania rozdzielczości...\n")

    # Test różnych rozdzielczości
    test_resolutions = [
        (1920, 1080, "Full HD 16:9"),
        (2560, 1440, "QHD 16:9"),
        (3440, 1440, "Ultrawide QHD 21:9"),
        (3840, 2160, "4K UHD 16:9"),
        (2560, 1080, "Ultrawide Full HD 21:9"),
        (5120, 1440, "Super Ultrawide 32:9"),
    ]

    for width, height, name in test_resolutions:
        print(f"\n📊 Test: {name}")
        detector = ResolutionDetector()
        config = detector.detect(width, height)
        settings = detector.get_optimal_settings()

        print(f"  Aspect: {config.aspect_ratio}")
        print(f"  ROI: {config.roi_default}")
        print(f"  UI Scale: {config.ui_scale:.2f}x")
        print(f"  Ultrawide: {'✅' if config.is_ultrawide else '❌'}")

    # Wykryj rzeczywistą rozdzielczość
    print("\n" + "="*60)
    print("Wykrywanie rzeczywistej rozdzielczości...")
    print("="*60)

    width, height = detect_screen_resolution()
    detector = ResolutionDetector()
    detector.detect(width, height)
    detector.print_info()
