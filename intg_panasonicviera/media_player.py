"""
Panasonic Viera TV Media Player entity.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import logging
from typing import Any
from ucapi import StatusCodes
from ucapi.media_player import (
    Attributes,
    Commands,
    DeviceClasses,
    Features,
    MediaPlayer,
    States,
    MediaType,
    Options,
)
from intg_panasonicviera.config import PanasonicVieraConfig
from intg_panasonicviera.device import PanasonicVieraDevice

_LOG = logging.getLogger(__name__)


class PanasonicVieraMediaPlayer(MediaPlayer):

    def __init__(
        self, device_config: PanasonicVieraConfig, device: PanasonicVieraDevice
    ):
        self._device = device
        self._device_config = device_config

        entity_id = f"media_player.{device_config.identifier}"

        features = [
            Features.ON_OFF,
            Features.VOLUME,
            Features.VOLUME_UP_DOWN,
            Features.MUTE_TOGGLE,
            Features.MUTE,
            Features.UNMUTE,
            Features.PLAY_PAUSE,
            Features.STOP,
            Features.NEXT,
            Features.PREVIOUS,
            Features.FAST_FORWARD,
            Features.REWIND,
            Features.SELECT_SOURCE,
        ]

        attributes = {
            Attributes.STATE: States.UNAVAILABLE,
            Attributes.VOLUME: 0,
            Attributes.MUTED: False,
            Attributes.SOURCE: "",
            Attributes.SOURCE_LIST: [],
        }

        options = {
            Options.SIMPLE_COMMANDS: [
                Commands.ON,
                Commands.OFF,
                Commands.VOLUME_UP,
                Commands.VOLUME_DOWN,
                Commands.MUTE_TOGGLE,
                Commands.MUTE,
                Commands.UNMUTE,
                Commands.PLAY_PAUSE,
                Commands.STOP,
                Commands.NEXT,
                Commands.PREVIOUS,
                Commands.FAST_FORWARD,
                Commands.REWIND,
            ]
        }

        super().__init__(
            entity_id,
            device_config.name,
            features,
            attributes,
            device_class=DeviceClasses.TV,
            cmd_handler=self.handle_command,
            options=options,
        )

        _LOG.info("[%s] Media player entity initialized", self.id)

    async def handle_command(
        self, entity: MediaPlayer, cmd_id: str, params: dict[str, Any] | None
    ) -> StatusCodes:
        _LOG.info("[%s] Command: %s %s", self.id, cmd_id, params or "")

        try:
            if cmd_id == Commands.ON:
                success = await self._device.turn_on()
                return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

            elif cmd_id == Commands.OFF:
                success = await self._device.turn_off()
                return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

            elif cmd_id == Commands.VOLUME:
                if params and "volume" in params:
                    success = await self._device.set_volume(int(params["volume"]))
                    return StatusCodes.OK if success else StatusCodes.SERVER_ERROR
                return StatusCodes.BAD_REQUEST

            elif cmd_id == Commands.VOLUME_UP:
                success = await self._device.volume_up()
                return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

            elif cmd_id == Commands.VOLUME_DOWN:
                success = await self._device.volume_down()
                return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

            elif cmd_id == Commands.MUTE_TOGGLE:
                current_mute = self._device.muted
                success = await self._device.mute(not current_mute)
                return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

            elif cmd_id == Commands.MUTE:
                success = await self._device.mute(True)
                return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

            elif cmd_id == Commands.UNMUTE:
                success = await self._device.mute(False)
                return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

            elif cmd_id == Commands.PLAY_PAUSE:
                success = await self._device.send_key("NRC_PLAY-ONOFF")
                return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

            elif cmd_id == Commands.STOP:
                success = await self._device.send_key("NRC_STOP-ONOFF")
                return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

            elif cmd_id == Commands.NEXT:
                success = await self._device.send_key("NRC_FF-ONOFF")
                return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

            elif cmd_id == Commands.PREVIOUS:
                success = await self._device.send_key("NRC_REW-ONOFF")
                return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

            elif cmd_id == Commands.FAST_FORWARD:
                success = await self._device.send_key("NRC_FF-ONOFF")
                return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

            elif cmd_id == Commands.REWIND:
                success = await self._device.send_key("NRC_REW-ONOFF")
                return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

            elif cmd_id == Commands.SELECT_SOURCE:
                if params and "source" in params:
                    success = await self._device.select_source(params["source"])
                    return StatusCodes.OK if success else StatusCodes.SERVER_ERROR
                return StatusCodes.BAD_REQUEST

            elif cmd_id == Commands.PLAY_MEDIA:
                if params and "media_type" in params and "media_id" in params:
                    media_type = params["media_type"]
                    media_id = params["media_id"]

                    if media_type == MediaType.URL or media_id.startswith("http"):
                        success = await self._device.play_media(media_id)
                        return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

                return StatusCodes.NOT_IMPLEMENTED

            return StatusCodes.NOT_IMPLEMENTED

        except Exception as err:
            _LOG.error("[%s] Command error: %s", self.id, err)
            return StatusCodes.SERVER_ERROR
