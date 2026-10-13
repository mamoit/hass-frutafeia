"""Sensor platform for the Frutafeia integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfMass
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_USERNAME, DOMAIN
from .coordinator import FrutafeiaCoordinator
from .frutafeia_api import BasketItem


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Frutafeia sensors."""
    coordinator: FrutafeiaCoordinator = entry.runtime_data
    data = coordinator.data
    prefix = f"frutafeia-{data.socio}-"
    email = entry.data[CONF_USERNAME]

    async_add_entities(
        [
            FrutafeiaSaldoSensor(coordinator, prefix, email),
            FrutafeiaDesperdicioSensor(coordinator, prefix, email),
            FrutafeiaSocioSensor(coordinator, prefix, email),
            FrutafeiaTamanhoSensor(coordinator, prefix, email),
            FrutafeiaEstadoSensor(coordinator, prefix, email),
            FrutafeiaDelegacaoSensor(coordinator, prefix, email),
            FrutafeiaNaoRecolhidaSensor(coordinator, prefix, email),
            FrutafeiaRecolhidaSensor(coordinator, prefix, email),
        ]
    )


class FrutafeiaSensor(CoordinatorEntity[FrutafeiaCoordinator], SensorEntity):
    """Base class for Frutafeia sensors."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: FrutafeiaCoordinator,
        prefix: str,
        email: str,
        key: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = f"{prefix}{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"socio-{coordinator.data.socio}")},
            name=email,
            manufacturer="Frutafeia",
            model="Account",
        )


class FrutafeiaSaldoSensor(FrutafeiaSensor):
    """Account balance sensor."""

    _attr_translation_key = "saldo"
    _attr_icon = "mdi:wallet"
    _attr_native_unit_of_measurement = "\u20ac"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(
        self, coordinator: FrutafeiaCoordinator, prefix: str, email: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, prefix, email, "saldo")

    @property
    def native_value(self) -> float:
        """Return the balance."""
        return self.coordinator.data.saldo


class FrutafeiaDesperdicioSensor(FrutafeiaSensor):
    """Waste avoided sensor."""

    _attr_translation_key = "desperdicio"
    _attr_icon = "mdi:recycle"
    _attr_native_unit_of_measurement = UnitOfMass.KILOGRAMS
    _attr_state_class = SensorStateClass.TOTAL

    def __init__(
        self, coordinator: FrutafeiaCoordinator, prefix: str, email: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, prefix, email, "desperdicio")

    @property
    def native_value(self) -> float:
        """Return the waste avoided in kg."""
        return self.coordinator.data.desperdicio


class FrutafeiaSocioSensor(FrutafeiaSensor):
    """Member number sensor."""

    _attr_translation_key = "socio"
    _attr_icon = "mdi:account"

    def __init__(
        self, coordinator: FrutafeiaCoordinator, prefix: str, email: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, prefix, email, "socio")

    @property
    def native_value(self) -> int:
        """Return the member number."""
        return self.coordinator.data.socio


class FrutafeiaTamanhoSensor(FrutafeiaSensor):
    """Basket size sensor."""

    _attr_translation_key = "tamanho"
    _attr_icon = "mdi:basket-plus"

    def __init__(
        self, coordinator: FrutafeiaCoordinator, prefix: str, email: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, prefix, email, "tamanho")

    @property
    def native_value(self) -> str:
        """Return the basket size."""
        return self.coordinator.data.tamanho


class FrutafeiaEstadoSensor(FrutafeiaSensor):
    """Account status sensor."""

    _attr_translation_key = "estado"
    _attr_icon = "mdi:sync"

    def __init__(
        self, coordinator: FrutafeiaCoordinator, prefix: str, email: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, prefix, email, "estado")

    @property
    def native_value(self) -> str:
        """Return the account status."""
        return self.coordinator.data.estado


class FrutafeiaDelegacaoSensor(FrutafeiaSensor):
    """Delegation sensor."""

    _attr_translation_key = "delegacao"
    _attr_icon = "mdi:warehouse"

    def __init__(
        self, coordinator: FrutafeiaCoordinator, prefix: str, email: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, prefix, email, "delegacao")

    @property
    def native_value(self) -> str:
        """Return the delegation."""
        return self.coordinator.data.delegacao


class FrutafeiaBasketSensor(FrutafeiaSensor):
    """Base class for basket sensors (count as state, items as attributes)."""

    _attr_state_class = SensorStateClass.TOTAL

    def __init__(
        self,
        coordinator: FrutafeiaCoordinator,
        prefix: str,
        email: str,
        key: str,
        translation_key: str,
    ) -> None:
        """Initialize the basket sensor."""
        super().__init__(coordinator, prefix, email, key)
        self._attr_translation_key = translation_key

    @property
    def _items(self) -> list[BasketItem]:
        """Return the basket items."""
        return getattr(self.coordinator.data, self._key)

    @property
    def native_value(self) -> int:
        """Return the number of items in the basket."""
        return len(self._items)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the basket items as attributes."""
        return {
            "items": [
                {"product": item.product, "producer": item.producer}
                for item in self._items
            ]
        }


class FrutafeiaNaoRecolhidaSensor(FrutafeiaBasketSensor):
    """Basket items not yet collected."""

    _attr_icon = "mdi:basket"

    def __init__(
        self, coordinator: FrutafeiaCoordinator, prefix: str, email: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(
            coordinator, prefix, email, "nao_recolhida", "nao_recolhida"
        )


class FrutafeiaRecolhidaSensor(FrutafeiaBasketSensor):
    """Basket items already collected."""

    _attr_icon = "mdi:basket-check"

    def __init__(
        self, coordinator: FrutafeiaCoordinator, prefix: str, email: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, prefix, email, "recolhida", "recolhida")
