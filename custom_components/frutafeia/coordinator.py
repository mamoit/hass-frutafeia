"""Data update coordinator for the Frutafeia integration."""

from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_SCAN_INTERVAL_HOURS,
    DEFAULT_SCAN_INTERVAL_HOURS,
    DOMAIN,
    MIN_SCAN_INTERVAL_HOURS,
)
from .frutafeia_api import FrutafeiaAuthError, FrutafeiaClient, FrutafeiaData, FrutafeiaError

_LOGGER = logging.getLogger(__name__)


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
        hours = max(
            int(
                entry.options.get(
                    CONF_SCAN_INTERVAL_HOURS,
                    entry.data.get(
                        CONF_SCAN_INTERVAL_HOURS, DEFAULT_SCAN_INTERVAL_HOURS
                    ),
                )
            ),
            MIN_SCAN_INTERVAL_HOURS,
        )
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=timedelta(hours=hours),
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
