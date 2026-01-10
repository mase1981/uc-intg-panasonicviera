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
from .config import PanasonicVieraConfig

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

    async def poll_device(self) -> None:
        """Poll device state."""
        if not self._remote:
            _LOG.warning("[%s] No remote connection available", self.log_id)
            return

        try:
            # Get volume
            volume = await asyncio.to_thread(self._remote.get_volume)
            if volume is not None:
                self._volume = volume
                _LOG.debug("[%s] Volume: %s", self.log_id, volume)

            # Get mute state
            mute = await asyncio.to_thread(self._remote.get_mute)
            if mute is not None:
                self._muted = mute
                _LOG.debug("[%s] Muted: %s", self.log_id, mute)

            # Check if TV is on by attempting to get volume
            # If we can get volume, TV is on
            self._power_state = volume is not None

            # Emit update event
            self._emit_update()

        except Exception as err:
            _LOG.debug("[%s] Poll error (TV may be off): %s", self.log_id, err)
            # TV is likely off if we can't poll
            if self._power_state:
                self._power_state = False
                self._emit_update()

    def _emit_update(self) -> None:
        """Emit device update event."""
        entity_id = f"media_player.{self.identifier}"
        attributes = {
            "state": "ON" if self._power_state else "OFF",
            "volume": self._volume,
            "muted": self._muted,
        }
        _LOG.debug("[%s] Emitting update: %s", self.log_id, attributes)
        self.events.emit(DeviceEvents.UPDATE, entity_id, attributes)

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
        if not self._remote:
            _LOG.error("[%s] No remote connection", self.log_id)
            return False

        try:
            await asyncio.to_thread(self._remote.turn_off)
            self._power_state = False
            self._emit_update()
            return True
        except Exception as err:
            _LOG.error("[%s] Turn off failed: %s", self.log_id, err)
            return False

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
        if not self._remote:
            _LOG.error("[%s] No remote connection", self.log_id)
            return False

        try:
            await asyncio.to_thread(self._remote.send_key, key)
            return True
        except Exception as err:
            _LOG.error("[%s] Send key failed: %s", self.log_id, err)
            return False

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
