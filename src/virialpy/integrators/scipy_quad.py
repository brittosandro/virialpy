"""SciPy adaptive quadrature integrator."""

from __future__ import annotations

from collections.abc import Callable

from scipy.integrate import quad

from virialpy.integrators.base import BaseIntegrator


class ScipyQuadIntegrator(BaseIntegrator):
    """Adaptive one-dimensional integrator based on ``scipy.integrate.quad``."""

    def __init__(self, epsabs: float = 1e-10, epsrel: float = 1e-10, limit: int = 500) -> None:
        """Create a SciPy quad integrator.

        Parameters
        ----------
        epsabs:
            Absolute error tolerance.
        epsrel:
            Relative error tolerance.
        limit:
            Upper bound on the number of subintervals used by QUADPACK.
        """
        self.epsabs = epsabs
        self.epsrel = epsrel
        self.limit = limit

    def integrate(
        self,
        function: Callable,
        lower: float,
        upper: float,
    ) -> tuple[float, float | None]:
        """Integrate a scalar callable with SciPy adaptive quadrature."""
        self._validate_bounds(lower, upper)
        value, error = quad(
            function,
            lower,
            upper,
            epsabs=self.epsabs,
            epsrel=self.epsrel,
            limit=self.limit,
        )
        return float(value), float(error)

