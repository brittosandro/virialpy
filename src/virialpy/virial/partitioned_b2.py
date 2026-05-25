"""Partitioned second virial coefficient calculations."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from numpy.typing import ArrayLike, NDArray

from virialpy.constants import AVOGADRO_CONSTANT
from virialpy.units import energy_to_kelvin
from virialpy.virial.mayer import mayer_integrand

_DISTANCE_TO_CM3 = {
    "angstrom": 1e-24,
    "pm": 1e-30,
    "meter": 1e6,
}


def _validate_partition_inputs(
    temperature: float,
    r1: float,
    r2: float,
    r3: float,
    r4: float,
    distance_unit: str,
    energy_unit: str,
) -> None:
    """Validate temperature, partition limits, and unit options."""
    if temperature <= 0:
        raise ValueError("temperature must be positive.")
    if not (0.0 < r1 < r2 < r3 < r4):
        raise ValueError("Partition limits must satisfy 0 < r1 < r2 < r3 < r4.")
    if distance_unit not in _DISTANCE_TO_CM3:
        supported = ", ".join(sorted(_DISTANCE_TO_CM3))
        raise ValueError(f"Unsupported distance_unit '{distance_unit}'. Supported units: {supported}")
    energy_to_kelvin(0.0, energy_unit)


def tail_integrand_approximation(
    r: float | ArrayLike,
    temperature: float,
    potential_func: Callable,
    parameters: dict[str, float],
    energy_unit: str = "kelvin",
) -> float | NDArray[np.float64]:
    """Evaluate the long-range tail approximation ``(U_K(r) / T) r^2``."""
    if temperature <= 0:
        raise ValueError("temperature must be positive.")

    scalar_input = np.isscalar(r)
    distance = np.asarray(r, dtype=float)
    energy = np.asarray(potential_func(distance, **parameters), dtype=float)
    energy_kelvin = energy_to_kelvin(energy, energy_unit)
    values = (energy_kelvin / temperature) * distance**2
    if scalar_input:
        return float(values)
    return values


def partitioned_second_virial_coefficient(
    temperature: float,
    potential_func: Callable,
    parameters: dict[str, float],
    integrator_b2,
    integrator_b3,
    integrator_b4,
    r1: float,
    r2: float,
    r3: float,
    r4: float,
    distance_unit: str = "angstrom",
    energy_unit: str = "kelvin",
) -> dict[str, float | str | None]:
    """Calculate a partitioned second virial coefficient in cm^3/mol.

    The total coefficient is decomposed as ``B = B1 + B2 + B3 + B4``. ``B1``
    is the analytic hard-core contribution, ``B2`` and ``B3`` use the full
    Mayer integrand, and ``B4`` uses the long-range approximation ``U/T``.
    """
    _validate_partition_inputs(temperature, r1, r2, r3, r4, distance_unit, energy_unit)

    scale = 2.0 * np.pi * AVOGADRO_CONSTANT * _DISTANCE_TO_CM3[distance_unit]
    b1 = scale * r1**3 / 3.0

    def full_integrand(r):
        return mayer_integrand(
            r,
            temperature,
            potential_func,
            parameters,
            energy_unit=energy_unit,
        )

    def tail_integrand(r):
        return tail_integrand_approximation(
            r,
            temperature,
            potential_func,
            parameters,
            energy_unit=energy_unit,
        )

    integral_b2, error_b2 = integrator_b2.integrate(full_integrand, r1, r2)
    integral_b3, error_b3 = integrator_b3.integrate(full_integrand, r2, r3)
    integral_b4, error_b4 = integrator_b4.integrate(tail_integrand, r3, r4)

    b2 = scale * integral_b2
    b3 = scale * integral_b3
    b4 = scale * integral_b4

    return {
        "temperature": float(temperature),
        "b1": float(b1),
        "b2": float(b2),
        "b3": float(b3),
        "b4": float(b4),
        "b_total": float(b1 + b2 + b3 + b4),
        "error_b2": None if error_b2 is None else float(scale * error_b2),
        "error_b3": None if error_b3 is None else float(scale * error_b3),
        "error_b4": None if error_b4 is None else float(scale * error_b4),
        "r1": r1,
        "r2": r2,
        "r3": r3,
        "r4": r4,
        "distance_unit": distance_unit,
        "energy_unit": energy_unit,
    }

