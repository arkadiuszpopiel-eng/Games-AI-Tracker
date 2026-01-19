"""Main application entry point."""

import sys
import signal
from pathlib import Path
from loguru import logger

from core.config import SystemConfig, GameProfile
from core.pipeline import AIVisionPipeline
from utils.profile_manager import ProfileManager


class AIVisionApp:
    """
    Main application controller.

    Manages the complete AI Vision Overlay system lifecycle.
    """

    def __init__(self):
        """Initialize application."""
        self.system_config = SystemConfig()
        self.profile_manager = ProfileManager(self.system_config.profile_dir)
        self.pipeline: AIVisionPipeline = None

        self._setup_logging()

        logger.info("=" * 60)
        logger.info("AI Vision Overlay System v0.1.0")
        logger.info("External • Safe • Modular • Enterprise-Grade")
        logger.info("=" * 60)

    def _setup_logging(self):
        """Setup logging configuration."""
        log_dir = Path(self.system_config.log_dir)
        log_dir.mkdir(parents=True, exist_ok=True)

        logger.add(
            log_dir / "ai_vision_{time}.log",
            rotation="10 MB",
            retention="7 days",
            level=self.system_config.log_level
        )

    def start(self, profile_id: str = None):
        """
        Start the application with a profile.

        Args:
            profile_id: Game profile to use (optional)
        """
        # Load profile
        if profile_id:
            if not self.profile_manager.activate_profile(profile_id):
                logger.error(f"Failed to load profile: {profile_id}")
                return False
        else:
            # Use first available profile or create default
            profiles = self.profile_manager.list_profiles()
            if profiles:
                self.profile_manager.activate_profile(profiles[0])
            else:
                logger.warning("No profiles found, creating default profile")
                default_profile = self.profile_manager.create_default_profile("default", "Default Game")
                self.profile_manager.save_profile(default_profile)
                self.profile_manager.activate_profile("default")

        active_profile = self.profile_manager.get_active_profile()
        if not active_profile:
            logger.error("No active profile")
            return False

        logger.info(f"Using profile: {active_profile.name}")

        # Initialize pipeline
        try:
            self.pipeline = AIVisionPipeline(active_profile, self.system_config)
            self.pipeline.start()
            return True
        except Exception as e:
            logger.error(f"Failed to start pipeline: {e}")
            return False

    def stop(self):
        """Stop the application."""
        if self.pipeline:
            self.pipeline.stop()

    def run(self, profile_id: str = None):
        """
        Run the application (blocking).

        Args:
            profile_id: Game profile to use
        """
        # Setup signal handlers
        def signal_handler(sig, frame):
            logger.info("Received shutdown signal")
            self.stop()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Start application
        if not self.start(profile_id):
            logger.error("Failed to start application")
            return 1

        logger.info("Application running. Press Ctrl+C to stop.")

        # Keep running
        try:
            while self.pipeline and self.pipeline.is_running:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")

        self.stop()
        return 0


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI Vision Overlay System - External AI-powered game overlay"
    )
    parser.add_argument(
        "--profile",
        "-p",
        type=str,
        help="Game profile to use"
    )
    parser.add_argument(
        "--list-profiles",
        "-l",
        action="store_true",
        help="List available profiles"
    )

    args = parser.parse_args()

    app = AIVisionApp()

    if args.list_profiles:
        profiles = app.profile_manager.list_profiles()
        print("\nAvailable profiles:")
        for profile_id in profiles:
            profile = app.profile_manager.get_profile(profile_id)
            print(f"  - {profile_id}: {profile.name}")
        return 0

    return app.run(profile_id=args.profile)


if __name__ == "__main__":
    sys.exit(main())
