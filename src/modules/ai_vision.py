"""AI Vision Core - Entity detection, tracking, and analysis."""

from typing import List, Dict, Optional
import numpy as np
import time
from collections import defaultdict
from loguru import logger

try:
    from ultralytics import YOLO
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger.warning("PyTorch/Ultralytics not available - AI Vision will run in mock mode")

from core.types import Entity, EntityType, BoundingBox
from core.config import AIModelConfig
from utils.gpu_detector import GPUDetector


class EntityTracker:
    """Track entities across frames with persistent IDs."""

    def __init__(self, max_age: int = 30, min_distance: float = 50.0):
        """
        Initialize tracker.

        Args:
            max_age: Maximum frames to keep track without detection
            min_distance: Maximum distance to associate detections (pixels)
        """
        self._tracks: Dict[int, Entity] = {}
        self._next_id = 1
        self._max_age = max_age
        self._min_distance = min_distance
        self._age_counter: Dict[int, int] = defaultdict(int)

    def update(self, detections: List[Entity]) -> List[Entity]:
        """
        Update tracks with new detections.

        Args:
            detections: New detections (with id=0)

        Returns:
            Tracked entities with persistent IDs
        """
        if not self._tracks:
            # First frame - assign new IDs
            for det in detections:
                det.id = self._next_id
                self._tracks[self._next_id] = det
                self._next_id += 1
            return detections

        # Match detections to existing tracks
        matched_detections = []
        unmatched_detections = []

        for det in detections:
            best_match_id = None
            best_distance = float('inf')

            det_center = det.bbox.center

            for track_id, track in self._tracks.items():
                track_center = track.bbox.center
                distance = np.sqrt((det_center[0] - track_center[0])**2 +
                                 (det_center[1] - track_center[1])**2)

                if distance < self._min_distance and distance < best_distance:
                    best_match_id = track_id
                    best_distance = distance

            if best_match_id is not None:
                # Update existing track
                det.id = best_match_id
                # Calculate velocity
                prev_center = self._tracks[best_match_id].bbox.center
                det.velocity = best_distance  # Simple pixel distance
                # Calculate direction
                dx = det_center[0] - prev_center[0]
                dy = det_center[1] - prev_center[1]
                det.direction = self._calculate_direction(dx, dy)

                self._tracks[best_match_id] = det
                self._age_counter[best_match_id] = 0
                matched_detections.append(det)
            else:
                unmatched_detections.append(det)

        # Add new tracks for unmatched detections
        for det in unmatched_detections:
            det.id = self._next_id
            self._tracks[self._next_id] = det
            self._next_id += 1
            matched_detections.append(det)

        # Age out old tracks
        to_remove = []
        for track_id in list(self._age_counter.keys()):
            self._age_counter[track_id] += 1
            if self._age_counter[track_id] > self._max_age:
                to_remove.append(track_id)

        for track_id in to_remove:
            del self._tracks[track_id]
            del self._age_counter[track_id]

        return matched_detections

    @staticmethod
    def _calculate_direction(dx: float, dy: float) -> str:
        """Calculate direction from movement vector."""
        if abs(dx) < 2 and abs(dy) < 2:
            return "stationary"

        angle = np.arctan2(dy, dx) * 180 / np.pi

        # Assume player is at center-bottom
        if -45 <= angle < 45:
            return "towards_player"
        elif 45 <= angle < 135:
            return "downward"
        elif -135 <= angle < -45:
            return "upward"
        else:
            return "away_from_player"


