"""
Panasonic Viera TV integration for Unfolded Circle Remote.

:copyright: (c) 2026 by Meir Miyara.
:license: MPL-2.0, see LICENSE for more details.
"""

import asyncio
import json
import logging
import os
from pathlib import Path
from ucapi import DeviceStates
from ucapi_framework import get_config_path, BaseConfigManager
from intg_panasonicviera.driver import PanasonicVieraDriver
from intg_panasonicviera.setup_flow import PanasonicVieraSetupFlow
from intg_panasonicviera.config import PanasonicVieraConfig

try:
    driver_path = Path(__file__).parent.parent / "driver.json"
    with open(driver_path, "r", encoding="utf-8") as f:
        driver_info = json.load(f)
        __version__ = driver_info.get("version", "0.0.0")
except (FileNotFoundError, json.JSONDecodeError, KeyError):
    __version__ = "0.0.0"

__all__ = ["__version__"]

_LOG = logging.getLogger(__name__)


async def main():
    """Main entry point."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
    )

    _LOG.info("Starting Panasonic Viera TV Integration v%s", __version__)

    try:
        # Create driver
        driver = PanasonicVieraDriver()

        # Setup configuration
        config_path = get_config_path(driver.api.config_dir_path or "")
        _LOG.info("Using configuration path: %s", config_path)

        config_manager = BaseConfigManager(
            config_path,
            add_handler=driver.on_device_added,
            remove_handler=driver.on_device_removed,
            config_class=PanasonicVieraConfig,
        )
        driver.config_manager = config_manager

        # Create setup handler
        setup_handler = PanasonicVieraSetupFlow.create_handler(driver)

        # Initialize API (requires driver.json at project root!)
        driver_path = os.path.join(os.path.dirname(__file__), "..", "driver.json")
        await driver.api.init(os.path.abspath(driver_path), setup_handler)

        # Register configured devices
        await driver.register_all_configured_devices(connect=False)

        # Set initial state
        device_count = len(list(config_manager.all()))
        if device_count > 0:
            await driver.api.set_device_state(DeviceStates.CONNECTED)
        else:
            await driver.api.set_device_state(DeviceStates.DISCONNECTED)

        _LOG.info("Panasonic Viera TV integration started")

        # Keep running
        await asyncio.Future()

    except KeyboardInterrupt:
        _LOG.info("Integration stopped by user")
    except Exception as err:
        _LOG.critical("Fatal error: %s", err, exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
