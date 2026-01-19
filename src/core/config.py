"""Configuration management and schemas."""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field, validator
from pathlib import Path
import yaml


class CaptureConfig(BaseModel):
    """Screen capture configuration."""
    fps: int = Field(default=60, ge=15, le=144)
    roi: Optional[List[int]] = Field(default=None, description="Region of interest [x, y, w, h]")
    monitor: int = Field(default=0, description="Monitor index to capture")
    format: Literal["RGB", "NV12", "BGR"] = "RGB"


class AIModelConfig(BaseModel):
    """AI model configuration."""
    model: str = Field(default="yolov8n", description="Model identifier")
    confidence: float = Field(default=0.6, ge=0.0, le=1.0)
    iou_threshold: float = Field(default=0.45, ge=0.0, le=1.0)
    device: Literal["cpu", "cuda", "auto"] = "auto"
    batch_size: int = Field(default=1, ge=1, le=8)


class OCRZoneConfig(BaseModel):
    """OCR zone definition."""
    x: int
    y: int
    width: int
    height: int
    label: str
    parser: Optional[str] = None


class OCRConfig(BaseModel):
    """OCR configuration."""
    engine: Literal["tesseract", "easyocr"] = "tesseract"
    language: str = "eng"
    zones: Dict[str, List[int]] = Field(default_factory=dict)


class RuleCondition(BaseModel):
    """Rule condition definition."""
    field: str
    operator: Literal["<", ">", "<=", ">=", "==", "!=", "in", "not_in"]
    value: Any


class RuleAction(BaseModel):
    """Rule action definition."""
    type: Literal["emit", "set", "log", "callback"]
    payload: Any


class Rule(BaseModel):
    """Rule definition."""
    name: str
    state: str
    priority: int = Field(default=0)
    conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    cooldown: float = Field(default=0.0, description="Cooldown in seconds")


class HUDConfig(BaseModel):
    """HUD rendering configuration."""
    theme: str = "tactical_minimal"
    show_proximity_rings: bool = True
    show_direction_arrows: bool = True
    show_health_warnings: bool = True
    opacity: float = Field(default=0.8, ge=0.0, le=1.0)
    scale: float = Field(default=1.0, ge=0.5, le=2.0)


class PerformanceConfig(BaseModel):
    """Performance and quality settings."""
    mode: Literal["SAFE", "PERFORMANCE", "QUALITY", "DEBUG"] = "PERFORMANCE"
    max_latency_ms: int = Field(default=50, ge=10, le=200)
    frame_skip: bool = True
    adaptive_quality: bool = True


class GameProfile(BaseModel):
    """Complete game profile configuration."""
    name: str
    game_id: str
    version: str = "1.0"
    capture: CaptureConfig = Field(default_factory=CaptureConfig)
    ai: AIModelConfig = Field(default_factory=AIModelConfig)
    ocr: OCRConfig = Field(default_factory=OCRConfig)
    rules: List[Rule] = Field(default_factory=list)
    hud: HUDConfig = Field(default_factory=HUDConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    custom: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_yaml(cls, path: Path) -> "GameProfile":
        """Load profile from YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def to_yaml(self, path: Path):
        """Save profile to YAML file."""
        with open(path, "w") as f:
            yaml.safe_dump(self.model_dump(), f, default_flow_style=False)


class SystemConfig(BaseModel):
    """System-wide configuration."""
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    log_dir: Path = Field(default=Path("logs"))
    profile_dir: Path = Field(default=Path("profiles"))
    model_dir: Path = Field(default=Path("models"))
    plugin_dir: Path = Field(default=Path("plugins"))
    telemetry_enabled: bool = False
    watchdog_interval: float = Field(default=5.0, description="Watchdog check interval in seconds")
    crash_recovery: bool = True
