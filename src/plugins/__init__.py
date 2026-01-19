"""Plugin system for extensibility."""

from typing import Protocol, Dict, Any, Optional
from abc import ABC, abstractmethod


class PluginInterface(Protocol):
    """Base interface for all plugins."""

    name: str
    version: str
    api_version: str

    def initialize(self, config: Dict[str, Any]) -> bool:
        """Initialize plugin with configuration."""
        ...

    def shutdown(self) -> None:
        """Shutdown and cleanup plugin."""
        ...


class AIModelPlugin(ABC):
    """Base class for AI model plugins."""

    def __init__(self):
        self.name = "BaseAIModel"
        self.version = "1.0.0"
        self.api_version = "1.0"

    @abstractmethod
    def detect(self, frame) -> list:
        """Detect entities in frame."""
        pass


class HUDWidgetPlugin(ABC):
    """Base class for HUD widget plugins."""

    def __init__(self):
        self.name = "BaseWidget"
        self.version = "1.0.0"
        self.api_version = "1.0"

    @abstractmethod
    def render(self, data: Dict[str, Any]):
        """Render widget."""
        pass


class RulePackPlugin(ABC):
    """Base class for rule pack plugins."""

    def __init__(self):
        self.name = "BaseRulePack"
        self.version = "1.0.0"
        self.api_version = "1.0"

    @abstractmethod
    def get_rules(self) -> list:
        """Get rules from pack."""
        pass
