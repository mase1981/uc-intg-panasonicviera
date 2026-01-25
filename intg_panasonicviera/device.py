"""
Panasonic Viera TV device implementation for Unfolded Circle integration.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import logging
import socket
from typing import Any
from panasonic_viera import RemoteControl
from ucapi_framework import PollingDevice, DeviceEvents
from ucapi.media_player import Attributes as MediaAttributes
from ucapi.remote import Attributes as RemoteAttributes
from intg_panasonicviera.config import PanasonicVieraConfig

_LOG = logging.getLogger(__name__)


class PanasonicVieraDevice(PollingDevice):

    def __init__(self, device_config: PanasonicVieraConfig, **kwargs):
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
        return self._device_config.identifier

    @property
    def name(self) -> str:
        return self._device_config.name

    @property
    def address(self) -> str:
        return self._device_config.host

    @property
    def log_id(self) -> str:
        return f"{self.name} ({self.address})"

    @property
    def power(self) -> bool:
        return self._power_state

    @property
    def volume(self) -> int:
        return self._volume

    @property
    def muted(self) -> bool:
        return self._muted

    @property
    def current_source(self) -> str:
        return self._current_source

    @property
    def source_list(self) -> list[str]:
        return self._source_list

    async def _create_remote_control(self) -> RemoteControl:
        if self._device_config.app_id and self._device_config.encryption_key:
            _LOG.debug("[%s] Creating encrypted RemoteControl", self.log_id)
            return await asyncio.to_thread(
                RemoteControl,
                self._device_config.host,
                self._device_config.port,
                self._device_config.app_id,
                self._device_config.encryption_key,
            )
        else:
            _LOG.debug("[%s] Creating non-encrypted RemoteControl", self.log_id)
            return await asyncio.to_thread(
                RemoteControl,
                self._device_config.host,
                self._device_config.port,
            )

    async def establish_connection(self) -> Any:
        _LOG.debug("[%s] Establishing connection", self.log_id)
        try:
            self._remote = await self._create_remote_control()

            volume = await asyncio.to_thread(self._remote.get_volume)
            if volume is not None:
                self._volume = volume
                self._power_state = True
                _LOG.info("[%s] Connection established, TV is ON (volume: %d)", self.log_id, volume)
            else:
                self._power_state = False
                _LOG.info("[%s] Connection established, TV is OFF", self.log_id)

            self._emit_update()
            return self._remote

        except Exception as err:
            _LOG.error("[%s] Connection failed: %s", self.log_id, err)
            self._power_state = False
            self._emit_update()
            raise

    async def poll_device(self) -> None:
        if not self._remote:
            _LOG.debug("[%s] No remote connection, skipping poll", self.log_id)
            return

        try:
            remote = await self._create_remote_control()

            volume = await asyncio.to_thread(remote.get_volume)

            if volume is not None:
                self._volume = volume

                mute = await asyncio.to_thread(remote.get_mute)
                if mute is not None:
                    self._muted = mute

                if not self._power_state:
                    _LOG.info("[%s] TV is now ON", self.log_id)
                    await self.get_sources()

                self._power_state = True
            else:
                if self._power_state:
                    _LOG.info("[%s] TV is now OFF", self.log_id)
                self._power_state = False

            self._emit_update()

        except Exception as err:
            error_str = str(err).lower()

            if "encryption" in error_str or "refer to the docs" in error_str:
                _LOG.error(
                    "[%s] TV requires encryption but credentials not configured.",
                    self.log_id
                )
            else:
                _LOG.debug("[%s] Poll error (TV likely off): %s", self.log_id, err)

            if self._power_state:
                _LOG.info("[%s] TV is now OFF or unreachable", self.log_id)
                self._power_state = False
                self._emit_update()

    def _emit_update(self) -> None:
        media_player_id = f"media_player.{self.identifier}"
        state_value = "ON" if self._power_state else "OFF"

        media_player_attrs = {
            MediaAttributes.STATE: state_value,
            MediaAttributes.VOLUME: self._volume,
            MediaAttributes.MUTED: self._muted,
            MediaAttributes.SOURCE: self._current_source,
            MediaAttributes.SOURCE_LIST: self._source_list,
        }

        _LOG.debug("[%s] Emitting update: %s", self.log_id, state_value)
        self.events.emit(DeviceEvents.UPDATE, media_player_id, media_player_attrs)

        remote_id = f"remote.{self.identifier}"
        remote_attrs = {
            RemoteAttributes.STATE: state_value,
        }
        self.events.emit(DeviceEvents.UPDATE, remote_id, remote_attrs)

    def _send_wol_packet(self, mac_address: str) -> bool:
        """Send Wake-on-LAN magic packet to TV on multiple ports."""
        try:
            # Parse MAC address (supports formats: AA:BB:CC:DD:EE:FF, AA-BB-CC-DD-EE-FF, AABBCCDDEEFF)
            mac = mac_address.replace(":", "").replace("-", "").upper()
            if len(mac) != 12:
                _LOG.error("[%s] Invalid MAC address format: %s", self.log_id, mac_address)
                return False

            # Convert MAC to bytes
            mac_bytes = bytes.fromhex(mac)

            # Create magic packet (6 bytes of FF followed by MAC repeated 16 times)
            magic_packet = b"\xFF" * 6 + mac_bytes * 16

            # Send to multiple common WoL ports for better compatibility
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            # Port 9 (most common)
            sock.sendto(magic_packet, ("<broadcast>", 9))
            # Port 7 (also common)
            sock.sendto(magic_packet, ("<broadcast>", 7))
            # Direct to TV IP on port 9 (in case broadcast is blocked)
            sock.sendto(magic_packet, (self._device_config.host, 9))

            sock.close()

            _LOG.info("[%s] Sent WoL magic packets to %s (broadcast ports 7&9, direct to %s:9)",
                     self.log_id, mac_address, self._device_config.host)
            return True

        except Exception as err:
            _LOG.error("[%s] Failed to send WoL packet: %s", self.log_id, err)
            return False

    async def turn_on(self) -> bool:
        _LOG.info("[%s] Turning on", self.log_id)
        try:
            # If MAC address is configured, use Wake-on-LAN
            if self._device_config.mac_address:
                _LOG.info("[%s] Using Wake-on-LAN with MAC: %s", self.log_id, self._device_config.mac_address)
                await asyncio.to_thread(self._send_wol_packet, self._device_config.mac_address)
                # Give TV time to wake up (WoL takes 5-10 seconds typically)
                await asyncio.sleep(8)
            else:
                # Fallback to remote.turn_on (less reliable for fully powered off TVs)
                _LOG.info("[%s] No MAC address configured, using remote.turn_on", self.log_id)
                remote = await self._create_remote_control()
                await asyncio.to_thread(remote.turn_on)
                await asyncio.sleep(2)

            self._power_state = True
            self._emit_update()
            return True
        except Exception as err:
            _LOG.error("[%s] Turn on failed: %s", self.log_id, err)
            return False

    async def turn_off(self) -> bool:
        _LOG.info("[%s] Turning off", self.log_id)
        try:
            remote = await self._create_remote_control()
            await asyncio.to_thread(remote.turn_off)
            self._power_state = False
            self._emit_update()
            return True
        except Exception as err:
            _LOG.error("[%s] Turn off failed: %s", self.log_id, err)
            return False

    async def set_volume(self, volume: int) -> bool:
        _LOG.info("[%s] Setting volume to %d", self.log_id, volume)
        try:
            remote = await self._create_remote_control()
            await asyncio.to_thread(remote.set_volume, volume)
            self._volume = volume
            self._emit_update()
            return True
        except Exception as err:
            _LOG.error("[%s] Set volume failed: %s", self.log_id, err)
            return False

    async def volume_up(self) -> bool:
        _LOG.info("[%s] Volume up", self.log_id)
        try:
            remote = await self._create_remote_control()
            await asyncio.to_thread(remote.send_key, "NRC_VOLUP-ONOFF")
            self._volume = min(100, self._volume + 2)
            self._emit_update()
            return True
        except Exception as err:
            _LOG.error("[%s] Volume up failed: %s", self.log_id, err)
            return False

    async def volume_down(self) -> bool:
        _LOG.info("[%s] Volume down", self.log_id)
        try:
            remote = await self._create_remote_control()
            await asyncio.to_thread(remote.send_key, "NRC_VOLDOWN-ONOFF")
            self._volume = max(0, self._volume - 2)
            self._emit_update()
            return True
        except Exception as err:
            _LOG.error("[%s] Volume down failed: %s", self.log_id, err)
            return False

    async def mute(self, muted: bool) -> bool:
        _LOG.info("[%s] Setting mute to %s", self.log_id, muted)
        try:
            remote = await self._create_remote_control()
            await asyncio.to_thread(remote.set_mute, muted)
            self._muted = muted
            self._emit_update()
            return True
        except Exception as err:
            _LOG.error("[%s] Set mute failed: %s", self.log_id, err)
            return False

    async def send_key(self, key: str) -> bool:
        _LOG.info("[%s] Sending key: %s", self.log_id, key)
        try:
            remote = await self._create_remote_control()
            await asyncio.to_thread(remote.send_key, key)
            return True
        except Exception as err:
            _LOG.error("[%s] Send key failed: %s", self.log_id, err)
            return False

    async def play_media(self, media_url: str) -> bool:
        _LOG.info("[%s] Playing media: %s", self.log_id, media_url)
        try:
            remote = await self._create_remote_control()
            await asyncio.to_thread(remote.open_webpage, media_url)
            return True
        except Exception as err:
            _LOG.error("[%s] Play media failed: %s", self.log_id, err)
            return False

    async def get_sources(self) -> list[str]:
        if not self._power_state:
            return []

        try:
            remote = await self._create_remote_control()
            apps = await asyncio.to_thread(remote.get_apps)
            if apps:
                self._source_list = [app.name if hasattr(app, 'name') else str(app) for app in apps]
                _LOG.debug("[%s] Found %d sources", self.log_id, len(self._source_list))
                self._emit_update()
            return self._source_list
        except Exception as err:
            _LOG.debug("[%s] Get sources failed: %s", self.log_id, err)
            return []

    async def select_source(self, source: str) -> bool:
        _LOG.info("[%s] Selecting source: %s", self.log_id, source)
        try:
            remote = await self._create_remote_control()
            apps = await asyncio.to_thread(remote.get_apps)
            if not apps:
                _LOG.warning("[%s] No apps available", self.log_id)
                return False

            for app in apps:
                app_name = app.name if hasattr(app, 'name') else str(app)
                if app_name == source:
                    await asyncio.to_thread(remote.launch_app, app)
                    self._current_source = source
                    self._emit_update()
                    _LOG.info("[%s] Launched app: %s", self.log_id, source)
                    return True

            _LOG.warning("[%s] Source not found: %s", self.log_id, source)
            return False

        except Exception as err:
            _LOG.error("[%s] Select source failed: %s", self.log_id, err)
            return False

    async def launch_app(self, app: Any) -> bool:
        """Launch a specific app on the TV."""
        app_name = app.name if hasattr(app, 'name') else str(app)
        _LOG.info("[%s] Launching app: %s", self.log_id, app_name)
        try:
            remote = await self._create_remote_control()
            await asyncio.to_thread(remote.launch_app, app)
            self._current_source = app_name
            self._emit_update()
            return True
        except Exception as err:
            _LOG.error("[%s] Launch app failed: %s", self.log_id, err)
            return False

    async def get_apps_list(self) -> list[Any]:
        """Get the raw list of app objects from the TV."""
        if not self._power_state:
            return []

        try:
            remote = await self._create_remote_control()
            apps = await asyncio.to_thread(remote.get_apps)
            return apps if apps else []
        except Exception as err:
            _LOG.debug("[%s] Get apps list failed: %s", self.log_id, err)
            return []
