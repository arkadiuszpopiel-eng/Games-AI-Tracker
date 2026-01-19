"""Profile Manager - Load, save, and manage game profiles."""

from typing import List, Optional, Dict
from pathlib import Path
import yaml
from loguru import logger

from core.config import GameProfile


class ProfileManager:
    """
    Profile management system.

    Features:
    - Load/save profiles from YAML
    - Hot-switch between profiles
    - Profile validation
    - Default profile templates
    """

    def __init__(self, profile_dir: Path = Path("profiles")):
        """
        Initialize profile manager.

        Args:
            profile_dir: Directory containing profile files
        """
        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(parents=True, exist_ok=True)

        self._profiles: Dict[str, GameProfile] = {}
        self._active_profile: Optional[GameProfile] = None

        self._load_all_profiles()

    def _load_all_profiles(self):
        """Load all profiles from profile directory."""
        for profile_file in self.profile_dir.glob("*.yaml"):
            try:
                profile = GameProfile.from_yaml(profile_file)
                self._profiles[profile.game_id] = profile
                logger.info(f"Loaded profile: {profile.name} ({profile.game_id})")
            except Exception as e:
                logger.error(f"Failed to load profile {profile_file}: {e}")

        logger.info(f"Loaded {len(self._profiles)} profiles")

    def get_profile(self, game_id: str) -> Optional[GameProfile]:
        """
        Get profile by game ID.

        Args:
            game_id: Game identifier

        Returns:
            GameProfile or None
        """
        return self._profiles.get(game_id)

    def list_profiles(self) -> List[str]:
        """
        Get list of available profile IDs.

        Returns:
            List of game IDs
        """
        return list(self._profiles.keys())

    def activate_profile(self, game_id: str) -> bool:
        """
        Activate a profile.

        Args:
            game_id: Game identifier

        Returns:
            True if successful
        """
        profile = self._profiles.get(game_id)
        if profile:
            self._active_profile = profile
            logger.info(f"Activated profile: {profile.name}")
            return True

        logger.warning(f"Profile not found: {game_id}")
        return False

    def get_active_profile(self) -> Optional[GameProfile]:
        """Get currently active profile."""
        return self._active_profile

    def save_profile(self, profile: GameProfile) -> bool:
        """
        Save profile to disk.

        Args:
            profile: Profile to save

        Returns:
            True if successful
        """
        try:
            profile_path = self.profile_dir / f"{profile.game_id}.yaml"
            profile.to_yaml(profile_path)
            self._profiles[profile.game_id] = profile
            logger.info(f"Saved profile: {profile.name}")
            return True
        except Exception as e:
            logger.error(f"Failed to save profile: {e}")
            return False

    def create_default_profile(self, game_id: str, game_name: str) -> GameProfile:
        """
        Create a default profile.

        Args:
            game_id: Game identifier
            game_name: Game display name

        Returns:
            New GameProfile
        """
        profile = GameProfile(
            name=game_name,
            game_id=game_id
        )

        logger.info(f"Created default profile: {game_name}")
        return profile

    def delete_profile(self, game_id: str) -> bool:
        """
        Delete a profile.

        Args:
            game_id: Game identifier

        Returns:
            True if successful
        """
        if game_id in self._profiles:
            profile_path = self.profile_dir / f"{game_id}.yaml"
            if profile_path.exists():
                profile_path.unlink()

            del self._profiles[game_id]
            logger.info(f"Deleted profile: {game_id}")
            return True

        return False
