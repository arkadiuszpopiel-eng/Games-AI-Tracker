"""Screen Capture Engine - OS-native desktop capture with ultra-low latency."""

import time
from typing import Optional, Callable
from threading import Thread, Event
import numpy as np
import mss
from queue import Queue, Full
from loguru import logger

from core.types import Frame
from core.config import CaptureConfig


class ScreenCaptureEngine:
    """
    High-performance screen capture engine.

    Features:
    - OS-native desktop capture
    - Multi-monitor support
    - 60-144 FPS capability
    - Ultra-low latency (<10ms capture time)
    - Async frame delivery
    """

    def __init__(self, config: CaptureConfig, callback: Optional[Callable[[Frame], None]] = None):
        """
        Initialize capture engine.

        Args:
            config: Capture configuration
            callback: Optional callback for each captured frame
        """
        self.config = config
        self.callback = callback
        self._sct = None
        self._running = False
        self._thread = None
        self._stop_event = Event()
        self._frame_queue = Queue(maxsize=3)  # Small buffer to prevent memory bloat
        self._frame_id = 0
        self._stats = {
            "frames_captured": 0,
            "frames_dropped": 0,
            "avg_capture_time_ms": 0.0,
        }

    def start(self):
        """Start capture thread."""
        if self._running:
            logger.warning("Capture engine already running")
            return

        self._running = True
        self._stop_event.clear()
        self._sct = mss.mss()
        self._thread = Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        logger.info(f"Screen capture started at {self.config.fps} FPS")

    def stop(self):
        """Stop capture thread."""
        if not self._running:
            return

        self._running = False
        self._stop_event.set()

        if self._thread:
            self._thread.join(timeout=2.0)

        if self._sct:
            self._sct.close()
            self._sct = None

        logger.info("Screen capture stopped")

    def _capture_loop(self):
        """Main capture loop running in separate thread."""
        frame_interval = 1.0 / self.config.fps
        capture_times = []

        # Determine capture region
        monitor = self._sct.monitors[self.config.monitor]
        if self.config.roi:
            x, y, w, h = self.config.roi
            capture_region = {"top": y, "left": x, "width": w, "height": h}
        else:
            capture_region = monitor

        logger.debug(f"Capture region: {capture_region}")

        while not self._stop_event.is_set():
            loop_start = time.perf_counter()

            try:
                # Capture frame
                capture_start = time.perf_counter()
                screenshot = self._sct.grab(capture_region)

                # Convert to numpy array (RGB format)
                frame_buffer = np.array(screenshot, dtype=np.uint8)

                # Convert BGRA to RGB if needed
                if frame_buffer.shape[2] == 4:
                    frame_buffer = frame_buffer[:, :, :3]
                if self.config.format == "RGB":
                    frame_buffer = frame_buffer[:, :, [2, 1, 0]]  # BGR to RGB

                capture_time = (time.perf_counter() - capture_start) * 1000
                capture_times.append(capture_time)
                if len(capture_times) > 100:
                    capture_times.pop(0)

                # Create frame object
                frame = Frame(
                    frame_id=self._frame_id,
                    buffer=frame_buffer,
                    width=frame_buffer.shape[1],
                    height=frame_buffer.shape[0],
                    timestamp_ns=time.perf_counter_ns(),
                    metadata={
                        "capture_time_ms": capture_time,
                        "monitor": self.config.monitor,
                    }
                )
                self._frame_id += 1
                self._stats["frames_captured"] += 1

                # Deliver frame via callback or queue
                if self.callback:
                    self.callback(frame)
                else:
                    try:
                        self._frame_queue.put_nowait(frame)
                    except Full:
                        # Drop frame if queue is full
                        self._stats["frames_dropped"] += 1

                # Update stats
                if capture_times:
                    self._stats["avg_capture_time_ms"] = sum(capture_times) / len(capture_times)

            except Exception as e:
                logger.error(f"Capture error: {e}")
                time.sleep(0.1)
                continue

            # Frame pacing
            elapsed = time.perf_counter() - loop_start
            sleep_time = frame_interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

    def get_frame(self, timeout: float = 0.1) -> Optional[Frame]:
        """
        Get next frame from queue (blocking).

        Args:
            timeout: Maximum wait time in seconds

        Returns:
            Frame or None if timeout
        """
        try:
            return self._frame_queue.get(timeout=timeout)
        except:
            return None

    def get_stats(self) -> dict:
        """Get capture statistics."""
        return self._stats.copy()

    @property
    def is_running(self) -> bool:
        """Check if capture is running."""
        return self._running


# Factory function for easy instantiation
def create_capture_engine(config: CaptureConfig, **kwargs) -> ScreenCaptureEngine:
    """Create and configure a screen capture engine."""
    return ScreenCaptureEngine(config, **kwargs)