class AIVisionCore:
    """
    AI Vision Core for entity detection and analysis.

    Features:
    - Entity detection (enemies, NPCs, objects)
    - Real-time tracking with persistent IDs
    - Threat scoring
    - Pose and action recognition (placeholder)
    """

    def __init__(self, config: AIModelConfig):
        """
        Initialize AI Vision Core.

        Args:
            config: AI model configuration
        """
        self.config = config
        self.model = None
        self.device = None
        self._tracker = EntityTracker()
        self._frame_count = 0

        # Entity type mapping (customize per game)
        self._class_to_entity_type = {
            "person": EntityType.ENEMY,
            "enemy": EntityType.ENEMY,
            "ally": EntityType.ALLY,
            "npc": EntityType.NPC,
            "object": EntityType.OBJECT,
            "item": EntityType.ITEM,
            "hazard": EntityType.HAZARD,
        }

        self._initialize_model()

    def _initialize_model(self):
        """Initialize AI model with automatic GPU detection."""
        if not TORCH_AVAILABLE:
            logger.warning("Running in mock mode - no actual detection will occur")
            return

        try:
            # Auto-detect GPU
            if self.config.device == "auto":
                gpu_detector = GPUDetector()
                device_type, backend, gpu_info = gpu_detector.detect()
                self.device = device_type
                self.gpu_info = gpu_info
                self.optimal_config = gpu_detector.get_optimal_config()

                logger.info(f"🎯 Wykryto GPU: {gpu_detector.device_name}")
                logger.info(f"   Backend: {backend}")

                # Specjalne komunikaty dla konkretnych GPU
                if "4050" in gpu_detector.device_name:
                    logger.info("💻 RTX 4050 (Laptop) - Optymalizacja dla trybu oszczędzania energii")
                elif "7900" in gpu_detector.device_name:
                    logger.info("🚀 RX 7900 GRE - Optymalizacja dla high-end AMD")

                # Obsługa DirectML dla AMD na Windows
                if backend == "directml":
                    try:
                        import torch_directml
                        self.device = torch_directml.device()
                        logger.info("✅ Używam DirectML dla AMD GPU")
                    except ImportError:
                        logger.warning("⚠️  torch-directml nie zainstalowany, używam CPU")
                        logger.info("   Zainstaluj: pip install torch-directml")
                        self.device = "cpu"

            else:
                self.device = self.config.device
                self.optimal_config = {"batch_size": 1, "fp16": False}

            # Load YOLO model
            logger.info(f"📥 Ładowanie modelu {self.config.model}...")
            self.model = YOLO(self.config.model)

            # Przenieś model na urządzenie
            if isinstance(self.device, str) and self.device in ["cuda", "cpu"]:
                self.model.to(self.device)
            elif hasattr(self.device, 'type'):  # DirectML device
                # DirectML obsługuje automatycznie
                pass

            logger.info(f"✅ AI Vision zainicjalizowany: {self.config.model} na {self.device}")

            # Wyświetl optymalne ustawienia
            if hasattr(self, 'optimal_config'):
                logger.info(f"   Batch size: {self.optimal_config.get('batch_size', 1)}")
                logger.info(f"   FP16: {self.optimal_config.get('fp16', False)}")

        except Exception as e:
            logger.error(f"❌ Błąd inicjalizacji modelu AI: {e}")
            logger.info("   Sprawdź instalację GPU - uruchom: python -m utils.gpu_detector")
            self.model = None

    def detect(self, frame: np.ndarray) -> List[Entity]:
        """
        Detect entities in frame.

        Args:
            frame: Frame buffer (RGB, normalized 0-1 or 0-255)

        Returns:
            List of detected entities with tracking IDs
        """
        self._frame_count += 1

        # Mock detection if model not available
        if self.model is None:
            return self._mock_detection(frame)

        try:
            # Run inference
            results = self.model(
                frame,
                conf=self.config.confidence,
                iou=self.config.iou_threshold,
                verbose=False
            )[0]

            # Parse detections
            detections = []
            for box in results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = results.names[class_id]

                # Map to entity type
                entity_type = self._class_to_entity_type.get(
                    class_name.lower(),
                    EntityType.UNKNOWN
                )

                # Create entity
                bbox = BoundingBox(
                    x=int(x1),
                    y=int(y1),
                    width=int(x2 - x1),
                    height=int(y2 - y1)
                )

                entity = Entity(
                    id=0,  # Will be assigned by tracker
                    type=entity_type,
                    bbox=bbox,
                    confidence=confidence,
                    metadata={"class_name": class_name}
                )

                # Calculate threat score
                entity.threat_score = self._calculate_threat_score(entity, frame.shape)

                detections.append(entity)

            # Update tracker
            tracked_entities = self._tracker.update(detections)

            return tracked_entities

        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []

    def _calculate_threat_score(self, entity: Entity, frame_shape: tuple) -> float:
        """
        Calculate threat score for entity.

        Args:
            entity: Detected entity
            frame_shape: Frame dimensions

        Returns:
            Threat score (0.0 to 1.0)
        """
        if entity.type != EntityType.ENEMY:
            return 0.0

        score = 0.0

        # Proximity score (closer = higher threat)
        frame_height = frame_shape[0]
        # Assume player is at bottom center
        player_y = frame_height * 0.8
        distance_to_player = abs(entity.bbox.center[1] - player_y)
        proximity_score = 1.0 - min(distance_to_player / frame_height, 1.0)
        score += proximity_score * 0.5

        # Size score (larger = higher threat)
        size_ratio = entity.bbox.area / (frame_shape[0] * frame_shape[1])
        size_score = min(size_ratio * 50, 1.0)  # Scale appropriately
        score += size_score * 0.3

        # Confidence score
        score += entity.confidence * 0.2

        return min(score, 1.0)

    def _mock_detection(self, frame: np.ndarray) -> List[Entity]:
        """Generate mock detections for testing without model."""
        # Simple mock: random enemy position
        if self._frame_count % 30 == 0:  # Every 30 frames
            mock_entity = Entity(
                id=0,
                type=EntityType.ENEMY,
                bbox=BoundingBox(x=500, y=400, width=100, height=150),
                confidence=0.85,
                threat_score=0.7,
                metadata={"mock": True}
            )
            return self._tracker.update([mock_entity])
        return []

    def get_stats(self) -> dict:
        """Get vision statistics."""
        return {
            "frames_processed": self._frame_count,
            "active_tracks": len(self._tracker._tracks),
            "model": self.config.model,
            "device": self.device,
        }
