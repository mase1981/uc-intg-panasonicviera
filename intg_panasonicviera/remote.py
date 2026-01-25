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

# Complete list of all Panasonic Viera NRC key codes
# Includes all keys from panasonic-viera library for maximum TV model compatibility
VIERA_KEYS = {
    # Navigation
    "UP": "NRC_UP-ONOFF",
    "DOWN": "NRC_DOWN-ONOFF",
    "LEFT": "NRC_LEFT-ONOFF",
    "RIGHT": "NRC_RIGHT-ONOFF",
    "OK": "NRC_ENTER-ONOFF",
    "ENTER": "NRC_ENTER-ONOFF",
    "BACK": "NRC_RETURN-ONOFF",
    "RETURN": "NRC_RETURN-ONOFF",
    "EXIT": "NRC_CANCEL-ONOFF",
    "CANCEL": "NRC_CANCEL-ONOFF",
    "HOME": "NRC_HOME-ONOFF",
    "MENU": "NRC_MENU-ONOFF",
    "OPTION": "NRC_SUBMENU-ONOFF",
    "INDEX": "NRC_INDEX-ONOFF",
    # Playback
    "PLAY": "NRC_PLAY-ONOFF",
    "PAUSE": "NRC_PAUSE-ONOFF",
    "STOP": "NRC_STOP-ONOFF",
    "REW": "NRC_REW-ONOFF",
    "REWIND": "NRC_REW-ONOFF",
    "FF": "NRC_FF-ONOFF",
    "FAST_FORWARD": "NRC_FF-ONOFF",
    "SKIP_BACK": "NRC_SKIP_PREV-ONOFF",
    "SKIP_PREV": "NRC_SKIP_PREV-ONOFF",
    "SKIP_FWD": "NRC_SKIP_NEXT-ONOFF",
    "SKIP_NEXT": "NRC_SKIP_NEXT-ONOFF",
    "REC": "NRC_REC-ONOFF",
    "RECORD": "NRC_REC-ONOFF",
    "THIRTY_SECOND_SKIP": "NRC_30S_SKIP-ONOFF",
    # Volume & Audio
    "VOL_UP": "NRC_VOLUP-ONOFF",
    "VOLUME_UP": "NRC_VOLUP-ONOFF",
    "VOL_DOWN": "NRC_VOLDOWN-ONOFF",
    "VOLUME_DOWN": "NRC_VOLDOWN-ONOFF",
    "MUTE": "NRC_MUTE-ONOFF",
    "SURROUND": "NRC_SURROUND-ONOFF",
    "SAP": "NRC_SAP-ONOFF",
    "MPX": "NRC_MPX-ONOFF",
    # Channel & Input
    "CH_UP": "NRC_CH_UP-ONOFF",
    "CH_DOWN": "NRC_CH_DOWN-ONOFF",
    "INPUT": "NRC_CHG_INPUT-ONOFF",
    "INPUT_KEY": "NRC_CHG_INPUT-ONOFF",
    "AV": "NRC_CHG_INPUT-ONOFF",
    "PREV_CH": "NRC_CHG_INPUT-ONOFF",
    "TV": "NRC_TV-ONOFF",
    "HDMI1": "NRC_HDMI1-ONOFF",
    "HDMI2": "NRC_HDMI2-ONOFF",
    "HDMI3": "NRC_HDMI3-ONOFF",
    "HDMI4": "NRC_HDMI4-ONOFF",
    # Numeric
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
    # Color buttons
    "RED": "NRC_RED-ONOFF",
    "GREEN": "NRC_GREEN-ONOFF",
    "YELLOW": "NRC_YELLOW-ONOFF",
    "BLUE": "NRC_BLUE-ONOFF",
    # Power & Settings
    "POWER": "NRC_POWER-ONOFF",
    "OFF_TIMER": "NRC_OFFTIMER-ONOFF",
    "P_NR": "NRC_P_NR-ONOFF",
    "PICTAI": "NRC_PICTAI-ONOFF",
    # Information & Guide
    "INFO": "NRC_INFO-ONOFF",
    "GUIDE": "NRC_EPG-ONOFF",
    "EPG": "NRC_EPG-ONOFF",
    "EHELP": "NRC_GUIDE-ONOFF",
    "PROGRAM": "NRC_PROG-ONOFF",
    "FAVORITE": "NRC_FAVORITE-ONOFF",
    "LAST_VIEW": "NRC_R_TUNE-ONOFF",
    # Display & Picture
    "DISPLAY": "NRC_DISP_MODE-ONOFF",
    "ASPECT": "NRC_ASPECT-ONOFF",
    "3D": "NRC_3D-ONOFF",
    "TOGGLE_3D": "NRC_3D-ONOFF",
    "R_SCREEN": "NRC_R_SCREEN-ONOFF",
    "SPLIT": "NRC_SPLIT-ONOFF",
    "SWAP": "NRC_SWAP-ONOFF",
    # Text & Subtitles
    "TEXT": "NRC_TEXT-ONOFF",
    "STTL": "NRC_STTL-ONOFF",
    "SUBTITLES": "NRC_STTL-ONOFF",
    "CC": "NRC_CC-ONOFF",
    "HOLD": "NRC_HOLD-ONOFF",
    # Apps & Network
    "APPS": "NRC_APPS-ONOFF",
    "MY_APP": "NRC_MYAPP-ONOFF",
    "NETFLIX": "NRC_NETFLIX-ONOFF",
    "CONNECT": "NRC_INTERNET-ONOFF",
    "INTERNET": "NRC_INTERNET-ONOFF",
    "NETWORK": "NRC_CHG_NETWORK-ONOFF",
    "VTOOLS": "NRC_VTOOLS-ONOFF",
    # External Devices
    "LINK": "NRC_VIERA_LINK-ONOFF",
    "VIERA_LINK": "NRC_VIERA_LINK-ONOFF",
    "EZ_SYNC": "NRC_EZ_SYNC-ONOFF",
    "DIGA_CONTROL": "NRC_DIGA_CTL-ONOFF",
    # Game & Special
    "GAME": "NRC_GAME-ONOFF",
    "CHAT_MODE": "NRC_CHAT_MODE-ONOFF",
    "TOGGLE_SD_CARD": "NRC_SD_CARD-ONOFF",
    # Regional/Broadcast
    "NET_BS": "NRC_NET_BS-ONOFF",
    "NET_CS": "NRC_NET_CS-ONOFF",
    "NET_TD": "NRC_NET_TD-ONOFF",
}

