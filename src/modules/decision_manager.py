"""Decision & Priority Manager - Event arbitration and HUD element generation."""

from typing import List, Dict, Optional
from collections import defaultdict
import time
from loguru import logger

from core.types import Event, EventPriority, HUDElement, SceneAnalysis


class DecisionManager:
    """
    Decision & Priority Manager.

    Features:
    - Event arbitration and escalation
    - De-duplication with visual cooldowns
    - HUD element generation based on priorities
    """

    def __init__(self, max_concurrent_alerts: int = 3):
        """
        Initialize decision manager.

        Args:
            max_concurrent_alerts: Maximum concurrent HUD alerts
        """
        self.max_concurrent_alerts = max_concurrent_alerts
        self._event_history: Dict[str, float] = {}
        self._active_alerts: List[Dict] = []
        self._visual_cooldowns: Dict[str, float] = defaultdict(lambda: 1.0)

    def process(self, events: List[Event], analysis: SceneAnalysis) -> List[HUDElement]:
        """
        Process events and generate HUD elements.

        Args:
            events: List of events from event engine
            analysis: Scene analysis for context

        Returns:
            List of HUD elements to render
        """
        current_time = time.time()

        # Filter and deduplicate events
        filtered_events = self._filter_events(events, current_time)

        # Sort by priority
        sorted_events = sorted(filtered_events, key=lambda e: e.priority.value, reverse=True)

        # Limit concurrent alerts
        active_events = sorted_events[:self.max_concurrent_alerts]

        # Generate HUD elements
        hud_elements = []

        # Process events
        for event in active_events:
            elements = self._event_to_hud_elements(event, analysis)
            hud_elements.extend(elements)

        # Add contextual HUD elements from analysis
        contextual_elements = self._generate_contextual_elements(analysis)
        hud_elements.extend(contextual_elements)

        return hud_elements

    def _filter_events(self, events: List[Event], current_time: float) -> List[Event]:
        """
        Filter events based on deduplication and cooldowns.

        Args:
            events: Input events
            current_time: Current timestamp

        Returns:
            Filtered events
        """
        filtered = []

        for event in events:
            event_key = f"{event.type}_{event.source}"

            # Check cooldown
            if event_key in self._event_history:
                time_since_last = current_time - self._event_history[event_key]
                cooldown = event.cooldown or self._visual_cooldowns[event.type]

                if time_since_last < cooldown:
                    continue

            # Add event
            filtered.append(event)
            self._event_history[event_key] = current_time

        return filtered

    def _event_to_hud_elements(self, event: Event, analysis: SceneAnalysis) -> List[HUDElement]:
        """
        Convert event to HUD elements.

        Args:
            event: Event to visualize
            analysis: Scene analysis for positioning

        Returns:
            List of HUD elements
        """
        elements = []

        # Color mapping based on priority
        color_map = {
            EventPriority.CRITICAL: (255, 0, 0, 255),      # Red
            EventPriority.HIGH: (255, 165, 0, 255),        # Orange
            EventPriority.MEDIUM: (255, 255, 0, 255),      # Yellow
            EventPriority.LOW: (255, 255, 255, 200),       # White
            EventPriority.INFO: (128, 128, 128, 180),      # Gray
        }

        color = color_map.get(event.priority, (255, 255, 255, 255))

        # Generate elements based on event type
        if event.type == "LOW_HEALTH_WARNING":
            # Health warning at top center
            elements.append(HUDElement(
                type="text",
                position=(960, 50),  # Top center for 1920x1080
                data={"text": "⚠ LOW HEALTH", "size": 32, "bold": True},
                color=color,
                priority=event.priority.value,
                ttl=3.0
            ))

            # Pulsing border effect
            elements.append(HUDElement(
                type="border",
                position=(0, 0),
                data={"style": "pulse", "thickness": 5},
                color=(255, 0, 0, 100),
                priority=event.priority.value,
                ttl=3.0
            ))

        elif event.type == "CRITICAL_DANGER":
            # Danger indicator
            elements.append(HUDElement(
                type="text",
                position=(960, 100),
                data={"text": "⚠⚠ CRITICAL DANGER ⚠⚠", "size": 36, "bold": True},
                color=(255, 0, 0, 255),
                priority=event.priority.value,
                ttl=5.0
            ))

        elif event.type == "HIGH_ENEMY_DENSITY":
            # Warning indicator
            elements.append(HUDElement(
                type="text",
                position=(960, 150),
                data={"text": "⚠ Many Enemies Nearby", "size": 28},
                color=color,
                priority=event.priority.value,
                ttl=4.0
            ))

        else:
            # Generic event display
            elements.append(HUDElement(
                type="text",
                position=(960, 200),
                data={"text": f"{event.type}", "size": 24},
                color=color,
                priority=event.priority.value,
                ttl=2.0
            ))

        return elements

    def _generate_contextual_elements(self, analysis: SceneAnalysis) -> List[HUDElement]:
        """
        Generate contextual HUD elements based on scene analysis.

        Args:
            analysis: Scene analysis

        Returns:
            List of HUD elements
        """
        elements = []

        # Enemy proximity indicators
        for entity in analysis.entities:
            if entity.type.value == "enemy" and entity.threat_score > 0.5:
                # Direction arrow
                elements.append(HUDElement(
                    type="arrow",
                    position=entity.bbox.center,
                    data={
                        "direction": entity.direction or "unknown",
                        "size": 30,
                        "threat": entity.threat_score
                    },
                    color=self._threat_to_color(entity.threat_score),
                    priority=3,
                    ttl=0.5  # Short TTL for dynamic updates
                ))

                # Proximity ring
                if entity.distance_estimate and entity.distance_estimate < 200:
                    elements.append(HUDElement(
                        type="ring",
                        position=entity.bbox.center,
                        data={
                            "radius": int(entity.bbox.width * 0.6),
                            "thickness": 3
                        },
                        color=self._threat_to_color(entity.threat_score),
                        priority=2
                    ))

        # Threat zones
        for zone in analysis.environment_data.get("threat_zones", []):
            elements.append(HUDElement(
                type="zone",
                position=zone["center"],
                data={
                    "radius": 150,
                    "enemy_count": zone["enemy_count"]
                },
                color=(255, 100, 0, 80),
                priority=2
            ))

        return elements

    @staticmethod
    def _threat_to_color(threat_score: float) -> tuple:
        """
        Convert threat score to color.

        Args:
            threat_score: Threat score (0-1)

        Returns:
            RGBA color tuple
        """
        if threat_score > 0.8:
            return (255, 0, 0, 255)      # Red
        elif threat_score > 0.6:
            return (255, 100, 0, 255)    # Orange-Red
        elif threat_score > 0.4:
            return (255, 165, 0, 255)    # Orange
        elif threat_score > 0.2:
            return (255, 255, 0, 255)    # Yellow
        else:
            return (255, 255, 255, 200)  # White

    def set_max_alerts(self, max_alerts: int):
        """Set maximum concurrent alerts."""
        self.max_concurrent_alerts = max_alerts
        logger.info(f"Max concurrent alerts set to {max_alerts}")
