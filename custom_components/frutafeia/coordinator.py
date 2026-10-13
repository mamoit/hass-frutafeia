"""Data update coordinator for the Frutafeia integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .frutafeia_api import FrutafeiaAuthError, FrutafeiaClient, FrutafeiaData, FrutafeiaError

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=15)


class FrutafeiaCoordinator(DataUpdateCoordinator[FrutafeiaData]):
    """Coordinator that polls the Frutafeia dashboard."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
        client: FrutafeiaClient,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=SCAN_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> FrutafeiaData:
        """Fetch the latest dashboard data from Frutafeia."""
        try:
            return await self.client.async_get_data()
        except FrutafeiaAuthError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except FrutafeiaError as err:
            raise UpdateFailed(f"Error communicating with Frutafeia: {err}") from err
