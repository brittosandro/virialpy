"""Second virial coefficient calculations."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from virialpy.constants import AVOGADRO_CONSTANT
from virialpy.virial.mayer import mayer_integrand

_DISTANCE_TO_CM3 = {
    "angstrom": 1e-24,
    "pm": 1e-30,
    "meter": 1e6,
}


def _validate_inputs(temperature: float, r_min: float, r_max: float, distance_unit: str) -> None:
    """Validate physical and unit inputs for the virial calculation."""
    if temperature <= 0:
        raise ValueError("temperature must be positive.")
    if r_max <= r_min:
        raise ValueError("r_max must be greater than r_min.")
    if distance_unit not in _DISTANCE_TO_CM3:
        supported = ", ".join(sorted(_DISTANCE_TO_CM3))
        raise ValueError(f"Unsupported distance_unit '{distance_unit}'. Supported units: {supported}")


def second_virial_coefficient(
    temperature: float,
    potential_func: Callable,
    parameters: dict[str, float],
    integrator,
    r_min: float,
    r_max: float,
    distance_unit: str = "angstrom",
    energy_unit: str = "kelvin",
) -> tuple[float, float | None]:
    """Calculate the second virial coefficient ``B(T)`` in cm^3/mol.

    The potential is assumed to return reduced energy in Kelvin, ``U / k_B``.
    Distances are integrated in the unit specified by ``distance_unit`` and
    converted to cm^3/mol after integration.

    Parameters
    ----------
    temperature:
        Absolute temperature in Kelvin.
    potential_func:
        Potential callable invoked as ``potential_func(r, **parameters)``.
    parameters:
        Potential parameters.
    integrator:
        Object with an ``integrate(function, lower, upper)`` method returning
        ``(value, error)``.
    r_min, r_max:
        Integration bounds in ``distance_unit``.
    distance_unit:
        Distance unit for the integration coordinate. Supported values are
        ``"angstrom"``, ``"pm"``, and ``"meter"``.
    energy_unit:
        Energy unit returned by ``potential_func``. Supported values are
        ``"kelvin"``, ``"kcal/mol"``, ``"kj/mol"``, ``"ev"``, and ``"mev"``.

    Returns
    -------
    tuple[float, float | None]
        ``B(T)`` in cm^3/mol and the propagated integration error when
        available.
    """
    _validate_inputs(temperature, r_min, r_max, distance_unit)

    def integrand(r):
        return mayer_integrand(r, temperature, potential_func, parameters, energy_unit=energy_unit)

    integral, integration_error = integrator.integrate(integrand, r_min, r_max)
    scale = 2.0 * np.pi * AVOGADRO_CONSTANT * _DISTANCE_TO_CM3[distance_unit]
    b2_value = scale * integral
    b2_error = None if integration_error is None else scale * integration_error
    return float(b2_value), None if b2_error is None else float(b2_error)
