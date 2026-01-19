"""Overlay/HUD Renderer - Transparent window overlay with click-through."""

from typing import List, Optional
import time
from threading import Thread, Lock
from loguru import logger

try:
    from PyQt6.QtWidgets import QApplication, QWidget
    from PyQt6.QtCore import Qt, QTimer, QRect, QPoint
    from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QBrush
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    logger.warning("PyQt6 not available - overlay will run in mock mode")

from core.types import HUDElement
from core.config import HUDConfig


if PYQT_AVAILABLE:
    class OverlayWindow(QWidget):
        """Transparent overlay window."""

        def __init__(self, config: HUDConfig):
            """Initialize overlay window."""
            super().__init__()
            self.config = config
            self.elements: List[HUDElement] = []
            self.elements_lock = Lock()
            self._setup_window()

        def _setup_window(self):
            """Configure window properties."""
            # Transparent, frameless, always on top
            self.setWindowFlags(
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowStaysOnTopHint |
                Qt.WindowType.Tool |
                Qt.WindowType.WindowTransparentForInput  # Click-through
            )

            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

            # Set to fullscreen
            screen = QApplication.primaryScreen().geometry()
            self.setGeometry(screen)

            logger.info(f"Overlay window created: {screen.width()}x{screen.height()}")

        def update_elements(self, elements: List[HUDElement]):
            """
            Update HUD elements to render.

            Args:
                elements: List of HUD elements
            """
            with self.elements_lock:
                # Filter expired elements
                current_time = time.time()
                self.elements = [
                    e for e in elements
                    if e.ttl is None or (current_time - (getattr(e, '_created_at', current_time))) < e.ttl
                ]

                # Set creation time for new elements
                for elem in self.elements:
                    if not hasattr(elem, '_created_at'):
                        elem._created_at = current_time

            self.update()  # Trigger repaint

        def paintEvent(self, event):
            """Paint HUD elements."""
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)

            with self.elements_lock:
                for element in self.elements:
                    self._draw_element(painter, element)

        def _draw_element(self, painter: QPainter, element: HUDElement):
            """
            Draw a single HUD element.

            Args:
                painter: QPainter instance
                element: HUD element to draw
            """
            r, g, b, a = element.color
            color = QColor(r, g, b, a)

            if element.type == "text":
                self._draw_text(painter, element, color)
            elif element.type == "arrow":
                self._draw_arrow(painter, element, color)
            elif element.type == "ring":
                self._draw_ring(painter, element, color)
            elif element.type == "zone":
                self._draw_zone(painter, element, color)
            elif element.type == "border":
                self._draw_border(painter, element, color)

        def _draw_text(self, painter: QPainter, element: HUDElement, color: QColor):
            """Draw text element."""
            data = element.data
            x, y = element.position

            font = QFont("Arial", data.get("size", 24))
            if data.get("bold"):
                font.setBold(True)

            painter.setFont(font)
            painter.setPen(color)

            # Draw text with outline for visibility
            outline_color = QColor(0, 0, 0, 200)
            for dx, dy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                painter.setPen(outline_color)
                painter.drawText(x + dx, y + dy, data.get("text", ""))

            painter.setPen(color)
            painter.drawText(x, y, data.get("text", ""))

        def _draw_arrow(self, painter: QPainter, element: HUDElement, color: QColor):
            """Draw direction arrow."""
            data = element.data
            x, y = element.position
            size = data.get("size", 30)

            painter.setPen(QPen(color, 3))
            painter.setBrush(QBrush(color))

            # Simple triangle arrow pointing down (towards player)
            direction = data.get("direction", "towards_player")

            if direction == "towards_player":
                # Down arrow
                points = [
                    QPoint(x, y + size),
                    QPoint(x - size//2, y),
                    QPoint(x + size//2, y)
                ]
            elif direction == "away_from_player":
                # Up arrow
                points = [
                    QPoint(x, y - size),
                    QPoint(x - size//2, y),
                    QPoint(x + size//2, y)
                ]
            else:
                # Circle for stationary
                painter.drawEllipse(QPoint(x, y), size//2, size//2)
                return

            painter.drawPolygon(points)

        def _draw_ring(self, painter: QPainter, element: HUDElement, color: QColor):
            """Draw proximity ring."""
            data = element.data
            x, y = element.position
            radius = data.get("radius", 50)
            thickness = data.get("thickness", 2)

            painter.setPen(QPen(color, thickness))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawEllipse(QPoint(x, y), radius, radius)

        def _draw_zone(self, painter: QPainter, element: HUDElement, color: QColor):
            """Draw threat zone."""
            data = element.data
            x, y = element.position
            radius = data.get("radius", 100)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(color))
            painter.drawEllipse(QPoint(x, y), radius, radius)

            # Draw enemy count
            if "enemy_count" in data:
                painter.setPen(QColor(255, 255, 255, 255))
                painter.setFont(QFont("Arial", 16, QFont.Weight.Bold))
                painter.drawText(x - 10, y + 5, f"{data['enemy_count']}")

        def _draw_border(self, painter: QPainter, element: HUDElement, color: QColor):
            """Draw screen border effect."""
            data = element.data
            thickness = data.get("thickness", 5)

            painter.setPen(QPen(color, thickness))
            painter.setBrush(Qt.BrushStyle.NoBrush)

            rect = self.rect()
            painter.drawRect(rect)


class HUDRenderer:
    """
    HUD Renderer for managing overlay display.

    Features:
    - Transparent overlay window
    - Always-on-top, click-through
    - Real-time element updates
    - DPI aware
    """

    def __init__(self, config: HUDConfig):
        """
        Initialize HUD renderer.

        Args:
            config: HUD configuration
        """
        self.config = config
        self.app = None
        self.window = None
        self._running = False
        self._thread = None
        self._update_timer = None

        if not PYQT_AVAILABLE:
            logger.warning("Running in mock mode - no overlay will be displayed")

    def start(self):
        """Start overlay renderer."""
        if not PYQT_AVAILABLE:
            logger.info("Mock overlay started")
            self._running = True
            return

        if self._running:
            logger.warning("Overlay already running")
            return

        self._running = True
        self._thread = Thread(target=self._run_qt_app, daemon=True)
        self._thread.start()

        logger.info("HUD overlay started")

    def _run_qt_app(self):
        """Run Qt application in separate thread."""
        import sys
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)

        self.window = OverlayWindow(self.config)
        self.window.show()

        # Update timer
        self._update_timer = QTimer()
        self._update_timer.timeout.connect(self._periodic_update)
        self._update_timer.start(16)  # ~60 FPS

        self.app.exec()

    def _periodic_update(self):
        """Periodic update callback."""
        if self.window:
            self.window.update()

    def stop(self):
        """Stop overlay renderer."""
        self._running = False

        if self.app and PYQT_AVAILABLE:
            self.app.quit()

        if self._thread:
            self._thread.join(timeout=2.0)

        logger.info("HUD overlay stopped")

    def render(self, elements: List[HUDElement]):
        """
        Render HUD elements.

        Args:
            elements: List of HUD elements to display
        """
        if not self._running:
            return

        if self.window and PYQT_AVAILABLE:
            self.window.update_elements(elements)

    @property
    def is_running(self) -> bool:
        """Check if overlay is running."""
        return self._running


# Factory function
def create_hud_renderer(config: HUDConfig) -> HUDRenderer:
    """Create HUD renderer instance."""
    return HUDRenderer(config)
