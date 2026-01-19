"""Watchdog - Monitor module health and auto-recovery."""

from typing import Dict, Callable, Optional
from threading import Thread, Event
import time
from loguru import logger


class ModuleHealthCheck:
    """Health check for a module."""

    def __init__(self, name: str, check_fn: Callable[[], bool], recovery_fn: Optional[Callable[[], None]] = None):
        """
        Initialize health check.

        Args:
            name: Module name
            check_fn: Function to check module health
            recovery_fn: Optional function to recover module
        """
        self.name = name
        self.check_fn = check_fn
        self.recovery_fn = recovery_fn
        self.failures = 0
        self.last_check = time.time()
        self.status = "healthy"


class Watchdog:
    """
    System watchdog for monitoring module health.

    Features:
    - Periodic health checks
    - Automatic recovery attempts
    - Failure tracking and alerting
    - Safe mode fallback
    """

    def __init__(self, check_interval: float = 5.0, max_failures: int = 3):
        """
        Initialize watchdog.

        Args:
            check_interval: Health check interval in seconds
            max_failures: Max failures before safe mode
        """
        self.check_interval = check_interval
        self.max_failures = max_failures

        self._modules: Dict[str, ModuleHealthCheck] = {}
        self._running = False
        self._thread: Optional[Thread] = None
        self._stop_event = Event()
        self._safe_mode = False

    def register_module(
        self,
        name: str,
        check_fn: Callable[[], bool],
        recovery_fn: Optional[Callable[[], None]] = None
    ):
        """
        Register a module for monitoring.

        Args:
            name: Module name
            check_fn: Health check function
            recovery_fn: Optional recovery function
        """
        self._modules[name] = ModuleHealthCheck(name, check_fn, recovery_fn)
        logger.info(f"Registered module for watchdog: {name}")

    def start(self):
        """Start watchdog monitoring."""
        if self._running:
            return

        self._running = True
        self._stop_event.clear()
        self._thread = Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

        logger.info("Watchdog started")

    def stop(self):
        """Stop watchdog monitoring."""
        self._running = False
        self._stop_event.set()

        if self._thread:
            self._thread.join(timeout=2.0)

        logger.info("Watchdog stopped")

    def _monitor_loop(self):
        """Main monitoring loop."""
        while not self._stop_event.wait(self.check_interval):
            for module_name, health_check in self._modules.items():
                try:
                    # Run health check
                    is_healthy = health_check.check_fn()
                    health_check.last_check = time.time()

                    if is_healthy:
                        # Module healthy
                        if health_check.status != "healthy":
                            logger.info(f"Module recovered: {module_name}")
                            health_check.status = "healthy"
                            health_check.failures = 0

                    else:
                        # Module unhealthy
                        health_check.failures += 1
                        health_check.status = "unhealthy"

                        logger.warning(
                            f"Module health check failed: {module_name} "
                            f"(failures: {health_check.failures}/{self.max_failures})"
                        )

                        # Attempt recovery
                        if health_check.recovery_fn and health_check.failures < self.max_failures:
                            logger.info(f"Attempting recovery: {module_name}")
                            try:
                                health_check.recovery_fn()
                            except Exception as e:
                                logger.error(f"Recovery failed for {module_name}: {e}")

                        # Enter safe mode if too many failures
                        if health_check.failures >= self.max_failures:
                            logger.critical(f"Module {module_name} exceeded max failures - entering safe mode")
                            self._enter_safe_mode()

                except Exception as e:
                    logger.error(f"Watchdog error checking {module_name}: {e}")

    def _enter_safe_mode(self):
        """Enter safe mode with minimal functionality."""
        if self._safe_mode:
            return

        self._safe_mode = True
        logger.critical("⚠ ENTERING SAFE MODE ⚠")

        # Safe mode could disable non-essential modules
        # For now, just log the event

    def get_status(self) -> Dict[str, str]:
        """
        Get health status of all modules.

        Returns:
            Dictionary of module statuses
        """
        return {
            name: health_check.status
            for name, health_check in self._modules.items()
        }

    def is_safe_mode(self) -> bool:
        """Check if in safe mode."""
        return self._safe_mode

    @property
    def is_running(self) -> bool:
        """Check if watchdog is running."""
        return self._running
