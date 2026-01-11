"""
Panasonic Viera TV driver for Unfolded Circle Remote.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import logging
from ucapi import Entity
from ucapi_framework import BaseIntegrationDriver
from intg_panasonicviera.config import PanasonicVieraConfig
from intg_panasonicviera.device import PanasonicVieraDevice
from intg_panasonicviera.media_player import PanasonicVieraMediaPlayer
from intg_panasonicviera.remote import PanasonicVieraRemote

_LOG = logging.getLogger(__name__)


class PanasonicVieraDriver(BaseIntegrationDriver[PanasonicVieraDevice, PanasonicVieraConfig]):
    """Panasonic Viera TV integration driver."""

    def __init__(self):
        """Initialize the driver."""
        super().__init__(
            device_class=PanasonicVieraDevice,
            entity_classes=[PanasonicVieraMediaPlayer, PanasonicVieraRemote],
            driver_id="panasonicviera",
        )

    def create_entities(
        self, device_config: PanasonicVieraConfig, device: PanasonicVieraDevice
    ) -> list[Entity]:
        """Create entity instances."""
        _LOG.info("Creating entities for %s", device_config.name)

        entities = [
            PanasonicVieraMediaPlayer(device_config, device),
            PanasonicVieraRemote(device_config, device),
        ]

        _LOG.info("Created %d entities for %s", len(entities), device_config.name)
        return entities
