"""Unit conventions and conversion helpers.

This module will centralize conversions for distance, energy, temperature,
and virial-coefficient units before values enter scientific calculations.
"""

from __future__ import annotations

from typing import Any

R_KCAL_MOL_K = 0.00198720425864083
R_KJ_MOL_K = 0.00831446261815324
EV_TO_KELVIN = 11604.51812
MEV_TO_KELVIN = 11.60451812


def kcal_per_mol_to_kelvin(value: Any) -> Any:
    """Convert energy from kcal/mol to Kelvin via ``U / R``."""
    return value / R_KCAL_MOL_K


def kj_per_mol_to_kelvin(value: Any) -> Any:
    """Convert energy from kJ/mol to Kelvin via ``U / R``."""
    return value / R_KJ_MOL_K


def ev_to_kelvin(value: Any) -> Any:
    """Convert energy from eV per particle to Kelvin."""
    return value * EV_TO_KELVIN


def mev_to_kelvin(value: Any) -> Any:
    """Convert energy from meV per particle to Kelvin."""
    return value * MEV_TO_KELVIN


def kelvin_to_kelvin(value: Any) -> Any:
    """Return energy already expressed in Kelvin."""
    return value


ENERGY_TO_KELVIN_CONVERTERS = {
    "kelvin": kelvin_to_kelvin,
    "kcal/mol": kcal_per_mol_to_kelvin,
    "kj/mol": kj_per_mol_to_kelvin,
    "ev": ev_to_kelvin,
    "mev": mev_to_kelvin,
}


def energy_to_kelvin(value: Any, energy_unit: str) -> Any:
    """Convert an energy value or array from a supported unit to Kelvin."""
    try:
        converter = ENERGY_TO_KELVIN_CONVERTERS[energy_unit]
    except KeyError as exc:
        supported = ", ".join(sorted(ENERGY_TO_KELVIN_CONVERTERS))
        raise ValueError(f"Unsupported energy_unit '{energy_unit}'. Supported units: {supported}") from exc
    return converter(value)

