"""Composite trapezoidal integration."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from virialpy.integrators.base import BaseIntegrator


class TrapezoidIntegrator(BaseIntegrator):
    """Composite trapezoid integrator on a uniform linear mesh."""

    def __init__(self, n_points: int = 10000) -> None:
        """Create a trapezoid integrator.

        Parameters
        ----------
        n_points:
            Number of mesh points.
        """
        if n_points < 2:
            raise ValueError("n_points must be at least 2.")
        self.n_points = n_points

    def integrate(
        self,
        function: Callable,
        lower: float,
        upper: float,
    ) -> tuple[float, float | None]:
        """Integrate a callable using composite trapezoidal integration."""
        self._validate_bounds(lower, upper)
        x = np.linspace(lower, upper, self.n_points)
        y = np.asarray(function(x), dtype=float)
        value = np.trapezoid(y, x=x)
        return float(value), None

