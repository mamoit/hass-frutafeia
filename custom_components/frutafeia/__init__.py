"""The Frutafeia integration for Home Assistant."""

from __future__ import annotations

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_PASSWORD, CONF_USERNAME, DOMAIN, TIMEOUT
from .coordinator import FrutafeiaCoordinator
from .frutafeia_api import FrutafeiaClient

PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Frutafeia from a config entry."""
    session = aiohttp.ClientSession(timeout=TIMEOUT)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = session

    client = FrutafeiaClient(
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
        session,
    )
    coordinator = FrutafeiaCoordinator(hass, entry, client)

    await coordinator.async_config_entry_first_refresh()

    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        session = hass.data[DOMAIN].pop(entry.entry_id)
        await session.close()

    return unload_ok
