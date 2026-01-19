"""Frame Preprocessor - Scaling, normalization, ROI cropping."""

from typing import Optional, Tuple, List
import numpy as np
import cv2
from loguru import logger

from core.types import Frame
from core.config import PerformanceConfig


class FramePreprocessor:
    """
    Frame preprocessing for AI pipeline.

    Features:
    - Scaling and normalization
    - ROI cropping
    - UI masking
    - Quality mode adaptation
    - Frame skipping logic
    """

    def __init__(self, config: PerformanceConfig):
        """
        Initialize preprocessor.

        Args:
            config: Performance configuration
        """
        self.config = config
        self._frame_count = 0
        self._skip_counter = 0

        # Quality mode settings
        self._quality_settings = {
            "QUALITY": {"scale": 1.0, "skip_frames": 0, "denoise": True},
            "PERFORMANCE": {"scale": 0.75, "skip_frames": 1, "denoise": False},
            "SAFE": {"scale": 0.5, "skip_frames": 2, "denoise": False},
            "DEBUG": {"scale": 1.0, "skip_frames": 0, "denoise": True},
        }

        self._current_settings = self._quality_settings[config.mode]
        logger.info(f"Preprocessor initialized in {config.mode} mode")

    def process(self, frame: Frame, roi: Optional[Tuple[int, int, int, int]] = None) -> Optional[np.ndarray]:
        """
        Process a frame.

        Args:
            frame: Input frame
            roi: Optional region of interest (x, y, w, h)

        Returns:
            Processed frame buffer or None if skipped
        """
        self._frame_count += 1

        # Frame skipping
        if self.config.frame_skip and self._should_skip_frame():
            return None

        buffer = frame.buffer.copy()

        # ROI cropping
        if roi:
            x, y, w, h = roi
            buffer = buffer[y:y+h, x:x+w]

        # Scaling
        scale = self._current_settings["scale"]
        if scale != 1.0:
            new_width = int(buffer.shape[1] * scale)
            new_height = int(buffer.shape[0] * scale)
            buffer = cv2.resize(buffer, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

        # Denoising
        if self._current_settings["denoise"]:
            buffer = cv2.fastNlMeansDenoisingColored(buffer, None, 10, 10, 7, 21)

        # Normalization (0-255 uint8 to 0-1 float32)
        buffer = buffer.astype(np.float32) / 255.0

        return buffer

    def _should_skip_frame(self) -> bool:
        """Determine if current frame should be skipped."""
        skip_frames = self._current_settings["skip_frames"]
        if skip_frames == 0:
            return False

        self._skip_counter += 1
        if self._skip_counter > skip_frames:
            self._skip_counter = 0
            return False
        return True

    def apply_mask(self, buffer: np.ndarray, mask_regions: List[Tuple[int, int, int, int]]) -> np.ndarray:
        """
        Apply UI masking to frame.

        Args:
            buffer: Frame buffer
            mask_regions: List of regions to mask (x, y, w, h)

        Returns:
            Masked buffer
        """
        masked = buffer.copy()
        for x, y, w, h in mask_regions:
            masked[y:y+h, x:x+w] = 0
        return masked

    def set_quality_mode(self, mode: str):
        """Change quality mode dynamically."""
        if mode in self._quality_settings:
            self._current_settings = self._quality_settings[mode]
            self.config.mode = mode
            logger.info(f"Quality mode changed to {mode}")
        else:
            logger.warning(f"Unknown quality mode: {mode}")

    def get_stats(self) -> dict:
        """Get preprocessing statistics."""
        return {
            "frames_processed": self._frame_count,
            "current_mode": self.config.mode,
            "scale_factor": self._current_settings["scale"],
        }
