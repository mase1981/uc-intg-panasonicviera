"""
Panasonic Viera TV driver for Unfolded Circle Remote.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import logging
from ucapi import Entity, EntityTypes
from ucapi.media_player import Attributes as MediaAttributes
from ucapi_framework import BaseIntegrationDriver
from intg_panasonicviera.config import PanasonicVieraConfig
from intg_panasonicviera.device import PanasonicVieraDevice
from intg_panasonicviera.media_player import PanasonicVieraMediaPlayer
from intg_panasonicviera.remote import PanasonicVieraRemote

_LOG = logging.getLogger(__name__)


class PanasonicVieraDriver(BaseIntegrationDriver[PanasonicVieraDevice, PanasonicVieraConfig]):

    def __init__(self):
        super().__init__(
            device_class=PanasonicVieraDevice,
            entity_classes=[PanasonicVieraMediaPlayer, PanasonicVieraRemote],
            driver_id="panasonicviera",
        )
        self._remote_entities: dict[str, PanasonicVieraRemote] = {}

    def create_entities(
        self, device_config: PanasonicVieraConfig, device: PanasonicVieraDevice
    ) -> list[Entity]:
        _LOG.info("Creating entities for %s", device_config.name)

        remote = PanasonicVieraRemote(device_config, device)
        self._remote_entities[device_config.identifier] = remote

        # Set up callback for app discovery updates
        async def on_apps_discovered(apps):
            await remote.update_discovered_apps(apps)
            _LOG.debug("[%s] Updated remote with %d discovered apps", device_config.identifier, len(apps))

        device._apps_update_callback = on_apps_discovered

        entities = [
            PanasonicVieraMediaPlayer(device_config, device),
            remote,
        ]

        _LOG.info("Created %d entities for %s", len(entities), device_config.name)
        return entities
