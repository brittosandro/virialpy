"""Composite Simpson integration."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
from scipy.integrate import simpson

from virialpy.integrators.base import BaseIntegrator


class SimpsonIntegrator(BaseIntegrator):
    """Composite Simpson integrator on a uniform linear mesh."""

    def __init__(self, n_points: int = 10001) -> None:
        """Create a Simpson integrator.

        Parameters
        ----------
        n_points:
            Number of mesh points. An odd default is used to favor Simpson's
            rule on uniformly spaced samples.
        """
        if n_points < 3:
            raise ValueError("n_points must be at least 3.")
        self.n_points = n_points

    def integrate(
        self,
        function: Callable,
        lower: float,
        upper: float,
    ) -> tuple[float, float | None]:
        """Integrate a callable using composite Simpson integration."""
        self._validate_bounds(lower, upper)
        x = np.linspace(lower, upper, self.n_points)
        y = np.asarray(function(x), dtype=float)
        value = simpson(y, x=x)
        return float(value), None

