"""
Panasonic Viera TV configuration for Unfolded Circle integration.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

from dataclasses import dataclass
from ucapi_framework import BaseConfigManager


@dataclass
class PanasonicVieraConfig:
    """Panasonic Viera TV configuration."""

    identifier: str
    name: str
    host: str
    port: int = 55000
    app_id: str | None = None
    encryption_key: str | None = None
    mac_address: str | None = None


class PanasonicVieraConfigManager(BaseConfigManager[PanasonicVieraConfig]):
    """Configuration manager with automatic JSON persistence."""

    pass
