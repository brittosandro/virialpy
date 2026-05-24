"""Base abstractions for numerical integrators."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable


class BaseIntegrator(ABC):
    """Abstract base class for one-dimensional numerical integrators."""

    @abstractmethod
    def integrate(
        self,
        function: Callable,
        lower: float,
        upper: float,
    ) -> tuple[float, float | None]:
        """Integrate ``function`` over the interval ``[lower, upper]``.

        Parameters
        ----------
        function:
            Callable to integrate.
        lower:
            Lower integration limit.
        upper:
            Upper integration limit.

        Returns
        -------
        tuple[float, float | None]
            Integral value and an error estimate, or ``None`` when the method
            does not provide one.
        """

    @staticmethod
    def _validate_bounds(lower: float, upper: float) -> None:
        """Raise a clear error when integration bounds are invalid."""
        if upper <= lower:
            raise ValueError("Integration upper bound must be greater than lower bound.")

