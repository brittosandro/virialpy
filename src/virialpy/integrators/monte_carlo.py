"""Monte Carlo numerical integration."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np

from virialpy.integrators.base import BaseIntegrator


class MonteCarloIntegrator(BaseIntegrator):
    """Monte Carlo integrator for finite one-dimensional intervals."""

    def __init__(self, n_samples: int = 100000, random_state: int | None = None) -> None:
        """Create a Monte Carlo integrator.

        Parameters
        ----------
        n_samples:
            Number of uniformly sampled points.
        random_state:
            Optional seed for reproducible sampling.
        """
        if n_samples <= 0:
            raise ValueError("n_samples must be positive.")
        self.n_samples = n_samples
        self.random_state = random_state

    def _evaluate_function(self, function: Callable, points: np.ndarray) -> np.ndarray:
        """Evaluate a vectorized function or fall back to pointwise calls."""
        try:
            values = np.asarray(function(points), dtype=float)
            if values.shape == ():
                values = np.full(points.shape, float(values))
            if values.shape != points.shape:
                raise ValueError
            return values
        except Exception:
            return np.asarray([function(float(point)) for point in points], dtype=float)

    def integrate(
        self,
        function: Callable,
        lower: float,
        upper: float,
    ) -> tuple[float, float | None]:
        """Estimate an integral using uniform Monte Carlo sampling."""
        self._validate_bounds(lower, upper)
        rng = np.random.default_rng(self.random_state)
        points = rng.uniform(lower, upper, size=self.n_samples)
        values = self._evaluate_function(function, points)

        width = upper - lower
        integral = width * np.mean(values)
        if self.n_samples == 1:
            error = 0.0
        else:
            error = width * np.std(values, ddof=1) / np.sqrt(self.n_samples)
        return float(integral), float(error)

