"""Mayer functions and integrands for virial coefficient calculations."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from numpy.typing import ArrayLike, NDArray


def _validate_temperature(temperature: float) -> None:
    """Raise a clear error when temperature is not physically valid."""
    if temperature <= 0:
        raise ValueError("temperature must be positive.")


def mayer_function(
    energy: float | ArrayLike,
    temperature: float,
) -> float | NDArray[np.float64]:
    """Evaluate the Mayer function ``f = exp[-U/T] - 1``.

    Parameters
    ----------
    energy:
        Potential energy ``U`` in reduced temperature units, such as Kelvin
        for ``U / k_B``. Scalars and NumPy-compatible arrays are accepted.
    temperature:
        Absolute temperature in Kelvin. It must use the same reduced energy
        convention as ``energy``.

    Returns
    -------
    float or numpy.ndarray
        Mayer function evaluated at ``energy``. Scalar input returns ``float``;
        array-like input returns ``numpy.ndarray``.
    """
    _validate_temperature(temperature)
    scalar_input = np.isscalar(energy)
    energy_array = np.asarray(energy, dtype=float)
    values = np.exp(-energy_array / temperature) - 1.0
    if scalar_input:
        return float(values)
    return values


def mayer_integrand(
    r: float | ArrayLike,
    temperature: float,
    potential_func: Callable,
    parameters: dict[str, float],
) -> float | NDArray[np.float64]:
    """Evaluate the radial Mayer integrand for the second virial coefficient.

    The returned quantity is

    ``[1 - exp(-U(r) / T)] r^2``,

    which is compatible with

    ``B(T) = 2 pi N_A integral [1 - exp(-U(r) / T)] r^2 dr``.
    """
    _validate_temperature(temperature)
    scalar_input = np.isscalar(r)
    distance = np.asarray(r, dtype=float)
    energy = np.asarray(potential_func(distance, **parameters), dtype=float)
    values = (1.0 - np.exp(-energy / temperature)) * distance**2
    if scalar_input:
        return float(values)
    return values

