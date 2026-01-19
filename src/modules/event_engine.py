"""Context & Event Engine - FSM, rule engine, and event emission."""

from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import time
from loguru import logger

from core.types import Event, EventPriority, SceneAnalysis, SceneState
from core.config import Rule


class RuleEvaluator:
    """
    Rule evaluation engine.

    Evaluates conditions and triggers actions based on scene state.
    """

    def __init__(self, rules: List[Rule]):
        """
        Initialize rule evaluator.

        Args:
            rules: List of rules to evaluate
        """
        self.rules = sorted(rules, key=lambda r: r.priority, reverse=True)
        self._last_triggered: Dict[str, float] = {}

    def evaluate(self, analysis: SceneAnalysis) -> List[Event]:
        """
        Evaluate rules against current scene analysis.

        Args:
            analysis: Scene analysis result

        Returns:
            List of triggered events
        """
        events = []
        current_time = time.time()

        for rule in self.rules:
            # Check if rule applies to current state
            if rule.state != analysis.state.value and rule.state != "*":
                continue

            # Check cooldown
            rule_key = f"{rule.name}_{rule.state}"
            if rule_key in self._last_triggered:
                time_since_last = current_time - self._last_triggered[rule_key]
                if time_since_last < rule.cooldown:
                    continue

            # Evaluate conditions
            if self._evaluate_conditions(rule.conditions, analysis):
                # Execute actions
                for action_config in rule.actions:
                    event = self._execute_action(action_config, analysis, rule)
                    if event:
                        events.append(event)

                # Update cooldown
                if rule.cooldown > 0:
                    self._last_triggered[rule_key] = current_time

        return events

    def _evaluate_conditions(self, conditions: List[Dict[str, Any]], analysis: SceneAnalysis) -> bool:
        """
        Evaluate all conditions for a rule.

        Args:
            conditions: List of condition dictionaries
            analysis: Scene analysis

        Returns:
            True if all conditions pass
        """
        for condition in conditions:
            if not self._evaluate_single_condition(condition, analysis):
                return False
        return True

    def _evaluate_single_condition(self, condition: Dict[str, Any], analysis: SceneAnalysis) -> bool:
        """
        Evaluate a single condition.

        Args:
            condition: Condition dictionary
            analysis: Scene analysis

        Returns:
            True if condition passes
        """
        # Parse condition string (e.g., "enemy.distance < 3")
        if isinstance(condition, str):
            return self._evaluate_condition_string(condition, analysis)

        # Dictionary format
        field = condition.get("field")
        operator = condition.get("operator")
        value = condition.get("value")

        if not all([field, operator, value]):
            return False

        # Extract actual value from analysis
        actual_value = self._extract_field_value(field, analysis)
        if actual_value is None:
            return False

        # Apply operator
        return self._apply_operator(actual_value, operator, value)

    def _evaluate_condition_string(self, condition: str, analysis: SceneAnalysis) -> bool:
        """
        Evaluate condition from string format.

        Args:
            condition: Condition string (e.g., "enemy.distance < 3")
            analysis: Scene analysis

        Returns:
            True if condition passes
        """
        # Simple parser for conditions like "enemy.distance < 3"
        operators = ['<=', '>=', '==', '!=', '<', '>']
        operator = None

        for op in operators:
            if op in condition:
                operator = op
                break

        if not operator:
            return False

        parts = condition.split(operator)
        if len(parts) != 2:
            return False

        field = parts[0].strip()
        value_str = parts[1].strip()

        try:
            value = float(value_str) if '.' in value_str else int(value_str)
        except ValueError:
            value = value_str

        actual_value = self._extract_field_value(field, analysis)
        if actual_value is None:
            return False

        return self._apply_operator(actual_value, operator, value)

    def _extract_field_value(self, field: str, analysis: SceneAnalysis) -> Any:
        """
        Extract field value from analysis.

        Args:
            field: Field path (e.g., "enemy.distance", "player.hp")
            analysis: Scene analysis

        Returns:
            Field value or None
        """
        parts = field.split('.')

        if parts[0] == "enemy":
            # Get closest enemy
            enemies = [e for e in analysis.entities if e.type.value == "enemy"]
            if not enemies:
                return None

            # Sort by distance estimate or threat score
            closest_enemy = min(enemies, key=lambda e: e.distance_estimate or e.threat_score)

            if len(parts) == 2:
                attr = parts[1]
                if attr == "distance":
                    return closest_enemy.distance_estimate
                elif attr == "threat_score":
                    return closest_enemy.threat_score
                elif hasattr(closest_enemy, attr):
                    return getattr(closest_enemy, attr)

        elif parts[0] == "player":
            player = analysis.player_state
            if len(parts) == 2:
                attr = parts[1]
                if hasattr(player, attr):
                    return getattr(player, attr)

        elif parts[0] == "scene":
            if len(parts) == 2:
                attr = parts[1]
                if attr == "state":
                    return analysis.state.value
                elif attr == "confidence":
                    return analysis.confidence

        elif parts[0] == "environment":
            env = analysis.environment_data
            if len(parts) == 2:
                return env.get(parts[1])

        return None

    def _apply_operator(self, actual: Any, operator: str, expected: Any) -> bool:
        """Apply comparison operator."""
        try:
            if operator == '<':
                return actual < expected
            elif operator == '>':
                return actual > expected
            elif operator == '<=':
                return actual <= expected
            elif operator == '>=':
                return actual >= expected
            elif operator == '==':
                return actual == expected
            elif operator == '!=':
                return actual != expected
        except TypeError:
            return False
        return False

    def _execute_action(self, action: Dict[str, Any], analysis: SceneAnalysis, rule: Rule) -> Optional[Event]:
        """
        Execute rule action.

        Args:
            action: Action configuration
            analysis: Scene analysis
            rule: Source rule

        Returns:
            Event or None
        """
        action_type = action.get("type")
        payload = action.get("payload")

        if action_type == "emit":
            # Emit event
            event_type = payload if isinstance(payload, str) else action.get("event", "RULE_TRIGGERED")

            # Determine priority
            priority_map = {
                "LOW_HEALTH": EventPriority.CRITICAL,
                "CRITICAL_DANGER": EventPriority.CRITICAL,
                "HIGH_RISK": EventPriority.HIGH,
                "WARNING": EventPriority.MEDIUM,
            }
            priority = priority_map.get(event_type, EventPriority.INFO)

            return Event(
                type=event_type,
                priority=priority,
                data={
                    "rule": rule.name,
                    "state": analysis.state.value,
                    "payload": payload
                },
                source="rule_engine",
                cooldown=rule.cooldown
            )

        elif action_type == "log":
            logger.info(f"Rule action log: {payload}")

        return None


