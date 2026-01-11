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

    def create_entities(
        self, device_config: PanasonicVieraConfig, device: PanasonicVieraDevice
    ) -> list[Entity]:
        _LOG.info("Creating entities for %s", device_config.name)

        entities = [
            PanasonicVieraMediaPlayer(device_config, device),
            PanasonicVieraRemote(device_config, device),
        ]

        _LOG.info("Created %d entities for %s", len(entities), device_config.name)
        return entities

    async def refresh_entity_state(self, entity_id: str) -> None:
        _LOG.debug("[%s] Refreshing entity state", entity_id)

        device_id = self.device_from_entity_id(entity_id)
        if not device_id:
            _LOG.warning("[%s] Could not extract device_id", entity_id)
            return

        device = self._configured_devices.get(device_id)
        if not device:
            _LOG.warning("[%s] Device %s not found", entity_id, device_id)
            return

        configured_entity = self.api.configured_entities.get(entity_id)
        if not configured_entity:
            _LOG.debug("[%s] Entity not configured yet", entity_id)
            return

        if not device.is_connected:
            _LOG.debug("[%s] Device not connected, marking unavailable", entity_id)
            await super().refresh_entity_state(entity_id)
            return

        if configured_entity.entity_type == EntityTypes.MEDIA_PLAYER:
            source_list = device.source_list
            if not source_list:
                source_list = await device.get_sources()

            if source_list:
                self.api.configured_entities.update_attributes(
                    entity_id, {MediaAttributes.SOURCE_LIST: source_list}
                )
                _LOG.info("[%s] Updated entity state with %d sources", entity_id, len(source_list))
