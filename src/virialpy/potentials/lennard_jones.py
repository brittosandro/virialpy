"""Lennard-Jones intermolecular potential."""

from __future__ import annotations

from typing import Sequence

import numpy as np
from numpy.typing import ArrayLike, NDArray


def _as_float_or_array(values: NDArray[np.float64], scalar_input: bool) -> float | NDArray[np.float64]:
    """Return a Python float for scalar input, otherwise return a NumPy array."""
    if scalar_input:
        return float(values)
    return values


def lennard_jones(
    r: float | Sequence[float] | ArrayLike,
    epsilon: float,
    sigma: float,
) -> float | NDArray[np.float64]:
    """Evaluate the Lennard-Jones 12-6 potential.

    The potential is

    ``U(r) = 4 epsilon [(sigma / r)^12 - (sigma / r)^6]``.

    Parameters
    ----------
    r:
        Intermolecular distance. It may be a scalar, a Python sequence, or a
        NumPy array. Its unit must be the same unit used for ``sigma``.
    epsilon:
        Potential well depth. The returned energy has this same unit.
    sigma:
        Distance at which the potential crosses zero. Its unit must be the
        same unit used for ``r``.

    Returns
    -------
    float or numpy.ndarray
        Potential energy evaluated at ``r``. Scalar input returns ``float``;
        array-like input returns ``numpy.ndarray``.
    """
    scalar_input = np.isscalar(r)
    distance = np.asarray(r, dtype=float)
    reduced = sigma / distance
    reduced_6 = reduced**6
    energy = 4.0 * epsilon * (reduced_6**2 - reduced_6)
    return _as_float_or_array(energy, scalar_input)