class ContextEngine:
    """
    Context & Event Engine.

    Features:
    - Finite State Machine (FSM)
    - Rule-based event emission
    - Context tracking
    """

    def __init__(self, rules: List[Rule]):
        """
        Initialize context engine.

        Args:
            rules: List of rules
        """
        self.evaluator = RuleEvaluator(rules)
        self._current_state: Optional[SceneState] = None
        self._state_duration: float = 0.0
        self._state_start_time: float = time.time()

    def process(self, analysis: SceneAnalysis) -> List[Event]:
        """
        Process scene analysis and generate events.

        Args:
            analysis: Scene analysis

        Returns:
            List of events
        """
        current_time = time.time()

        # Track state changes
        if self._current_state != analysis.state:
            if self._current_state is not None:
                logger.debug(f"State transition: {self._current_state.value} -> {analysis.state.value}")

            self._current_state = analysis.state
            self._state_start_time = current_time
            self._state_duration = 0.0
        else:
            self._state_duration = current_time - self._state_start_time

        # Evaluate rules
        events = self.evaluator.evaluate(analysis)

        # Add automatic events based on analysis
        auto_events = self._generate_automatic_events(analysis)
        events.extend(auto_events)

        return events

    def _generate_automatic_events(self, analysis: SceneAnalysis) -> List[Event]:
        """
        Generate automatic events based on analysis.

        Args:
            analysis: Scene analysis

        Returns:
            List of automatic events
        """
        events = []

        # Low health warning
        player = analysis.player_state
        if player.hp is not None and player.hp_max is not None:
            hp_ratio = player.hp / player.hp_max
            if hp_ratio < 0.2:
                events.append(Event(
                    type="LOW_HEALTH_WARNING",
                    priority=EventPriority.CRITICAL,
                    data={"hp": player.hp, "hp_max": player.hp_max},
                    source="auto"
                ))

        # High enemy density
        env = analysis.environment_data
        if env.get("enemy_density", 0) > 5:
            events.append(Event(
                type="HIGH_ENEMY_DENSITY",
                priority=EventPriority.HIGH,
                data={"density": env["enemy_density"]},
                source="auto"
            ))

        return events

    def get_context(self) -> Dict[str, Any]:
        """Get current context information."""
        return {
            "current_state": self._current_state.value if self._current_state else None,
            "state_duration": self._state_duration,
        }
