"""Tests for the AI Vision Pipeline."""

import pytest
import numpy as np
from core.types import Frame, Entity, EntityType, BoundingBox, PlayerState, SceneState
from core.config import GameProfile
from modules.preprocessor import FramePreprocessor
from modules.scene_understanding import SceneUnderstanding


class TestFramePreprocessor:
    """Test frame preprocessing."""

    def test_frame_scaling(self):
        """Test frame scaling."""
        from core.config import PerformanceConfig

        config = PerformanceConfig(mode="SAFE")
        preprocessor = FramePreprocessor(config)

        # Create test frame
        frame = Frame(
            frame_id=1,
            buffer=np.random.randint(0, 255, (1080, 1920, 3), dtype=np.uint8),
            width=1920,
            height=1080,
            timestamp_ns=0
        )

        processed = preprocessor.process(frame)

        # Should be scaled to 0.5x in SAFE mode
        assert processed is not None
        assert processed.shape[1] < frame.width


class TestSceneUnderstanding:
    """Test scene understanding."""

    def test_scene_classification(self):
        """Test scene state classification."""
        scene = SceneUnderstanding()

        # Create test entities (enemies)
        enemies = [
            Entity(
                id=1,
                type=EntityType.ENEMY,
                bbox=BoundingBox(100, 100, 50, 50),
                confidence=0.9,
                threat_score=0.8
            )
        ]

        player_state = PlayerState(hp=50, hp_max=100)

        analysis = scene.analyze(enemies, player_state)

        assert analysis.state == SceneState.COMBAT
        assert analysis.confidence > 0.5


class TestEntityTracking:
    """Test entity tracking."""

    def test_persistent_ids(self):
        """Test that entities maintain IDs across frames."""
        from modules.ai_vision import EntityTracker

        tracker = EntityTracker()

        # Frame 1
        entities_1 = [
            Entity(
                id=0,
                type=EntityType.ENEMY,
                bbox=BoundingBox(100, 100, 50, 50),
                confidence=0.9
            )
        ]

        tracked_1 = tracker.update(entities_1)
        entity_1_id = tracked_1[0].id

        # Frame 2 - same entity, slightly moved
        entities_2 = [
            Entity(
                id=0,
                type=EntityType.ENEMY,
                bbox=BoundingBox(105, 105, 50, 50),
                confidence=0.9
            )
        ]

        tracked_2 = tracker.update(entities_2)
        entity_2_id = tracked_2[0].id

        # ID should be persistent
        assert entity_1_id == entity_2_id


class TestRuleEvaluator:
    """Test rule evaluation."""

    def test_rule_condition_evaluation(self):
        """Test rule condition evaluation."""
        from modules.event_engine import RuleEvaluator
        from core.config import Rule

        rules = [
            Rule(
                name="test_rule",
                state="combat",
                conditions=["player.hp < 50"],
                actions=[{"type": "emit", "payload": "LOW_HEALTH"}]
            )
        ]

        evaluator = RuleEvaluator(rules)

        # Create analysis with low health
        from core.types import SceneAnalysis
        analysis = SceneAnalysis(
            state=SceneState.COMBAT,
            confidence=0.9,
            entities=[],
            player_state=PlayerState(hp=30, hp_max=100)
        )

        events = evaluator.evaluate(analysis)

        # Should emit LOW_HEALTH event
        assert len(events) > 0
        assert events[0].type == "LOW_HEALTH"


def test_profile_loading():
    """Test loading game profiles."""
    from core.config import GameProfile
    from pathlib import Path

    # Create test profile
    profile = GameProfile(
        name="Test Game",
        game_id="test"
    )

    # Verify default values
    assert profile.capture.fps == 60
    assert profile.ai.model == "yolov8n"
    assert profile.performance.mode == "PERFORMANCE"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
