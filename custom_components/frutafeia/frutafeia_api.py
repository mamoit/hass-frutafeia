"""Asynchronous client for the Frutafeia.pt website."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import aiohttp
from bs4 import BeautifulSoup

from .const import LOGIN_URL


class FrutafeiaError(Exception):
    """Base exception for the Frutafeia client."""


class FrutafeiaAuthError(FrutafeiaError):
    """Exception raised when authentication fails."""


@dataclass
class BasketItem:
    """A single product in a basket."""

    product: str
    producer: str


@dataclass
class FrutafeiaData:
    """Data returned from the Frutafeia dashboard."""

    saldo: float
    socio: int
    tamanho: str
    estado: str
    delegacao: str
    nao_recolhida: list[BasketItem] = field(default_factory=list)
    recolhida: list[BasketItem] = field(default_factory=list)


class FrutafeiaClient:
    """Client that logs into Frutafeia and scrapes the dashboard."""

    def __init__(self, username: str, password: str, session: aiohttp.ClientSession) -> None:
        """Initialize the client."""
        self._username = username
        self._password = password
        self._session = session

    async def async_get_data(self) -> FrutafeiaData:
        """Log in and return the dashboard data."""
        captcha = await self._get_captcha()
        return await self._login(captcha)

    async def _get_captcha(self) -> dict[str, str]:
        """Fetch the login page and extract the captcha form values."""
        try:
            async with self._session.get(LOGIN_URL) as resp:
                resp.raise_for_status()
                html = await resp.text()
        except aiohttp.ClientError as err:
            raise FrutafeiaError(f"Unable to reach Frutafeia: {err}") from err

        soup = BeautifulSoup(html, "html.parser")
        values: dict[str, str] = {}
        for name in ("captcha_sid", "captcha_token", "form_build_id"):
            element = soup.find("input", {"name": name})
            if element is None or element.get("value") is None:
                raise FrutafeiaError(f"Login form field '{name}' not found")
            values[name] = element["value"]
        return values

    async def _login(self, captcha: dict[str, str]) -> FrutafeiaData:
        """Submit the login form and parse the resulting dashboard."""
        try:
            async with self._session.post(
                LOGIN_URL,
                data={
                    "name": self._username,
                    "pass": self._password,
                    "form_id": "user_login",
                    "form_build_id": captcha["form_build_id"],
                    "captcha_sid": captcha["captcha_sid"],
                    "captcha_token": captcha["captcha_token"],
                    "captcha_response": "",
                    "op": "Entrar",
                },
            ) as resp:
                resp.raise_for_status()
                html = await resp.text()
        except aiohttp.ClientError as err:
            raise FrutafeiaError(f"Unable to reach Frutafeia: {err}") from err

        soup = BeautifulSoup(html, "html.parser")

        # If the authenticated dashboard is not present, the credentials were
        # rejected and the login form is shown again.
        if (
            soup.select_one(".saldo") is None
            or soup.select_one(".estado-cons .val") is None
            or soup.select_one(".numero-socio .val") is None
        ):
            raise FrutafeiaAuthError("Invalid username or password")

        return FrutafeiaData(
            saldo=self._parse_saldo(soup),
            socio=self._parse_socio(soup),
            tamanho=self._parse_value(soup, ".cesta .val"),
            estado=self._parse_value(soup, ".estado-cons .val"),
            delegacao=self._parse_value(soup, ".delelegacao-cons .val"),
            nao_recolhida=self._parse_basket(soup, ".nao-recolhida .views-row"),
            recolhida=self._parse_basket(soup, ".recolhida .views-row"),
        )

    @staticmethod
    def _parse_value(soup: BeautifulSoup, selector: str) -> str:
        """Return the stripped text of the first element matching a selector."""
        element = soup.select_one(selector)
        if element is None:
            raise FrutafeiaError(f"Dashboard field not found: {selector}")
        return element.text.strip()

    @staticmethod
    def _parse_saldo(soup: BeautifulSoup) -> float:
        """Return the account balance as a float."""
        element = soup.select_one(".pane-consumidor-panel .row .val")
        if element is None:
            raise FrutafeiaError("Saldo field not found")
        return float(element.text.strip().replace("\u20ac", "").replace(",", "."))

    @staticmethod
    def _parse_socio(soup: BeautifulSoup) -> int:
        """Return the member number as an int."""
        element = soup.select_one(".numero-socio .val")
        if element is None:
            raise FrutafeiaError("Socio field not found")
        return int(element.text.strip())

    @staticmethod
    def _parse_basket(soup: BeautifulSoup, selector: str) -> list[BasketItem]:
        """Return the list of products in a basket."""
        items: list[BasketItem] = []
        for row in soup.select(selector):
            product = row.select_one(".views-field-field-ref-producto")
            producer = row.select_one(".views-field-field-produtor")
            if product is None or producer is None:
                continue
            items.append(
                BasketItem(
                    product=product.text.strip(),
                    producer=producer.text.strip(),
                )
            )
        return items

    def to_dict(self, data: FrutafeiaData) -> dict[str, Any]:
        """Serialize dashboard data to a plain dictionary."""
        return {
            "saldo": data.saldo,
            "socio": data.socio,
            "tamanho": data.tamanho,
            "estado": data.estado,
            "delegacao": data.delegacao,
            "nao_recolhida": [
                {"product": item.product, "producer": item.producer}
                for item in data.nao_recolhida
            ],
            "recolhida": [
                {"product": item.product, "producer": item.producer}
                for item in data.recolhida
            ],
        }
