"""Constants for the Frutafeia integration."""

from __future__ import annotations

import aiohttp

DOMAIN = "frutafeia"
VERSION = "1.0.0"

BASE_URL = "https://frutafeia.pt"
LOGIN_URL = f"{BASE_URL}/user"

# Total timeout for all HTTP requests to Frutafeia.
TIMEOUT = aiohttp.ClientTimeout(total=30)

CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_SCAN_INTERVAL_HOURS = "scan_interval_hours"

DEFAULT_SCAN_INTERVAL_HOURS = 6

MIN_SCAN_INTERVAL_HOURS = 1
MAX_SCAN_INTERVAL_HOURS = 24
