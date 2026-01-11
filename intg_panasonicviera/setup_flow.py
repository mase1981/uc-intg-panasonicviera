"""
Panasonic Viera TV setup flow for Unfolded Circle integration.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import logging
from typing import Any
from panasonic_viera import RemoteControl
from ucapi import RequestUserInput, IntegrationSetupError, SetupError
from ucapi_framework import BaseSetupFlow
from intg_panasonicviera.config import PanasonicVieraConfig

_LOG = logging.getLogger(__name__)


class PanasonicVieraSetupFlow(BaseSetupFlow[PanasonicVieraConfig]):
    """Setup flow for Panasonic Viera TV integration with PIN pairing support."""

    def __init__(self, driver, **kwargs):
        """Initialize setup flow."""
        super().__init__(driver, **kwargs)
        self._remote_instance: RemoteControl | None = None

    def get_manual_entry_form(self) -> RequestUserInput:
        """Define manual entry fields."""
        return RequestUserInput(
            {"en": "Panasonic Viera TV Setup"},
            [
                {
                    "id": "name",
                    "label": {"en": "TV Name"},
                    "field": {"text": {"value": ""}},
                },
                {
                    "id": "host",
                    "label": {"en": "IP Address"},
                    "field": {"text": {"value": ""}},
                },
                {
                    "id": "port",
                    "label": {"en": "Port"},
                    "field": {"text": {"value": "55000"}},
                },
            ],
        )

    async def query_device(
        self, input_values: dict[str, Any]
    ) -> PanasonicVieraConfig | RequestUserInput:
        """
        Validate connection and create config.
        Handles PIN pairing for encrypted TVs.
        """
        host = input_values.get("host", "").strip()
        if not host:
            raise ValueError("IP address is required")

        port = int(input_values.get("port", 55000))
        name = input_values.get("name", f"Panasonic Viera ({host})").strip()
        pin = input_values.get("pin", "").strip()

        _LOG.info("Setting up Panasonic Viera TV at %s:%s", host, port)

        try:
            # Reuse RemoteControl instance if available (for PIN flow)
            # This is critical - authorize_pin_code needs the same instance that called request_pin_code
            if self._remote_instance is None:
                self._remote_instance = await asyncio.to_thread(RemoteControl, host, port)

            remote = self._remote_instance

            # Check if TV requires encryption (has app_id and enc_key)
            app_id = None
            encryption_key = None

            # Try to send a key to check if encryption is needed
            # Note: get_volume uses SOAP API which may not require encryption,
            # but send_key uses command API which DOES require encryption on 2018+ models
            try:
                # Test with a harmless INFO key - won't change TV state
                await asyncio.to_thread(remote.send_key, "NRC_INFO-ONOFF")
                _LOG.info("TV does not require encryption - send_key works")

            except Exception as test_err:
                # TV requires encryption - need PIN pairing
                _LOG.info("TV requires encryption - initiating PIN pairing")

                # If we don't have a PIN yet, request it
                if not pin:
                    # Request PIN from TV
                    try:
                        await asyncio.to_thread(remote.request_pin_code)
                        _LOG.info("PIN request sent to TV - displaying on screen")

                        # Return form to collect PIN
                        return RequestUserInput(
                            {"en": "Enter PIN from TV"},
                            [
                                {
                                    "id": "host",
                                    "label": {"en": "IP Address"},
                                    "field": {"text": {"value": host}},
                                },
                                {
                                    "id": "port",
                                    "label": {"en": "Port"},
                                    "field": {"text": {"value": str(port)}},
                                },
                                {
                                    "id": "name",
                                    "label": {"en": "TV Name"},
                                    "field": {"text": {"value": name}},
                                },
                                {
                                    "id": "pin",
                                    "label": {
                                        "en": "PIN Code (displayed on TV screen)"
                                    },
                                    "field": {"text": {"value": ""}},
                                },
                            ],
                        )

                    except Exception as pin_err:
                        raise ValueError(
                            f"Failed to request PIN from TV: {pin_err}"
                        ) from pin_err

                # We have a PIN - authorize and get credentials
                try:
                    _LOG.info("Authorizing with PIN: %s", pin)
                    await asyncio.to_thread(remote.authorize_pin_code, pincode=pin)

                    # Get app_id and encryption_key
                    app_id = remote.app_id
                    encryption_key = remote.enc_key

                    if not app_id or not encryption_key:
                        raise ValueError(
                            "Failed to obtain app_id and encryption_key after PIN authorization"
                        )

                    _LOG.info("Successfully paired with encrypted TV")

                except Exception as auth_err:
                    raise ValueError(
                        f"PIN authorization failed: {auth_err}. "
                        "Please verify the PIN is correct and try again."
                    ) from auth_err

            # Create identifier
            identifier = f"viera_{host.replace('.', '_')}_{port}"

            # Test connection with credentials (if encrypted)
            if app_id and encryption_key:
                test_remote = await asyncio.to_thread(RemoteControl, host, port)
                test_remote.app_id = app_id
                test_remote.enc_key = encryption_key

                # Verify credentials work
                try:
                    await asyncio.to_thread(test_remote.get_volume)
                    _LOG.info("Verified encrypted connection works")
                except Exception as test_err:
                    raise ValueError(
                        f"Failed to verify encrypted connection: {test_err}"
                    ) from test_err

            # Create and return config
            config = PanasonicVieraConfig(
                identifier=identifier,
                name=name,
                host=host,
                port=port,
                app_id=app_id,
                encryption_key=encryption_key,
            )

            _LOG.info("Setup completed successfully for %s", name)

            # Clear the instance for next setup
            self._remote_instance = None

            return config

        except asyncio.TimeoutError:
            self._remote_instance = None
            raise ValueError(
                f"Connection timeout to {host}:{port}\n"
                "Please verify TV is powered on and accessible"
            ) from None

        except ValueError:
            # Re-raise ValueError as-is (already has good error message)
            self._remote_instance = None
            raise

        except Exception as err:
            self._remote_instance = None
            raise ValueError(f"Setup failed: {err}") from err
