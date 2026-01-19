"""OCR & UI Parsing - Extract game state from UI elements."""

from typing import List, Dict, Optional, Any
import numpy as np
import re
from loguru import logger

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError:
    EASYOCR_AVAILABLE = False

from core.types import OCRResult, PlayerState, BoundingBox
from core.config import OCRConfig


class OCREngine:
    """
    OCR Engine for extracting text from game UI.

    Features:
    - Multiple OCR backends (Tesseract, EasyOCR)
    - Zone-based extraction
    - Value parsing (HP, stamina, etc.)
    - Pattern matching for combat messages
    """

    def __init__(self, config: OCRConfig):
        """
        Initialize OCR engine.

        Args:
            config: OCR configuration
        """
        self.config = config
        self.reader = None

        if config.engine == "easyocr" and EASYOCR_AVAILABLE:
            self.reader = easyocr.Reader([config.language], gpu=False)
            logger.info("EasyOCR initialized")
        elif config.engine == "tesseract" and TESSERACT_AVAILABLE:
            logger.info("Tesseract OCR initialized")
        else:
            logger.warning("No OCR engine available - running in mock mode")

    def extract_zones(self, frame: np.ndarray) -> List[OCRResult]:
        """
        Extract text from configured zones.

        Args:
            frame: Frame buffer (uint8, 0-255)

        Returns:
            List of OCR results
        """
        results = []

        for zone_name, zone_coords in self.config.zones.items():
            x, y, w, h = zone_coords

            # Crop zone
            zone_img = frame[y:y+h, x:x+w]

            # Run OCR
            text, confidence = self._ocr_image(zone_img)

            # Parse value
            parsed_value = self._parse_zone_value(zone_name, text)

            result = OCRResult(
                zone=zone_name,
                text=text,
                confidence=confidence,
                bbox=BoundingBox(x=x, y=y, width=w, height=h),
                parsed_value=parsed_value
            )
            results.append(result)

        return results

    def _ocr_image(self, image: np.ndarray) -> tuple[str, float]:
        """
        Run OCR on image region.

        Args:
            image: Image buffer

        Returns:
            Tuple of (text, confidence)
        """
        if self.config.engine == "easyocr" and self.reader:
            try:
                result = self.reader.readtext(image, detail=1)
                if result:
                    text = " ".join([r[1] for r in result])
                    confidence = sum([r[2] for r in result]) / len(result)
                    return text.strip(), confidence
                return "", 0.0
            except Exception as e:
                logger.debug(f"EasyOCR error: {e}")
                return "", 0.0

        elif self.config.engine == "tesseract" and TESSERACT_AVAILABLE:
            try:
                text = pytesseract.image_to_string(image, config='--psm 7')
                # Tesseract doesn't provide confidence easily
                return text.strip(), 0.8
            except Exception as e:
                logger.debug(f"Tesseract error: {e}")
                return "", 0.0

        # Mock mode
        return self._mock_ocr(), 0.9

    def _mock_ocr(self) -> str:
        """Generate mock OCR text for testing."""
        return "100/120"

    def _parse_zone_value(self, zone_name: str, text: str) -> Any:
        """
        Parse OCR text to extract meaningful values.

        Args:
            zone_name: Zone identifier
            text: OCR extracted text

        Returns:
            Parsed value
        """
        # Health parsing: "123 / 200" or "123/200" or "123"
        if "health" in zone_name.lower() or "hp" in zone_name.lower():
            return self._parse_health(text)

        # Stamina parsing
        if "stamina" in zone_name.lower():
            return self._parse_stamina(text)

        # Mana parsing
        if "mana" in zone_name.lower() or "mp" in zone_name.lower():
            return self._parse_mana(text)

        # Number parsing
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])

        return text

    def _parse_health(self, text: str) -> Dict[str, int]:
        """Parse health value from text."""
        # Match patterns like "123 / 200" or "123/200"
        match = re.search(r'(\d+)\s*/\s*(\d+)', text)
        if match:
            return {
                "current": int(match.group(1)),
                "max": int(match.group(2))
            }

        # Single number
        numbers = re.findall(r'\d+', text)
        if numbers:
            return {"current": int(numbers[0]), "max": None}

        return {"current": None, "max": None}

    def _parse_stamina(self, text: str) -> Dict[str, int]:
        """Parse stamina value from text."""
        return self._parse_health(text)  # Same format

    def _parse_mana(self, text: str) -> Dict[str, int]:
        """Parse mana value from text."""
        return self._parse_health(text)  # Same format

    def extract_player_state(self, ocr_results: List[OCRResult]) -> PlayerState:
        """
        Build player state from OCR results.

        Args:
            ocr_results: List of OCR extraction results

        Returns:
            Player state object
        """
        state = PlayerState()

        for result in ocr_results:
            zone = result.zone.lower()
            value = result.parsed_value

            if isinstance(value, dict):
                if "health" in zone or "hp" in zone:
                    state.hp = value.get("current")
                    state.hp_max = value.get("max")
                elif "stamina" in zone:
                    state.stamina = value.get("current")
                    state.stamina_max = value.get("max")
                elif "mana" in zone or "mp" in zone:
                    state.mana = value.get("current")
                    state.mana_max = value.get("max")

        # Determine combat state
        if state.hp is not None and state.hp_max is not None:
            hp_ratio = state.hp / state.hp_max
            if hp_ratio < 0.3:
                state.alerts.append("low_health")
            if hp_ratio < 0.1:
                state.alerts.append("critical_health")

        return state


class UICombatParser:
    """Parse combat-related UI messages."""

    def __init__(self):
        """Initialize combat parser."""
        self.combat_patterns = {
            "damage_taken": re.compile(r'(-\d+)|(\d+\s+damage)', re.IGNORECASE),
            "damage_dealt": re.compile(r'(\+\d+)|(hit\s+for\s+\d+)', re.IGNORECASE),
            "status_effect": re.compile(r'(poisoned|stunned|burned|frozen)', re.IGNORECASE),
        }

    def parse_combat_messages(self, text: str) -> Dict[str, Any]:
        """
        Parse combat messages from UI text.

        Args:
            text: Text to parse

        Returns:
            Dictionary of parsed combat info
        """
        result = {
            "damage_taken": None,
            "damage_dealt": None,
            "status_effects": []
        }

        for key, pattern in self.combat_patterns.items():
            matches = pattern.findall(text)
            if matches:
                if key == "status_effect":
                    result["status_effects"].extend([m[0] for m in matches if m])
                else:
                    result[key] = matches[0]

        return result
