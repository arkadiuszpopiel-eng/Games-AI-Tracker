"""Example custom plugin implementation."""

from plugins import AIModelPlugin, HUDWidgetPlugin
from core.types import Entity, EntityType, BoundingBox


class ExampleAIModel(AIModelPlugin):
    """
    Example custom AI model plugin.

    This demonstrates how to create a custom detection model.
    """

    def __init__(self):
        super().__init__()
        self.name = "ExampleModel"
        self.version = "1.0.0"
        self.api_version = "1.0"
        self.model = None

    def initialize(self, config):
        """Initialize the model."""
        print(f"Initializing {self.name} v{self.version}")

        # Load your custom model here
        # self.model = load_custom_model(config['model_path'])

        return True

    def detect(self, frame):
        """
        Perform detection on frame.

        Args:
            frame: Frame buffer (numpy array)

        Returns:
            List of Entity objects
        """
        entities = []

        # Example: Mock detection
        # In real implementation, run your model inference here

        # Mock entity
        entity = Entity(
            id=0,  # Will be assigned by tracker
            type=EntityType.ENEMY,
            bbox=BoundingBox(x=100, y=100, width=50, height=50),
            confidence=0.9,
            metadata={"model": self.name}
        )

        entities.append(entity)

        return entities

    def shutdown(self):
        """Cleanup resources."""
        print(f"Shutting down {self.name}")
        self.model = None


class ExampleWidget(HUDWidgetPlugin):
    """
    Example custom HUD widget plugin.

    This demonstrates how to create a custom HUD element.
    """

    def __init__(self):
        super().__init__()
        self.name = "ExampleWidget"
        self.version = "1.0.0"
        self.api_version = "1.0"

    def initialize(self, config):
        """Initialize the widget."""
        print(f"Initializing {self.name} v{self.version}")
        self.config = config
        return True

    def render(self, data):
        """
        Render the widget.

        Args:
            data: Widget data dictionary

        Returns:
            HUD element or list of HUD elements
        """
        from core.types import HUDElement

        # Example: Create a custom status widget
        element = HUDElement(
            type="text",
            position=(10, 10),
            data={
                "text": f"Custom Widget: {data.get('status', 'OK')}",
                "size": 14
            },
            color=(0, 255, 0, 255),
            priority=1
        )

        return element

    def shutdown(self):
        """Cleanup resources."""
        print(f"Shutting down {self.name}")


# Example usage
if __name__ == "__main__":
    # Create plugin instances
    ai_plugin = ExampleAIModel()
    widget_plugin = ExampleWidget()

    # Initialize
    ai_plugin.initialize({})
    widget_plugin.initialize({})

    # Use plugins
    import numpy as np

    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    entities = ai_plugin.detect(frame)

    print(f"Detected {len(entities)} entities")

    # Cleanup
    ai_plugin.shutdown()
    widget_plugin.shutdown()
