"""Scene Understanding - Temporal smoothing and state classification."""

from typing import List, Dict, Optional
from collections import deque
import numpy as np
from loguru import logger

from core.types import Entity, EntityType, PlayerState, SceneState, SceneAnalysis


class SceneUnderstanding:
    """
    Scene Understanding module.

    Features:
    - Temporal smoothing over frame history
    - Noise reduction and confidence fusion
    - Scene state classification
    - Environmental analysis
    """

    def __init__(self, history_size: int = 30):
        """
        Initialize scene understanding.

        Args:
            history_size: Number of frames to keep in history
        """
        self.history_size = history_size
        self._entity_history: deque = deque(maxlen=history_size)
        self._state_history: deque = deque(maxlen=history_size)
        self._player_state_history: deque = deque(maxlen=history_size)

    def analyze(
        self,
        entities: List[Entity],
        player_state: Optional[PlayerState] = None
    ) -> SceneAnalysis:
        """
        Analyze current scene.

        Args:
            entities: Detected entities
            player_state: Player state from OCR

        Returns:
            Scene analysis result
        """
        # Add to history
        self._entity_history.append(entities)
        if player_state:
            self._player_state_history.append(player_state)

        # Smooth entities
        smoothed_entities = self._smooth_entities(entities)

        # Classify scene state
        scene_state, confidence = self._classify_scene_state(
            smoothed_entities,
            player_state
        )

        self._state_history.append(scene_state)

        # Build analysis
        analysis = SceneAnalysis(
            state=scene_state,
            confidence=confidence,
            entities=smoothed_entities,
            player_state=player_state or PlayerState(),
            environment_data=self._analyze_environment(smoothed_entities)
        )

        return analysis

    def _smooth_entities(self, entities: List[Entity]) -> List[Entity]:
        """
        Apply temporal smoothing to entities.

        Args:
            entities: Current frame entities

        Returns:
            Smoothed entities
        """
        if len(self._entity_history) < 3:
            return entities  # Not enough history

        # Simple smoothing: keep entities that appear in recent frames
        smoothed = []
        for entity in entities:
            # Count how many times this entity ID appears in recent history
            appearance_count = 0
            for hist_entities in list(self._entity_history)[-5:]:
                if any(e.id == entity.id for e in hist_entities):
                    appearance_count += 1

            # Keep if appeared in at least 2 of last 5 frames
            if appearance_count >= 2:
                smoothed.append(entity)

        return smoothed

    def _classify_scene_state(
        self,
        entities: List[Entity],
        player_state: Optional[PlayerState]
    ) -> tuple[SceneState, float]:
        """
        Classify current scene state.

        Args:
            entities: Detected entities
            player_state: Player state

        Returns:
            Tuple of (state, confidence)
        """
        # Count enemies and their threat levels
        enemies = [e for e in entities if e.type == EntityType.ENEMY]
        num_enemies = len(enemies)

        if num_enemies == 0:
            # No enemies
            if player_state and player_state.hp:
                return SceneState.EXPLORATION, 0.9
            return SceneState.IDLE, 0.85

        # Calculate average threat score
        avg_threat = sum(e.threat_score for e in enemies) / num_enemies

        # Determine combat intensity
        if num_enemies >= 3 and avg_threat > 0.6:
            return SceneState.HIGH_RISK_COMBAT, 0.85
        elif num_enemies >= 1:
            return SceneState.COMBAT, 0.8

        return SceneState.EXPLORATION, 0.7

    def _analyze_environment(self, entities: List[Entity]) -> Dict:
        """
        Analyze environmental factors.

        Args:
            entities: Detected entities

        Returns:
            Environment analysis
        """
        enemies = [e for e in entities if e.type == EntityType.ENEMY]

        if not enemies:
            return {
                "enemy_density": 0.0,
                "avg_proximity": 0.0,
                "threat_zones": []
            }

        # Calculate enemy density (enemies per screen area)
        # Assume normalized screen area of 1920x1080
        screen_area = 1920 * 1080
        enemy_density = len(enemies) / (screen_area / 100000)  # per 100k pixels

        # Calculate average proximity (to assumed player position)
        player_pos = (1920 // 2, 1080 * 0.8)  # Center-bottom
        proximities = []
        for enemy in enemies:
            enemy_center = enemy.bbox.center
            distance = np.sqrt(
                (enemy_center[0] - player_pos[0])**2 +
                (enemy_center[1] - player_pos[1])**2
            )
            proximities.append(distance)

        avg_proximity = sum(proximities) / len(proximities) if proximities else 0

        # Identify threat zones (clusters of enemies)
        threat_zones = self._identify_threat_zones(enemies)

        return {
            "enemy_density": enemy_density,
            "avg_proximity": avg_proximity,
            "threat_zones": threat_zones,
            "total_enemies": len(enemies)
        }

    def _identify_threat_zones(self, enemies: List[Entity]) -> List[Dict]:
        """
        Identify spatial threat zones.

        Args:
            enemies: Enemy entities

        Returns:
            List of threat zone descriptions
        """
        if len(enemies) < 2:
            return []

        # Simple clustering: find groups of enemies within 200 pixels
        zones = []
        processed = set()

        for i, enemy1 in enumerate(enemies):
            if i in processed:
                continue

            cluster = [enemy1]
            processed.add(i)

            for j, enemy2 in enumerate(enemies):
                if j <= i or j in processed:
                    continue

                center1 = enemy1.bbox.center
                center2 = enemy2.bbox.center
                distance = np.sqrt(
                    (center1[0] - center2[0])**2 +
                    (center1[1] - center2[1])**2
                )

                if distance < 200:
                    cluster.append(enemy2)
                    processed.add(j)

            if len(cluster) >= 2:
                # Calculate cluster center
                centers = [e.bbox.center for e in cluster]
                cluster_center = (
                    sum(c[0] for c in centers) // len(centers),
                    sum(c[1] for c in centers) // len(centers)
                )

                zones.append({
                    "center": cluster_center,
                    "enemy_count": len(cluster),
                    "avg_threat": sum(e.threat_score for e in cluster) / len(cluster)
                })

        return zones

    def get_state_stability(self) -> float:
        """
        Calculate scene state stability.

        Returns:
            Stability score (0-1), higher = more stable
        """
        if len(self._state_history) < 5:
            return 0.5

        # Check if state has been consistent
        recent_states = list(self._state_history)[-10:]
        most_common_state = max(set(recent_states), key=recent_states.count)
        stability = recent_states.count(most_common_state) / len(recent_states)

        return stability
