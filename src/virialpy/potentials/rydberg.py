"""Rydberg intermolecular potential models."""

from __future__ import annotations

from typing import Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray


def _as_float_or_array(values: NDArray[np.float64], scalar_input: bool) -> float | NDArray[np.float64]:
    """Return a Python float for scalar input, otherwise return a NumPy array."""
    if scalar_input:
        return float(values)
    return values


def rydberg6(
    r: float | Sequence[float] | ArrayLike,
    de: float,
    re: float,
    c1: float,
    c2: float,
    c3: float,
    c4: float,
    c5: float,
    c6: float,
) -> float | NDArray[np.float64]:
    """Evaluate a sixth-degree Rydberg potential.

    The potential is

    ``U(r) = -de [1 + c1 x + c2 x^2 + c3 x^3 + c4 x^4 + c5 x^5 + c6 x^6] exp(-c1 x)``,

    where ``x = r - re``.

    Parameters
    ----------
    r:
        Intermolecular distance. It may be a scalar, a Python sequence, or a
        NumPy array. Its unit must be the same unit used for ``re``.
    de:
        Dissociation energy or well depth. The returned energy has this same
        unit.
    re:
        Equilibrium distance. Its unit must be the same unit used for ``r``.
    c1, c2, c3, c4, c5, c6:
        Polynomial and exponential coefficients. Their dimensions must be
        consistent with powers of ``r - re`` so the bracketed polynomial and
        exponential argument are dimensionless.

    Returns
    -------
    float or numpy.ndarray
        Potential energy evaluated at ``r``. Scalar input returns ``float``;
        array-like input returns ``numpy.ndarray``.
    """
    scalar_input = np.isscalar(r)
    distance = np.asarray(r, dtype=float)
    displacement = distance - re
    polynomial = (
        1.0
        + c1 * displacement
        + c2 * displacement**2
        + c3 * displacement**3
        + c4 * displacement**4
        + c5 * displacement**5
        + c6 * displacement**6
    )
    energy = -de * polynomial * np.exp(-c1 * displacement)
    return _as_float_or_array(energy, scalar_input)

