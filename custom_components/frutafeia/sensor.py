"""Sensor platform for the Frutafeia integration."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

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

    async_add_entities(
        [
            FrutafeiaSaldoSensor(coordinator, prefix),
            FrutafeiaSocioSensor(coordinator, prefix),
            FrutafeiaTamanhoSensor(coordinator, prefix),
            FrutafeiaEstadoSensor(coordinator, prefix),
            FrutafeiaDelegacaoSensor(coordinator, prefix),
            FrutafeiaNaoRecolhidaSensor(coordinator, prefix),
            FrutafeiaRecolhidaSensor(coordinator, prefix),
        ]
    )


class FrutafeiaSensor(CoordinatorEntity[FrutafeiaCoordinator], SensorEntity):
    """Base class for Frutafeia sensors."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: FrutafeiaCoordinator, prefix: str, key: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = f"{prefix}{key}"


class FrutafeiaSaldoSensor(FrutafeiaSensor):
    """Account balance sensor."""

    _attr_name = "Saldo"
    _attr_native_unit_of_measurement = "\u20ac"
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator: FrutafeiaCoordinator, prefix: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, prefix, "saldo")

    @property
    def native_value(self) -> float:
        """Return the balance."""
        return self.coordinator.data.saldo


class FrutafeiaSocioSensor(FrutafeiaSensor):
    """Member number sensor."""

    _attr_name = "N\u00famero de s\u00f3cio"

    def __init__(self, coordinator: FrutafeiaCoordinator, prefix: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, prefix, "socio")

    @property
    def native_value(self) -> int:
        """Return the member number."""
        return self.coordinator.data.socio


class FrutafeiaTamanhoSensor(FrutafeiaSensor):
    """Basket size sensor."""

    _attr_name = "Tamanho"

    def __init__(self, coordinator: FrutafeiaCoordinator, prefix: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, prefix, "tamanho")

    @property
    def native_value(self) -> str:
        """Return the basket size."""
        return self.coordinator.data.tamanho


class FrutafeiaEstadoSensor(FrutafeiaSensor):
    """Account status sensor."""

    _attr_name = "Estado"

    def __init__(self, coordinator: FrutafeiaCoordinator, prefix: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, prefix, "estado")

    @property
    def native_value(self) -> str:
        """Return the account status."""
        return self.coordinator.data.estado


class FrutafeiaDelegacaoSensor(FrutafeiaSensor):
    """Delegation sensor."""

    _attr_name = "Delega\u00e7\u00e3o"

    def __init__(self, coordinator: FrutafeiaCoordinator, prefix: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, prefix, "delegacao")

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
        key: str,
        name: str,
    ) -> None:
        """Initialize the basket sensor."""
        super().__init__(coordinator, prefix, key)
        self._attr_name = name

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

    def __init__(self, coordinator: FrutafeiaCoordinator, prefix: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, prefix, "nao_recolhida", "Cesta n\u00e3o recolhida")


class FrutafeiaRecolhidaSensor(FrutafeiaBasketSensor):
    """Basket items already collected."""

    def __init__(self, coordinator: FrutafeiaCoordinator, prefix: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, prefix, "recolhida", "Cesta recolhida")
