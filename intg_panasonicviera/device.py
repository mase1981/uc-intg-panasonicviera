"""
Panasonic Viera TV device implementation for Unfolded Circle integration.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import logging
from typing import Any
from panasonic_viera import RemoteControl
from ucapi_framework import PollingDevice, DeviceEvents
from intg_panasonicviera.config import PanasonicVieraConfig

_LOG = logging.getLogger(__name__)


class PanasonicVieraDevice(PollingDevice):
    """Panasonic Viera TV device implementation using PollingDevice."""

    def __init__(self, device_config: PanasonicVieraConfig, **kwargs):
        """Initialize the device."""
        super().__init__(device_config, poll_interval=30, **kwargs)
        self._device_config = device_config
        self._remote: RemoteControl | None = None
        self._power_state: bool = False
        self._volume: int = 0
        self._muted: bool = False
        self._current_source: str = ""
        self._source_list: list[str] = []

    @property
    def identifier(self) -> str:
        """Return device identifier."""
        return self._device_config.identifier

    @property
    def name(self) -> str:
        """Return device name."""
        return self._device_config.name

    @property
    def address(self) -> str:
        """Return device address."""
        return self._device_config.host

    @property
    def log_id(self) -> str:
        """Return log identifier."""
        return f"{self.name} ({self.address})"

    @property
    def power(self) -> bool:
        """Return power state."""
        return self._power_state

    @property
    def volume(self) -> int:
        """Return volume level (0-100)."""
        return self._volume

    @property
    def muted(self) -> bool:
        """Return mute state."""
        return self._muted

    @property
    def current_source(self) -> str:
        """Return current input source."""
        return self._current_source

    @property
    def source_list(self) -> list[str]:
        """Return list of available input sources."""
        return self._source_list

    async def establish_connection(self) -> Any:
        """Establish connection to TV."""
        _LOG.debug("[%s] Establishing connection", self.log_id)
        try:
            # Create RemoteControl instance
            self._remote = await asyncio.to_thread(
                RemoteControl,
                self._device_config.host,
                self._device_config.port,
            )

            # If encrypted TV, set app_id and encryption_key
            if self._device_config.app_id and self._device_config.encryption_key:
                _LOG.debug("[%s] Using encrypted connection", self.log_id)
                self._remote.app_id = self._device_config.app_id
                self._remote.enc_key = self._device_config.encryption_key

            return self._remote

        except Exception as err:
            _LOG.error("[%s] Connection failed: %s", self.log_id, err)
            raise

    async def _handle_command_errors(self, func, *args) -> tuple[bool, str | None]:
        """
        Execute command with proper error handling.
        Returns (success, error_message).
        """
        if not self._remote:
            return False, "No remote connection"

        try:
            result = await asyncio.to_thread(func, *args)
            return True, None
        except Exception as err:
            error_msg = str(err)

            # Encryption required
            if "encryption" in error_msg.lower() or "refer to the docs" in error_msg.lower():
                _LOG.error(
                    "[%s] TV requires encryption. Please reconfigure integration with PIN pairing. Error: %s",
                    self.log_id, err
                )
                return False, "TV requires encryption - please reconfigure with PIN pairing"

            # TV is off or unreachable
            if "connection" in error_msg.lower() or "timeout" in error_msg.lower() or "refused" in error_msg.lower():
                _LOG.debug("[%s] TV appears to be off or unreachable: %s", self.log_id, err)
                self._power_state = False
                self._emit_update()
                return False, "TV is off or unreachable"

            # Generic error
            _LOG.error("[%s] Command failed: %s", self.log_id, err)
            return False, str(err)

    async def poll_device(self) -> None:
        """Poll device state."""
        if not self._remote:
            _LOG.warning("[%s] No remote connection available", self.log_id)
            return

        try:
            # Get volume (this also tests if TV is on)
            volume = await asyncio.to_thread(self._remote.get_volume)

            if volume is not None:
                self._volume = volume
                _LOG.debug("[%s] Volume: %s", self.log_id, volume)

                # Get mute state
                mute = await asyncio.to_thread(self._remote.get_mute)
                if mute is not None:
                    self._muted = mute
                    _LOG.debug("[%s] Muted: %s", self.log_id, mute)

                # TV is on and responding
                if not self._power_state:
                    _LOG.info("[%s] TV is now ON", self.log_id)
                    # Fetch available sources when TV comes online
                    await self.get_sources()

                self._power_state = True
                self._emit_update()
            else:
                # TV returned None - likely off
                if self._power_state:
                    _LOG.info("[%s] TV is now OFF", self.log_id)
                self._power_state = False
                self._emit_update()

        except Exception as err:
            error_str = str(err).lower()

            # Check if error indicates encryption requirement
            if "encryption" in error_str or "refer to the docs" in error_str:
                _LOG.error(
                    "[%s] TV requires encryption but credentials not configured. "
                    "Please reconfigure integration with PIN pairing.",
                    self.log_id
                )
                # Keep polling but mark as off since commands won't work
                if self._power_state:
                    _LOG.info("[%s] Marking as OFF due to encryption error", self.log_id)
                    self._power_state = False
                    self._emit_update()
                return

            # TV is off or unreachable - normal condition
            _LOG.debug("[%s] Poll error (TV likely off or unreachable): %s", self.log_id, err)
            if self._power_state:
                _LOG.info("[%s] TV is now OFF or unreachable", self.log_id)
                self._power_state = False
                self._emit_update()

    def _emit_update(self) -> None:
        """Emit device update event for both media_player and remote entities."""
        # Update media player entity
        media_player_id = f"media_player.{self.identifier}"
        media_player_attrs = {
            "state": "ON" if self._power_state else "OFF",
            "volume": self._volume,
            "muted": self._muted,
            "source": self._current_source,
            "source_list": self._source_list,
        }
        _LOG.debug("[%s] Emitting media_player update: %s", self.log_id, media_player_attrs)
        self.events.emit(DeviceEvents.UPDATE, media_player_id, media_player_attrs)

        # Update remote entity with same power state
        remote_id = f"remote.{self.identifier}"
        remote_attrs = {
            "state": "ON" if self._power_state else "OFF",
        }
        _LOG.debug("[%s] Emitting remote update: %s", self.log_id, remote_attrs)
        self.events.emit(DeviceEvents.UPDATE, remote_id, remote_attrs)

    async def turn_on(self) -> bool:
        """Turn TV on."""
        _LOG.info("[%s] Turning on", self.log_id)
        if not self._remote:
            _LOG.error("[%s] No remote connection", self.log_id)
            return False

        try:
            await asyncio.to_thread(self._remote.turn_on)
            self._power_state = True
            self._emit_update()
            # Give TV time to boot
            await asyncio.sleep(2)
            return True
        except Exception as err:
            _LOG.error("[%s] Turn on failed: %s", self.log_id, err)
            return False

    async def turn_off(self) -> bool:
        """Turn TV off."""
        _LOG.info("[%s] Turning off", self.log_id)

        success, error = await self._handle_command_errors(self._remote.turn_off)

        if success:
            self._power_state = False
            self._emit_update()
        elif error:
            _LOG.error("[%s] Turn off failed: %s", self.log_id, error)

        return success

    async def set_volume(self, volume: int) -> bool:
        """Set volume level (0-100)."""
        _LOG.info("[%s] Setting volume to %s", self.log_id, volume)
        if not self._remote:
            _LOG.error("[%s] No remote connection", self.log_id)
            return False

        try:
            await asyncio.to_thread(self._remote.set_volume, volume)
            self._volume = volume
            self._emit_update()
            return True
        except Exception as err:
            _LOG.error("[%s] Set volume failed: %s", self.log_id, err)
            return False

    async def volume_up(self) -> bool:
        """Increase volume."""
        _LOG.info("[%s] Volume up", self.log_id)
        if not self._remote:
            _LOG.error("[%s] No remote connection", self.log_id)
            return False

        try:
            await asyncio.to_thread(self._remote.send_key, "NRC_VOLUP-ONOFF")
            # Estimate new volume
            self._volume = min(100, self._volume + 2)
            self._emit_update()
            return True
        except Exception as err:
            _LOG.error("[%s] Volume up failed: %s", self.log_id, err)
            return False

    async def volume_down(self) -> bool:
        """Decrease volume."""
        _LOG.info("[%s] Volume down", self.log_id)
        if not self._remote:
            _LOG.error("[%s] No remote connection", self.log_id)
            return False

        try:
            await asyncio.to_thread(self._remote.send_key, "NRC_VOLDOWN-ONOFF")
            # Estimate new volume
            self._volume = max(0, self._volume - 2)
            self._emit_update()
            return True
        except Exception as err:
            _LOG.error("[%s] Volume down failed: %s", self.log_id, err)
            return False

    async def mute(self, muted: bool) -> bool:
        """Set mute state."""
        _LOG.info("[%s] Setting mute to %s", self.log_id, muted)
        if not self._remote:
            _LOG.error("[%s] No remote connection", self.log_id)
            return False

        try:
            await asyncio.to_thread(self._remote.set_mute, muted)
            self._muted = muted
            self._emit_update()
            return True
        except Exception as err:
            _LOG.error("[%s] Set mute failed: %s", self.log_id, err)
            return False

    async def send_key(self, key: str) -> bool:
        """Send remote control key."""
        _LOG.info("[%s] Sending key: %s", self.log_id, key)

        success, error = await self._handle_command_errors(self._remote.send_key, key)

        if not success and error:
            _LOG.error("[%s] Send key failed: %s", self.log_id, error)

        return success

    async def play_media(self, media_url: str) -> bool:
        """Play media URL in TV browser."""
        _LOG.info("[%s] Playing media: %s", self.log_id, media_url)
        if not self._remote:
            _LOG.error("[%s] No remote connection", self.log_id)
            return False

        try:
            await asyncio.to_thread(self._remote.open_webpage, media_url)
            return True
        except Exception as err:
            _LOG.error("[%s] Play media failed: %s", self.log_id, err)
            return False

    async def get_sources(self) -> list[str]:
        """Get available input sources (apps)."""
        if not self._remote:
            return []

        try:
            apps = await asyncio.to_thread(self._remote.get_apps)
            if apps:
                self._source_list = [app.name for app in apps]
                _LOG.debug("[%s] Found %d sources", self.log_id, len(self._source_list))
            return self._source_list
        except Exception as err:
            _LOG.debug("[%s] Get sources failed: %s", self.log_id, err)
            return []

    async def select_source(self, source: str) -> bool:
        """Select input source by launching app."""
        _LOG.info("[%s] Selecting source: %s", self.log_id, source)
        if not self._remote:
            _LOG.error("[%s] No remote connection", self.log_id)
            return False

        try:
            # Get available apps
            apps = await asyncio.to_thread(self._remote.get_apps)
            if not apps:
                _LOG.warning("[%s] No apps available", self.log_id)
                return False

            # Find matching app by name
            for app in apps:
                if app.name == source:
                    await asyncio.to_thread(self._remote.launch_app, app)
                    self._current_source = source
                    self._emit_update()
                    _LOG.info("[%s] Launched app: %s", self.log_id, source)
                    return True

            _LOG.warning("[%s] Source not found: %s", self.log_id, source)
            return False

        except Exception as err:
            _LOG.error("[%s] Select source failed: %s", self.log_id, err)
            return False
