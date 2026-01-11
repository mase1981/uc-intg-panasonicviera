"""
Panasonic Viera TV Remote entity.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import logging
from typing import Any
from ucapi import StatusCodes
from ucapi.remote import Attributes, Commands, Features, Options, Remote
from intg_panasonicviera.config import PanasonicVieraConfig
from intg_panasonicviera.device import PanasonicVieraDevice

_LOG = logging.getLogger(__name__)

VIERA_KEYS = {
    "UP": "NRC_UP-ONOFF",
    "DOWN": "NRC_DOWN-ONOFF",
    "LEFT": "NRC_LEFT-ONOFF",
    "RIGHT": "NRC_RIGHT-ONOFF",
    "OK": "NRC_ENTER-ONOFF",
    "BACK": "NRC_RETURN-ONOFF",
    "EXIT": "NRC_CANCEL-ONOFF",
    "HOME": "NRC_HOME-ONOFF",
    "MENU": "NRC_MENU-ONOFF",
    "PLAY": "NRC_PLAY-ONOFF",
    "PAUSE": "NRC_PAUSE-ONOFF",
    "STOP": "NRC_STOP-ONOFF",
    "REW": "NRC_REW-ONOFF",
    "FF": "NRC_FF-ONOFF",
    "SKIP_BACK": "NRC_SKIP_PREV-ONOFF",
    "SKIP_FWD": "NRC_SKIP_NEXT-ONOFF",
    "REC": "NRC_REC-ONOFF",
    "VOL_UP": "NRC_VOLUP-ONOFF",
    "VOL_DOWN": "NRC_VOLDOWN-ONOFF",
    "MUTE": "NRC_MUTE-ONOFF",
    "CH_UP": "NRC_CH_UP-ONOFF",
    "CH_DOWN": "NRC_CH_DOWN-ONOFF",
    "PREV_CH": "NRC_CHG_INPUT-ONOFF",
    "RED": "NRC_RED-ONOFF",
    "GREEN": "NRC_GREEN-ONOFF",
    "YELLOW": "NRC_YELLOW-ONOFF",
    "BLUE": "NRC_BLUE-ONOFF",
    "NETFLIX": "NRC_NETFLIX-ONOFF",
    "APPS": "NRC_APPS-ONOFF",
    "INPUT": "NRC_INPUT-ONOFF",
    "TV": "NRC_TV-ONOFF",
    "AV": "NRC_CHG_INPUT-ONOFF",
    "INFO": "NRC_INFO-ONOFF",
    "GUIDE": "NRC_GUIDE-ONOFF",
    "EPG": "NRC_EPG-ONOFF",
    "3D": "NRC_3D-ONOFF",
    "ASPECT": "NRC_P_NR-ONOFF",
    "STTL": "NRC_STTL-ONOFF",
    "SAP": "NRC_SAP-ONOFF",
    "NUM_0": "NRC_D0-ONOFF",
    "NUM_1": "NRC_D1-ONOFF",
    "NUM_2": "NRC_D2-ONOFF",
    "NUM_3": "NRC_D3-ONOFF",
    "NUM_4": "NRC_D4-ONOFF",
    "NUM_5": "NRC_D5-ONOFF",
    "NUM_6": "NRC_D6-ONOFF",
    "NUM_7": "NRC_D7-ONOFF",
    "NUM_8": "NRC_D8-ONOFF",
    "NUM_9": "NRC_D9-ONOFF",
}


class PanasonicVieraRemote(Remote):

    def __init__(
        self, device_config: PanasonicVieraConfig, device: PanasonicVieraDevice
    ):
        self._device = device
        self._device_config = device_config

        entity_id = f"remote.{device_config.identifier}"

        simple_commands = list(VIERA_KEYS.keys())

        ui_pages = [
            {
                "page_id": "navigation",
                "name": "Navigation",
                "grid": {"width": 3, "height": 4},
                "items": [
                    {"command": {"cmd_id": "HOME"}, "location": {"x": 0, "y": 0}},
                    {"command": {"cmd_id": "UP"}, "location": {"x": 1, "y": 0}},
                    {"command": {"cmd_id": "MENU"}, "location": {"x": 2, "y": 0}},
                    {"command": {"cmd_id": "LEFT"}, "location": {"x": 0, "y": 1}},
                    {"command": {"cmd_id": "OK"}, "location": {"x": 1, "y": 1}},
                    {"command": {"cmd_id": "RIGHT"}, "location": {"x": 2, "y": 1}},
                    {"command": {"cmd_id": "BACK"}, "location": {"x": 0, "y": 2}},
                    {"command": {"cmd_id": "DOWN"}, "location": {"x": 1, "y": 2}},
                    {"command": {"cmd_id": "EXIT"}, "location": {"x": 2, "y": 2}},
                    {"command": {"cmd_id": "INFO"}, "location": {"x": 0, "y": 3}},
                    {"command": {"cmd_id": "GUIDE"}, "location": {"x": 1, "y": 3}},
                    {"command": {"cmd_id": "APPS"}, "location": {"x": 2, "y": 3}},
                ],
            },
            {
                "page_id": "playback",
                "name": "Playback",
                "grid": {"width": 3, "height": 3},
                "items": [
                    {"command": {"cmd_id": "SKIP_BACK"}, "location": {"x": 0, "y": 0}},
                    {"command": {"cmd_id": "PLAY"}, "location": {"x": 1, "y": 0}},
                    {"command": {"cmd_id": "SKIP_FWD"}, "location": {"x": 2, "y": 0}},
                    {"command": {"cmd_id": "REW"}, "location": {"x": 0, "y": 1}},
                    {"command": {"cmd_id": "PAUSE"}, "location": {"x": 1, "y": 1}},
                    {"command": {"cmd_id": "FF"}, "location": {"x": 2, "y": 1}},
                    {"command": {"cmd_id": "REC"}, "location": {"x": 0, "y": 2}},
                    {"command": {"cmd_id": "STOP"}, "location": {"x": 1, "y": 2}},
                ],
            },
            {
                "page_id": "channels",
                "name": "Channels",
                "grid": {"width": 3, "height": 4},
                "items": [
                    {"command": {"cmd_id": "NUM_1"}, "location": {"x": 0, "y": 0}},
                    {"command": {"cmd_id": "NUM_2"}, "location": {"x": 1, "y": 0}},
                    {"command": {"cmd_id": "NUM_3"}, "location": {"x": 2, "y": 0}},
                    {"command": {"cmd_id": "NUM_4"}, "location": {"x": 0, "y": 1}},
                    {"command": {"cmd_id": "NUM_5"}, "location": {"x": 1, "y": 1}},
                    {"command": {"cmd_id": "NUM_6"}, "location": {"x": 2, "y": 1}},
                    {"command": {"cmd_id": "NUM_7"}, "location": {"x": 0, "y": 2}},
                    {"command": {"cmd_id": "NUM_8"}, "location": {"x": 1, "y": 2}},
                    {"command": {"cmd_id": "NUM_9"}, "location": {"x": 2, "y": 2}},
                    {"command": {"cmd_id": "CH_DOWN"}, "location": {"x": 0, "y": 3}},
                    {"command": {"cmd_id": "NUM_0"}, "location": {"x": 1, "y": 3}},
                    {"command": {"cmd_id": "CH_UP"}, "location": {"x": 2, "y": 3}},
                ],
            },
            {
                "page_id": "color_input",
                "name": "Color & Input",
                "grid": {"width": 2, "height": 4},
                "items": [
                    {"command": {"cmd_id": "RED"}, "location": {"x": 0, "y": 0}},
                    {"command": {"cmd_id": "GREEN"}, "location": {"x": 1, "y": 0}},
                    {"command": {"cmd_id": "YELLOW"}, "location": {"x": 0, "y": 1}},
                    {"command": {"cmd_id": "BLUE"}, "location": {"x": 1, "y": 1}},
                    {"command": {"cmd_id": "INPUT"}, "location": {"x": 0, "y": 2}},
                    {"command": {"cmd_id": "TV"}, "location": {"x": 1, "y": 2}},
                    {"command": {"cmd_id": "AV"}, "location": {"x": 0, "y": 3}},
                    {"command": {"cmd_id": "NETFLIX"}, "location": {"x": 1, "y": 3}},
                ],
            },
        ]

        attributes = {Attributes.STATE: "UNKNOWN"}

        options = {
            Options.SIMPLE_COMMANDS: simple_commands,
            Options.USER_INTERFACE: {"pages": ui_pages},
        }

        super().__init__(
            entity_id,
            device_config.name,
            [Features.SEND_CMD],
            attributes,
            cmd_handler=self.handle_command,
            options=options,
        )

        _LOG.info("[%s] Remote entity initialized with %d commands", self.id, len(simple_commands))

    async def handle_command(
        self, entity: Remote, cmd_id: str, params: dict[str, Any] | None
    ) -> StatusCodes:
        _LOG.info("[%s] Command: %s %s", self.id, cmd_id, params or "")

        try:
            if cmd_id == Commands.SEND_CMD:
                if params and "command" in params:
                    key_name = params["command"]
                    if key_name in VIERA_KEYS:
                        key_code = VIERA_KEYS[key_name]
                        success = await self._device.send_key(key_code)
                        return StatusCodes.OK if success else StatusCodes.SERVER_ERROR
                    else:
                        _LOG.warning("[%s] Unknown key: %s", self.id, key_name)
                        return StatusCodes.BAD_REQUEST
                return StatusCodes.BAD_REQUEST

            if cmd_id in VIERA_KEYS:
                key_code = VIERA_KEYS[cmd_id]
                success = await self._device.send_key(key_code)
                return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

            return StatusCodes.NOT_IMPLEMENTED

        except Exception as err:
            _LOG.error("[%s] Command error: %s", self.id, err)
            return StatusCodes.SERVER_ERROR