# Prefix for dynamically discovered app commands
APP_CMD_PREFIX = "APP_"


class PanasonicVieraRemote(Remote):

    def __init__(
        self, device_config: PanasonicVieraConfig, device: PanasonicVieraDevice
    ):
        self._device = device
        self._device_config = device_config
        self._discovered_apps: list[Any] = []
        self._app_commands: dict[str, Any] = {}  # Maps APP_xxx command to app object

        entity_id = f"remote.{device_config.identifier}"
        entity_name = f"{device_config.name} Remote"

        features = [Features.SEND_CMD]
        attributes = {Attributes.STATE: "UNKNOWN"}

        super().__init__(
            entity_id,
            entity_name,
            features,
            attributes,
            cmd_handler=self.handle_command,
        )

        self._update_options()
        _LOG.info("[%s] Remote entity initialized with %d commands", self.id, len(VIERA_KEYS))

    def _get_static_pages(self) -> list[dict]:
        """Return the static UI pages for navigation, playback, channels, and inputs."""
        return [
            {
                "page_id": "navigation",
                "name": "Navigation",
                "grid": {"width": 3, "height": 4},
                "items": [
                    {"type": "text", "text": "Home", "command": {"cmd_id": "HOME"}, "location": {"x": 0, "y": 0}},
                    {"type": "icon", "icon": "uc:up-arrow", "command": {"cmd_id": "UP"}, "location": {"x": 1, "y": 0}},
                    {"type": "text", "text": "Menu", "command": {"cmd_id": "MENU"}, "location": {"x": 2, "y": 0}},
                    {"type": "icon", "icon": "uc:left-arrow", "command": {"cmd_id": "LEFT"}, "location": {"x": 0, "y": 1}},
                    {"type": "text", "text": "OK", "command": {"cmd_id": "OK"}, "location": {"x": 1, "y": 1}},
                    {"type": "icon", "icon": "uc:right-arrow", "command": {"cmd_id": "RIGHT"}, "location": {"x": 2, "y": 1}},
                    {"type": "text", "text": "Back", "command": {"cmd_id": "BACK"}, "location": {"x": 0, "y": 2}},
                    {"type": "icon", "icon": "uc:down-arrow", "command": {"cmd_id": "DOWN"}, "location": {"x": 1, "y": 2}},
                    {"type": "text", "text": "Exit", "command": {"cmd_id": "EXIT"}, "location": {"x": 2, "y": 2}},
                    {"type": "text", "text": "Info", "command": {"cmd_id": "INFO"}, "location": {"x": 0, "y": 3}},
                    {"type": "text", "text": "Guide", "command": {"cmd_id": "GUIDE"}, "location": {"x": 1, "y": 3}},
                    {"type": "text", "text": "Last View", "command": {"cmd_id": "LAST_VIEW"}, "location": {"x": 2, "y": 3}},
                ],
            },
            {
                "page_id": "playback",
                "name": "Playback",
                "grid": {"width": 3, "height": 3},
                "items": [
                    {"type": "icon", "icon": "uc:prev", "command": {"cmd_id": "SKIP_BACK"}, "location": {"x": 0, "y": 0}},
                    {"type": "icon", "icon": "uc:play", "command": {"cmd_id": "PLAY"}, "location": {"x": 1, "y": 0}},
                    {"type": "icon", "icon": "uc:next", "command": {"cmd_id": "SKIP_FWD"}, "location": {"x": 2, "y": 0}},
                    {"type": "icon", "icon": "uc:backward", "command": {"cmd_id": "REW"}, "location": {"x": 0, "y": 1}},
                    {"type": "icon", "icon": "uc:pause", "command": {"cmd_id": "PAUSE"}, "location": {"x": 1, "y": 1}},
                    {"type": "icon", "icon": "uc:forward", "command": {"cmd_id": "FF"}, "location": {"x": 2, "y": 1}},
                    {"type": "icon", "icon": "uc:rec", "command": {"cmd_id": "REC"}, "location": {"x": 0, "y": 2}},
                    {"type": "icon", "icon": "uc:stop", "command": {"cmd_id": "STOP"}, "location": {"x": 1, "y": 2}},
                ],
            },
            {
                "page_id": "channels",
                "name": "Channels",
                "grid": {"width": 3, "height": 4},
                "items": [
                    {"type": "text", "text": "1", "command": {"cmd_id": "NUM_1"}, "location": {"x": 0, "y": 0}},
                    {"type": "text", "text": "2", "command": {"cmd_id": "NUM_2"}, "location": {"x": 1, "y": 0}},
                    {"type": "text", "text": "3", "command": {"cmd_id": "NUM_3"}, "location": {"x": 2, "y": 0}},
                    {"type": "text", "text": "4", "command": {"cmd_id": "NUM_4"}, "location": {"x": 0, "y": 1}},
                    {"type": "text", "text": "5", "command": {"cmd_id": "NUM_5"}, "location": {"x": 1, "y": 1}},
                    {"type": "text", "text": "6", "command": {"cmd_id": "NUM_6"}, "location": {"x": 2, "y": 1}},
                    {"type": "text", "text": "7", "command": {"cmd_id": "NUM_7"}, "location": {"x": 0, "y": 2}},
                    {"type": "text", "text": "8", "command": {"cmd_id": "NUM_8"}, "location": {"x": 1, "y": 2}},
                    {"type": "text", "text": "9", "command": {"cmd_id": "NUM_9"}, "location": {"x": 2, "y": 2}},
                    {"type": "icon", "icon": "uc:down-arrow", "command": {"cmd_id": "CH_DOWN"}, "location": {"x": 0, "y": 3}},
                    {"type": "text", "text": "0", "command": {"cmd_id": "NUM_0"}, "location": {"x": 1, "y": 3}},
                    {"type": "icon", "icon": "uc:up-arrow", "command": {"cmd_id": "CH_UP"}, "location": {"x": 2, "y": 3}},
                ],
            },
            {
                "page_id": "color_input",
                "name": "Color & Input",
                "grid": {"width": 4, "height": 5},
                "items": [
                    {"type": "text", "text": "Power", "command": {"cmd_id": "POWER"}, "location": {"x": 0, "y": 0}},
                    {"type": "text", "text": "Option", "command": {"cmd_id": "OPTION"}, "location": {"x": 2, "y": 0}},
                    {"type": "text", "text": "eHelp", "command": {"cmd_id": "EHELP"}, "location": {"x": 3, "y": 0}},
                    {"type": "text", "text": "Apps", "command": {"cmd_id": "APPS"}, "location": {"x": 0, "y": 1}},
                    {"type": "text", "text": "My App", "command": {"cmd_id": "MY_APP"}, "location": {"x": 1, "y": 1}},
                    {"type": "text", "text": "Netflix", "command": {"cmd_id": "NETFLIX"}, "location": {"x": 2, "y": 1}},
                    {"type": "text", "text": "TV", "command": {"cmd_id": "TV"}, "location": {"x": 0, "y": 2}},
                    {"type": "text", "text": "AV", "command": {"cmd_id": "AV"}, "location": {"x": 1, "y": 2}},
                    {"type": "text", "text": "HDMI1", "command": {"cmd_id": "HDMI1"}, "location": {"x": 0, "y": 3}},
                    {"type": "text", "text": "HDMI2", "command": {"cmd_id": "HDMI2"}, "location": {"x": 1, "y": 3}},
                    {"type": "text", "text": "HDMI3", "command": {"cmd_id": "HDMI3"}, "location": {"x": 2, "y": 3}},
                    {"type": "text", "text": "HDMI4", "command": {"cmd_id": "HDMI4"}, "location": {"x": 3, "y": 3}},
                    {"type": "text", "text": "Red", "command": {"cmd_id": "RED"}, "location": {"x": 0, "y": 4}},
                    {"type": "text", "text": "Green", "command": {"cmd_id": "GREEN"}, "location": {"x": 1, "y": 4}},
                    {"type": "text", "text": "Yellow", "command": {"cmd_id": "YELLOW"}, "location": {"x": 2, "y": 4}},
                    {"type": "text", "text": "Blue", "command": {"cmd_id": "BLUE"}, "location": {"x": 3, "y": 4}},
                ],
            },
        ]

    def _generate_apps_page(self) -> dict | None:
        """Generate a dynamic Apps page from discovered apps."""
        if not self._discovered_apps:
            return None

        # Max grid is 8x12, we'll use 4 columns
        grid_width = 4
        max_apps = 48  # 4 columns x 12 rows
        apps_to_show = self._discovered_apps[:max_apps]

        items = []
        for i, app in enumerate(apps_to_show):
            x = i % grid_width
            y = i // grid_width
            # Create command ID from app name (sanitized)
            cmd_id = self._get_app_command_id(app)
            # Handle both app objects with .name attribute and string app names
            app_name = app.name if hasattr(app, 'name') else str(app)
            # Truncate app name for display (max ~10 chars to fit in button)
            display_name = app_name[:10] if len(app_name) > 10 else app_name
            items.append({
                "type": "text",
                "text": display_name,
                "command": {"cmd_id": cmd_id},
                "location": {"x": x, "y": y},
            })

        grid_height = min(12, (len(apps_to_show) + grid_width - 1) // grid_width)

        return {
            "page_id": "apps",
            "name": "Apps",
            "grid": {"width": grid_width, "height": grid_height},
            "items": items,
        }

    def _get_app_command_id(self, app: Any) -> str:
        """Generate a safe command ID for an app."""
        # Handle both app objects with .name attribute and string app names
        app_name = app.name if hasattr(app, 'name') else str(app)
        # Sanitize app name: remove spaces/special chars, uppercase, limit to 15 chars
        safe_name = "".join(c for c in app_name if c.isalnum()).upper()[:15]
        return f"{APP_CMD_PREFIX}{safe_name}"

    def _update_options(self) -> None:
        """Update the remote options with current commands and UI."""
        # Build simple commands list: all VIERA_KEYS + discovered app commands
        simple_commands = list(VIERA_KEYS.keys())

        # Add discovered app commands
        self._app_commands.clear()
        for app in self._discovered_apps:
            cmd_id = self._get_app_command_id(app)
            self._app_commands[cmd_id] = app
            if cmd_id not in simple_commands:
                simple_commands.append(cmd_id)

        # Build UI pages
        pages = self._get_static_pages()

        # Add dynamic apps page if we have discovered apps
        apps_page = self._generate_apps_page()
        if apps_page:
            pages.append(apps_page)

        user_interface = {"pages": pages}

        self.options = {
            Options.SIMPLE_COMMANDS: simple_commands,
            "user_interface": user_interface,
        }

    async def update_discovered_apps(self, apps: list[Any]) -> None:
        """Update the remote with newly discovered apps from the TV."""
        if apps == self._discovered_apps:
            return

        self._discovered_apps = apps
        self._update_options()
        _LOG.info(
            "[%s] Updated remote with %d discovered apps: %s",
            self.id,
            len(apps),
            [app.name if hasattr(app, 'name') else str(app) for app in apps[:10]],  # Log first 10
        )

    async def handle_command(
        self, entity: Remote, cmd_id: str, params: dict[str, Any] | None
    ) -> StatusCodes:
        _LOG.info("[%s] Command: %s %s", self.id, cmd_id, params or "")

        try:
            if cmd_id == Commands.SEND_CMD:
                if params and "command" in params:
                    key_name = params["command"]
                    return await self._execute_command(key_name)
                return StatusCodes.BAD_REQUEST

            return await self._execute_command(cmd_id)

        except Exception as err:
            _LOG.error("[%s] Command error: %s", self.id, err)
            return StatusCodes.SERVER_ERROR

    async def _execute_command(self, cmd_id: str) -> StatusCodes:
        """Execute a command by ID (either a key or an app)."""
        # Check if it's a standard Viera key command
        if cmd_id in VIERA_KEYS:
            key_code = VIERA_KEYS[cmd_id]
            success = await self._device.send_key(key_code)
            return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

        # Check if it's a discovered app command
        if cmd_id.startswith(APP_CMD_PREFIX) and cmd_id in self._app_commands:
            app = self._app_commands[cmd_id]
            app_name = app.name if hasattr(app, 'name') else str(app)
            _LOG.info("[%s] Launching app: %s", self.id, app_name)
            success = await self._device.launch_app(app)
            return StatusCodes.OK if success else StatusCodes.SERVER_ERROR

        _LOG.warning("[%s] Unknown command: %s", self.id, cmd_id)
        return StatusCodes.NOT_IMPLEMENTED
