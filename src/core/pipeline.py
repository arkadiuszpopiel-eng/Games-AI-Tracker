"""Main AI Vision Pipeline - Orchestrates all modules."""

import time
from typing import Optional
from loguru import logger

from core.config import GameProfile, SystemConfig
from core.types import Frame, SceneAnalysis
from modules.capture import ScreenCaptureEngine
from modules.preprocessor import FramePreprocessor
from modules.ai_vision import AIVisionCore
from modules.ocr import OCREngine
from modules.scene_understanding import SceneUnderstanding
from modules.event_engine import ContextEngine
from modules.decision_manager import DecisionManager
from modules.overlay import HUDRenderer
from utils.watchdog import Watchdog


class AIVisionPipeline:
    """
    Main AI Vision Pipeline.

    Orchestrates the complete flow:
    Capture → Preprocess → AI Vision → OCR → Scene Understanding
    → Event Engine → Decision Manager → HUD Renderer
    """

    def __init__(self, profile: GameProfile, system_config: SystemConfig):
        """
        Initialize pipeline.

        Args:
            profile: Game profile configuration
            system_config: System configuration
        """
        self.profile = profile
        self.system_config = system_config
        self._running = False

        # Statistics
        self._frame_count = 0
        self._start_time = 0.0
        self._latencies = []

        # Initialize modules
        logger.info("Initializing AI Vision Pipeline...")

        self.capture = ScreenCaptureEngine(
            profile.capture,
            callback=self._process_frame
        )

        self.preprocessor = FramePreprocessor(profile.performance)
        self.ai_vision = AIVisionCore(profile.ai)
        self.ocr = OCREngine(profile.ocr)
        self.scene_understanding = SceneUnderstanding()
        self.event_engine = ContextEngine(profile.rules)
        self.decision_manager = DecisionManager()
        self.hud_renderer = HUDRenderer(profile.hud)

        # Watchdog
        self.watchdog = Watchdog(
            check_interval=system_config.watchdog_interval
        )

        self._setup_watchdog()

        logger.info("Pipeline initialized")

    def _setup_watchdog(self):
        """Setup watchdog monitoring."""
        self.watchdog.register_module(
            "capture",
            lambda: self.capture.is_running,
            lambda: self.capture.start()
        )

        self.watchdog.register_module(
            "overlay",
            lambda: self.hud_renderer.is_running,
            lambda: self.hud_renderer.start()
        )

    def start(self):
        """Start the pipeline."""
        if self._running:
            logger.warning("Pipeline already running")
            return

        logger.info("Starting AI Vision Pipeline...")

        self._running = True
        self._start_time = time.time()

        # Start modules
        self.capture.start()
        self.hud_renderer.start()
        self.watchdog.start()

        logger.info("✓ Pipeline started successfully")

    def stop(self):
        """Stop the pipeline."""
        if not self._running:
            return

        logger.info("Stopping AI Vision Pipeline...")

        self._running = False

        # Stop modules
        self.watchdog.stop()
        self.hud_renderer.stop()
        self.capture.stop()

        # Print statistics
        self._print_statistics()

        logger.info("✓ Pipeline stopped")

    def _process_frame(self, frame: Frame):
        """
        Process a single frame through the pipeline.

        Args:
            frame: Captured frame
        """
        if not self._running:
            return

        frame_start = time.perf_counter()

        try:
            # 1. Preprocess
            processed = self.preprocessor.process(frame, roi=self.profile.capture.roi)
            if processed is None:
                return  # Frame skipped

            # 2. AI Vision
            entities = self.ai_vision.detect(processed)

            # 3. OCR
            ocr_results = self.ocr.extract_zones(frame.buffer)
            player_state = self.ocr.extract_player_state(ocr_results)

            # 4. Scene Understanding
            analysis = self.scene_understanding.analyze(entities, player_state)

            # 5. Event Engine
            events = self.event_engine.process(analysis)

            # 6. Decision Manager
            hud_elements = self.decision_manager.process(events, analysis)

            # 7. Render HUD
            self.hud_renderer.render(hud_elements)

            # Track performance
            frame_latency = (time.perf_counter() - frame_start) * 1000
            self._latencies.append(frame_latency)
            if len(self._latencies) > 100:
                self._latencies.pop(0)

            self._frame_count += 1

            # Log slow frames
            if frame_latency > self.profile.performance.max_latency_ms:
                logger.warning(f"High latency: {frame_latency:.1f}ms")

        except Exception as e:
            logger.error(f"Frame processing error: {e}")

    def get_statistics(self) -> dict:
        """Get pipeline statistics."""
        runtime = time.time() - self._start_time if self._start_time else 0
        fps = self._frame_count / runtime if runtime > 0 else 0
        avg_latency = sum(self._latencies) / len(self._latencies) if self._latencies else 0

        return {
            "runtime": runtime,
            "frames_processed": self._frame_count,
            "fps": fps,
            "avg_latency_ms": avg_latency,
            "capture_stats": self.capture.get_stats(),
            "ai_stats": self.ai_vision.get_stats(),
            "watchdog_status": self.watchdog.get_status(),
        }

    def _print_statistics(self):
        """Print pipeline statistics."""
        stats = self.get_statistics()

        logger.info("=" * 50)
        logger.info("Pipeline Statistics")
        logger.info("=" * 50)
        logger.info(f"Runtime: {stats['runtime']:.1f}s")
        logger.info(f"Frames Processed: {stats['frames_processed']}")
        logger.info(f"Average FPS: {stats['fps']:.1f}")
        logger.info(f"Average Latency: {stats['avg_latency_ms']:.1f}ms")
        logger.info("=" * 50)

    @property
    def is_running(self) -> bool:
        """Check if pipeline is running."""
        return self._running
