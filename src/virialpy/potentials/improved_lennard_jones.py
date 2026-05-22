"""Improved Lennard-Jones intermolecular potential."""

from __future__ import annotations

from typing import Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray


def _as_float_or_array(values: NDArray[np.float64], scalar_input: bool) -> float | NDArray[np.float64]:
    """Return a Python float for scalar input, otherwise return a NumPy array."""
    if scalar_input:
        return float(values)
    return values


def improved_lennard_jones(
    r: float | Sequence[float] | ArrayLike,
    de: float,
    req: float,
    beta: float,
) -> float | NDArray[np.float64]:
    """Evaluate the Improved Lennard-Jones potential.

    The potential is defined by

    ``n(r) = beta + 4 (r / req)^2``

    and

    ``U(r) = de / (n(r) - 6) [6 (req / r)^n(r) - n(r) (req / r)^6]``.

    Parameters
    ----------
    r:
        Intermolecular distance. It may be a scalar, a Python sequence, or a
        NumPy array. Its unit must be the same unit used for ``req``.
    de:
        Dissociation energy or well depth. The returned energy has this same
        unit.
    req:
        Equilibrium distance. Its unit must be the same unit used for ``r``.
    beta:
        Dimensionless shape parameter controlling the distance-dependent
        exponent.

    Returns
    -------
    float or numpy.ndarray
        Potential energy evaluated at ``r``. Scalar input returns ``float``;
        array-like input returns ``numpy.ndarray``.
    """
    scalar_input = np.isscalar(r)
    distance = np.asarray(r, dtype=float)
    exponent = beta + 4.0 * (distance / req) ** 2
    reduced = req / distance
    energy = de / (exponent - 6.0) * (6.0 * reduced**exponent - exponent * reduced**6)
    return _as_float_or_array(energy, scalar_input)

