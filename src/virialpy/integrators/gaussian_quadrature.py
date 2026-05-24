"""Gauss-Legendre quadrature integrator."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from numpy.polynomial.legendre import leggauss

from virialpy.integrators.base import BaseIntegrator


class GaussianQuadratureIntegrator(BaseIntegrator):
    """Fixed-order Gauss-Legendre quadrature on a finite interval."""

    def __init__(self, n_points: int = 64) -> None:
        """Create a Gauss-Legendre integrator.

        Parameters
        ----------
        n_points:
            Number of quadrature nodes.
        """
        if n_points < 1:
            raise ValueError("n_points must be at least 1.")
        self.n_points = n_points

    def integrate(
        self,
        function: Callable,
        lower: float,
        upper: float,
    ) -> tuple[float, float | None]:
        """Integrate a callable using Gauss-Legendre quadrature."""
        self._validate_bounds(lower, upper)
        nodes, weights = leggauss(self.n_points)
        midpoint = 0.5 * (upper + lower)
        half_width = 0.5 * (upper - lower)
        x = midpoint + half_width * nodes
        y = np.asarray(function(x), dtype=float)
        value = half_width * np.sum(weights * y)
        return float(value), None

